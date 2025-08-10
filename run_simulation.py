# run_simulation.py
# This script tests the ethical decision-making logic functions
# by running them on a set of predefined scenarios
# and logging the results to a CSV file.

from ethics_logic_reporting import utilitarian_decision, deontological_decision, virtue_ethics_decision
import csv
import os

# Define test scenarios with:
# - name: type of ethical dilemma
# - left_risk, right_risk: numerical values indicating the risk on each side
# - left_is_child: boolean indicating if a child is present on the left side
scenarios = [
    {"name": "car_vs_pedestrian", "left_risk": 10, "right_risk": 3, "left_is_child": False},
    {"name": "car_vs_car", "left_risk": 7, "right_risk": 6, "left_is_child": False},
    {"name": "pedestrian_vs_pedestrian", "left_risk": 6, "right_risk": 4, "left_is_child": True}
]

# Maps ethical mode names to their corresponding decision-making functions
ethics = {
    "utilitarian": utilitarian_decision,
    "deontological": deontological_decision,
    "virtue": virtue_ethics_decision
}

# Ensures that the "results" folder exists to store the CSV output
os.makedirs("results", exist_ok=True)

# Opens a CSV file for writing results
with open("results/ethical_decision_log.csv", "w", newline="") as f:
    writer = csv.writer(f)

    # Writes the CSV header row
    writer.writerow(["scenario", "mode", "decision"])

    # Iterates through each scenario and each ethical mode
    for scenario in scenarios:
        for mode_name, mode_func in ethics.items():
            # Runs the corresponding decision function for this mode
            decision = mode_func(scenario)

            # Logs the scenario, mode, and resulting decision to the CSV file
            writer.writerow([scenario["name"], mode_name, decision])

            # Prints the decision to the console for quick verification
            print(f"{scenario['name']} | {mode_name} => {decision}")
