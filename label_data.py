# label_data.py
# This script generates a synthetic dataset of driving scenarios with multiple features,
# then uses the teacher model (rules_adapter) to assign an action label for each row.
# One CSV file is created per ethical mode.

import numpy as np          # For random number generation
import pandas as pd         # For DataFrame creation and CSV writing
import os                   # For file and directory handling

# Uses the adapter instead of directly importing ethics_engine
# so that extra features (child_present, left_risk, etc.) actually influence decisions.
import rules_adapter as teacher

# ----------------------------
# Configuration section
# ----------------------------
RNG_SEED = 42  # Random seed to make the dataset generation reproducible
N_ROWS = 10000  # Number of synthetic rows to generate
SCENARIOS = ["car_vs_pedestrian", "car_vs_car", "pedestrian_vs_pedestrian"]  # Scenario types
MODES = ["utilitarian", "deontological", "virtue"]  # Ethical modes to label data for
OUT_DIR = "labeled_data"  # Directory to save generated CSVs

# ----------------------------
# Main script logic
# ----------------------------
if __name__ == "__main__":
    # Creates a reproducible random number generator
    rng = np.random.default_rng(RNG_SEED)

    # Creates the output directory if it does not exist
    os.makedirs(OUT_DIR, exist_ok=True)

    # Generates the synthetic dataset with richer features (no weather)
    df = pd.DataFrame({
        "name": rng.choice(SCENARIOS, N_ROWS),       # Randomly pick one of the scenarios
        "child_present": rng.integers(0, 2, N_ROWS), # 0 = no child, 1 = child present
        "left_risk": rng.random(N_ROWS),             # Continuous value between 0.0 and 1.0
        "right_risk": rng.random(N_ROWS),            # Continuous value between 0.0 and 1.0
        "speed_kph": rng.integers(0, 71, N_ROWS),    # Speed in km/h between 0 and 70
    })

    # Iterates over each ethical mode and labels the dataset separately
    for mode in MODES:
        actions = []  # Stores the decision for each row

        # Iterates over all rows in the DataFrame
        for _, row in df.iterrows():
            # Converts the row to a dictionary and passes it to the teacher to get a decision
            a = teacher.decide_action(mode, row.to_dict())
            actions.append(a)

        # Creates a copy of the DataFrame to attach mode and action columns
        out = df.copy()
        out["mode"] = mode
        out["action"] = actions

        # Saves the labeled dataset to a CSV file for the current mode
        fname = os.path.join(OUT_DIR, f"{mode}_labeled.csv")
        out.to_csv(fname, index=False)

        # Prints confirmation with file path and row count
        print(f"✅ wrote {fname} ({len(out)} rows)")
