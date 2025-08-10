# ethics_engine.py
# This file contains the core ethical decision-making rules for three different
# philosophical approaches: utilitarianism, deontological ethics, and virtue ethics.
# Each function accepts a dictionary of scenario data and returns an action string.

def utilitarian_decision(data):
    """
    Implements a utilitarian decision rule.
    Goal: minimize overall harm, regardless of strict rules or character virtues.
    """
    if data["name"] == "car_vs_pedestrian":
        return "swerve_left"  # Left side has a car, so swerving toward it avoids hitting a pedestrian.
    elif data["name"] == "car_vs_car":
        return "swerve_left"  # Assumes left car poses less harm; choose lesser damage.
    elif data["name"] == "pedestrian_vs_pedestrian":
        return "brake"        # Both sides involve pedestrians, so stop to minimize harm.
    return "straight"         # Default action if scenario is unknown.


def deontological_decision(data):
    """
    Implements a deontological decision rule.
    Goal: follow strict moral rules, regardless of outcome optimization.
    """
    if data["name"] == "car_vs_pedestrian":
        return "brake"        # Moral rule: never harm a human if avoidable.
    elif data["name"] == "car_vs_car":
        return "brake"        # Moral rule: stop before impact, regardless of which side.
    elif data["name"] == "pedestrian_vs_pedestrian":
        return "brake"        # Moral rule: do not harm humans; stopping is safest.
    return "straight"         # Default action if scenario is unknown.


def virtue_ethics_decision(data):
    """
    Implements a virtue ethics decision rule.
    Goal: act with moral character, compassion, and context awareness.
    """
    if data["name"] == "car_vs_pedestrian":
        return "swerve_left"  # Shows moral character by protecting human life.
    elif data["name"] == "car_vs_car":
        return "slow down"    # Demonstrates caution and thoughtfulness.
    elif data["name"] == "pedestrian_vs_pedestrian":
        return "brake"        # Acts with compassion by stopping.
    return "straight"         # Default action if scenario is unknown.
