# metrics_runner.py
# This script evaluates trained ML models for each ethical mode by:
# 1. Loading the labeled dataset for that mode
# 2. Splitting into training and testing sets (stratified)
# 3. Loading the corresponding trained model
# 4. Predicting actions and probabilities on the test set
# 5. Calculating key performance metrics:
#    - Accuracy
#    - Precision (macro)
#    - Recall (macro)
#    - Specificity (macro)
#    - F1 Score (macro)
#    - AUC-ROC (macro-average, one-vs-rest for multiclass)
# 6. Printing results for each mode and saving a summary CSV in 'visualizations/'

import os
import pandas as pd               # For dataset handling and saving results
import numpy as np                # For numerical operations and array handling
import joblib                     # For loading trained models
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score
)
from sklearn.preprocessing import label_binarize

# Features used in both training and evaluation
FEATURES = ["left_risk", "right_risk", "speed_kph", "name", "child_present"]

# Ethical modes corresponding to separate datasets and models
MODES = ["utilitarian", "deontological", "virtue"]

# List to store evaluation results for all modes
results = []

# Loop over each ethical mode
for mode in MODES:
    print(f"\n=== {mode.capitalize()} Mode ===")

    # --- Load dataset for the current mode ---
    df = pd.read_csv(f"labeled_data/{mode}_labeled.csv")
    X = df[FEATURES]                  # Feature columns
    y = df["action"].astype(str)      # Actions converted to string

    # --- Split into train/test sets (stratified by class) ---
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=7, stratify=y
    )

    # --- Load the trained model for the current mode ---
    model = joblib.load(f"models/{mode}.pkl")

    # --- Generate predictions and predicted probabilities ---
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)

    # --- Calculate standard metrics ---
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average="macro", zero_division=0)
    rec = recall_score(y_test, y_pred, average="macro", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)

    # --- Calculate specificity (macro-average) ---
    labels = np.unique(y_test)
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    specifics = []
    for k in range(len(labels)):
        TP = cm[k, k]
        FP = cm[:, k].sum() - TP
        FN = cm[k, :].sum() - TP
        TN = cm.sum() - (TP + FP + FN)
        spec_k = TN / (TN + FP) if (TN + FP) > 0 else 0.0
        specifics.append(spec_k)
    specificity_macro = np.mean(specifics)

    # --- Calculate AUC-ROC (handle binary vs multiclass) ---
    if len(labels) == 2:
        pos_label = labels[1]
        y_true_bin = (y_test == pos_label).astype(int)
        pos_index = list(model.classes_).index(pos_label)
        auc_macro = roc_auc_score(y_true_bin, y_proba[:, pos_index])
    else:
        y_bin = label_binarize(y_test, classes=labels)
        auc_macro = roc_auc_score(y_bin, y_proba, average="macro", multi_class="ovr")

    # --- Print metrics for this mode ---
    print(f"Accuracy:           {acc:.3f}")
    print(f"Precision (macro):  {prec:.3f}")
    print(f"Recall (macro):     {rec:.3f}")
    print(f"Specificity (macro):{specificity_macro:.3f}")
    print(f"F1 Score (macro):   {f1:.3f}")
    print(f"AUC-ROC (macro-ovr):{auc_macro:.3f}")

    # --- Store metrics in results list ---
    results.append({
        "mode": mode,
        "Accuracy": round(acc, 3),
        "Precision (macro)": round(prec, 3),
        "Recall (macro)": round(rec, 3),
        "Specificity (macro)": round(specificity_macro, 3),
        "F1 Score (macro)": round(f1, 3),
        "AUC-ROC (macro-ovr)": round(auc_macro, 3)
    })

# === Save all results to CSV ===
# Create 'visualizations' folder if missing
os.makedirs("visualizations", exist_ok=True)

# Save summary CSV in the folder
output_path = os.path.join("visualizations", "model_metrics_summary.csv")
results_df = pd.DataFrame(results)
results_df.to_csv(output_path, index=False)

print(f"\n✅ Saved all metrics to {output_path}")
