# ethics_logic_reporting.py
# This file defines simplified ethical decision-making rules
# for three different philosophical approaches:
# Utilitarianism, Deontological ethics, and Virtue ethics.
# Each function accepts a dictionary containing a scenario description
# and returns a driving action.

def utilitarian_decision(scenario):
    """
    Utilitarian decision-making:
    - Goal: choose the action that minimizes total harm.
    - In this simplified rule set:
        * If the scenario involves 'car_vs_car', the decision is to swerve.
        * In all other scenarios, the decision is to brake.
    """
    if scenario["name"] == "car_vs_car":
        return "swerve"
    return "brake"


def deontological_decision(scenario):
    """
    Deontological decision-making:
    - Goal: follow strict moral rules regardless of outcomes.
    - In this simplified version:
        * Always brake, regardless of scenario type.
    """
    return "brake"


def virtue_ethics_decision(scenario):
    """
    Virtue ethics decision-making:
    - Goal: act according to moral character, compassion, and good judgement.
    - In this simplified rule set:
        * If the scenario is 'car_vs_car' or 'pedestrian_vs_pedestrian', slow down.
        * In all other cases, brake.
    """
    if scenario["name"] in ["car_vs_car", "pedestrian_vs_pedestrian"]:
        return "slow down"
    return "brake"
