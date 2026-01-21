# ai_code_detector/train.py
import os
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    DataCollatorWithPadding,
)
import evaluate
import numpy as np

MODEL_NAME = "microsoft/codebert-base"          # or "Salesforce/codet5p-220m" etc.
DATASET_PATH = "path/to/your/dataset"           # e.g. "json" directory or HF hub
OUTPUT_DIR = "./models/ai_code_detector_v1"
NUM_LABELS = 2

def compute_metrics(eval_pred):
    accuracy = evaluate.load("accuracy")
    f1 = evaluate.load("f1")
    predictions, labels = eval_pred
    preds = np.argmax(predictions, axis=1)
    return {
        "accuracy": accuracy.compute(predictions=preds, references=labels)["accuracy"],
        "f1": f1.compute(predictions=preds, references=labels, average="binary")["f1"],
    }

def main():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    # Load your dataset (adjust split/format as needed)
    dataset = load_dataset("json", data_files={"train": "train.jsonl", "validation": "val.jsonl"})

    def preprocess(examples):
        return tokenizer(examples["text"], truncation=True, max_length=512)

    tokenized_dataset = dataset.map(preprocess, batched=True)
    tokenized_dataset = tokenized_dataset.rename_column("label", "labels")
    tokenized_dataset.set_format("torch", columns=["input_ids", "attention_mask", "labels"])

    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=NUM_LABELS)

    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=3,                # tune based on your data size
        per_device_train_batch_size=8,
        per_device_eval_batch_size=16,
        gradient_accumulation_steps=4,
        learning_rate=2e-5,
        weight_decay=0.01,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        fp16=True,                         # if GPU supports
        report_to="none",                  # or "wandb"/"tensorboard"
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
        eval_dataset=tokenized_dataset["validation"],
        data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
        compute_metrics=compute_metrics,
    )

    trainer.train()
    trainer.save_model(os.path.join(OUTPUT_DIR, "best"))
    tokenizer.save_pretrained(os.path.join(OUTPUT_DIR, "best"))

    print(f"Model saved to {OUTPUT_DIR}/best")


if __name__ == "__main__":
    main()