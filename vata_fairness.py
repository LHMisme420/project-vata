from sklearn.metrics import confusion_matrix
import numpy as np

def prove_fairness(y_true, y_pred, sensitive_groups):
    # Demographic parity check — ZK circuit coming soon
    rates = {}
    for group in sensitive_groups:
        mask = sensitive_groups[group]
        rates[group] = np.mean(y_pred[mask])
    
    disparity = max(rates.values()) - min(rates.values())
    return disparity < 0.1, rates, disparity