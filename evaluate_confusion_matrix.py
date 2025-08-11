# evaluate_confusion_matrix.py
# This script evaluates trained ML models for each ethical mode by:
# 1. Loading the labeled dataset for that mode
# 2. Predicting actions using the corresponding trained model
# 3. Computing and displaying a confusion matrix comparing predicted vs. actual actions
# 4. Saving the confusion matrix visualization as a PNG in the "visualizations" folder

import os
import pandas as pd          # For dataset loading and DataFrame operations
import numpy as np           # For numerical operations and unique label extraction
import joblib                # For loading saved ML models
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt  # For plotting confusion matrices

# Create the "visualizations" folder if it doesn't exist
os.makedirs("visualizations", exist_ok=True)

# List of features used in training and prediction
FEATURES = ["left_risk", "right_risk", "speed_kph", "name", "child_present"]

# Ethical modes to evaluate (matching model filenames and datasets)
MODES = ["utilitarian", "deontological", "virtue"]

# Iterate over each ethical mode
for mode in MODES:
    print(f"\n=== {mode.capitalize()} Mode ===")

    # --- Load the labeled dataset for the current mode ---
    df = pd.read_csv(f"labeled_data/{mode}_labeled.csv")
    X = df[FEATURES]                  # Feature columns
    y = df["action"].astype(str)      # Actual actions as strings

    # --- Load the corresponding trained ML model ---
    model = joblib.load(f"models/{mode}.pkl")

    # --- Make predictions on the full dataset ---
    y_pred = model.predict(X)

    # --- Compute confusion matrix ---
    labels = np.unique(y)  # Ensure consistent label ordering
    cm = confusion_matrix(y, y_pred, labels=labels)
    print("Confusion Matrix (rows = actual, cols = predicted):")
    print(pd.DataFrame(cm, index=labels, columns=labels))

    # --- Plot confusion matrix ---
    fig, ax = plt.subplots(figsize=(8, 6))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
    disp.plot(cmap=plt.cm.Blues, ax=ax, values_format="d")
    plt.title(f"{mode.capitalize()} Mode Confusion Matrix", fontsize=14)

    # --- Save the plot to the visualizations folder ---
    save_path = os.path.join("visualizations", f"{mode}_confusion_matrix.png")
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    print(f"✅ Saved confusion matrix to {save_path}")

    # --- Close the figure to free memory ---
    plt.close(fig)
