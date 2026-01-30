# src/vata/evaluator.py – Metrics for VATA AI code detection eval
import numpy as np
from typing import List, Tuple

class VataEvaluator:
    def __init__(self, true_labels: List[int], pred_labels: List[int]):
        """
        true_labels: List of ground truth (0=Human, 1=AI)
        pred_labels: List of VATA predictions (0=Human, 1=AI)
        """
        self.true = np.array(true_labels)
        self.pred = np.array(pred_labels)
        self.validate_inputs()

    def validate_inputs(self):
        if len(self.true) != len(self.pred):
            raise ValueError("True and predicted labels must be same length")
        if not set(self.true).issubset({0, 1}) or not set(self.pred).issubset({0, 1}):
            raise ValueError("Labels must be binary (0 or 1)")

    def confusion_matrix(self) -> Tuple[int, int, int, int]:
        """Returns (TP, TN, FP, FN)"""
        tp = np.sum((self.true == 1) & (self.pred == 1))
        tn = np.sum((self.true == 0) & (self.pred == 0))
        fp = np.sum((self.true == 0) & (self.pred == 1))
        fn = np.sum((self.true == 1) & (self.pred == 0))
        return tp, tn, fp, fn

    def accuracy(self) -> float:
        tp, tn, fp, fn = self.confusion_matrix()
        return (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0.0

    def precision(self) -> float:
        tp, _, fp, _ = self.confusion_matrix()
        return tp / (tp + fp) if (tp + fp) > 0 else 0.0

    def recall(self) -> float:
        tp, _, _, fn = self.confusion_matrix()
        return tp / (tp + fn) if (tp + fn) > 0 else 0.0

    def f1_score(self) -> float:
        prec = self.precision()
        rec = self.recall()
        return 2 * (prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

    def print_report(self):
        tp, tn, fp, fn = self.confusion_matrix()
        print("Confusion Matrix:")
        print(f"  TP: {tp}  FP: {fp}")
        print(f"  FN: {fn}  TN: {tn}")
        print(f"Accuracy: {self.accuracy():.4f}")
        print(f"Precision: {self.precision():.4f}")
        print(f"Recall: {self.recall():.4f}")
        print(f"F1 Score: {self.f1_score():.4f}")

# Usage example (add to your test scripts)
if __name__ == "__main__":
    # Dummy data: true (ground truth), pred (VATA output)
    true_labels = [0, 1, 0, 1, 0, 1]  # e.g., [Human, AI, Human, AI, Human, AI]
    pred_labels = [0, 1, 1, 1, 0, 0]  # VATA guesses
    evaluator = VataEvaluator(true_labels, pred_labels)
    evaluator.print_report()
    # Output example:
    # Confusion Matrix:
    #   TP: 2  FP: 1
    #   FN: 1  TN: 2
    # Accuracy: 0.6667
    # Precision: 0.6667
    # Recall: 0.6667
    # F1 Score: 0.6667
