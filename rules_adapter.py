# rules_adapter.py
# Acts as an adapter that applies extra heuristics based on additional features
# (e.g., child_present, left_risk, right_risk, speed_kph) on top of the existing
# rule-based decisions from ethics_engine.py without modifying the original rules.

import ethics_engine  # Imports the original rule-based decision logic

# --- Normalization helpers ---
def _norm(a: str) -> str:
    # Ensures the returned action string is consistent and lowercase
    if a is None: return "brake"  # Defaults to "brake" if no action is given
    a = str(a).strip().lower()    # Converts to lowercase and strips whitespace
    if a == "straight": return "hold_lane"  # Maps "straight" to "hold_lane" for consistency
    if a == "slow down": return "slow_down" # Maps spaced phrase to underscore version
    return a  # Returns the cleaned action string as-is

def _riskify(x):
    # Converts a risk value to a float and ensures it lies between 0.0 and 1.0
    try:
        v = float(x)
        return min(max(v, 0.0), 1.0)  # Clamps the value to [0.0, 1.0]
    except:
        return 0.0  # Defaults to 0.0 if value is invalid

def _base_decision(mode: str, data: dict) -> str:
    # Calls the corresponding function from ethics_engine.py based on the ethical mode
    # and normalizes the returned action
    if mode == "utilitarian":
        return _norm(ethics_engine.utilitarian_decision(data))
    elif mode == "deontological":
        return _norm(ethics_engine.deontological_decision(data))
    else:
        return _norm(ethics_engine.virtue_ethics_decision(data))

def decide_action(mode: str, data: dict) -> str:
    """
    Produces the final teacher decision by taking the base decision from
    ethics_engine.py and refining it using additional features:
      - child_present (0/1)
      - left_risk, right_risk (0–1 range)
      - speed_kph (integer)
    This function leaves the original ethics_engine.py untouched.
    """
    mode = str(mode).lower()  # Converts the mode to lowercase for uniformity
    base = _base_decision(mode, data)  # Gets the base action from ethics_engine

    # Reads additional feature values from the input, with defaults if missing
    child   = int(data.get("child_present", 0))
    left_r  = _riskify(data.get("left_risk", 0.0))
    right_r = _riskify(data.get("right_risk", 0.0))
    speed   = int(data.get("speed_kph", 0))

    # Calculates "effective" risks by adding a small penalty proportional to speed
    left_eff  = min(1.0, left_r  + (speed/120.0)*0.10)
    right_eff = min(1.0, right_r + (speed/120.0)*0.10)
    total_eff = left_eff + right_eff  # Combined total risk
    max_eff   = max(left_eff, right_eff)  # Higher of the two side risks
    diff_eff  = abs(left_eff - right_eff) # Difference between left and right risks

    # Defines constant thresholds for decision-making
    HIGH_SPEED         = 45    # kph threshold considered too fast
    VERY_HIGH_TOTAL    = 1.40  # Sum of effective risks considered too dangerous
    HIGH_SIDE_RISK     = 0.75  # Single side risk considered high
    MEANINGFUL_DIFF    = 0.15  # Minimum risk difference that matters for swerving

    # Applies universal safety rules regardless of ethical mode
    if total_eff >= VERY_HIGH_TOTAL or speed >= HIGH_SPEED:
        return "brake"  # Always brake if total risk is very high or speed is too high

    # Prevents swerving toward the side with greater risk if a child is present
    if child == 1:
        if left_eff > right_eff and base == "swerve_left":
            base = "brake"
        if right_eff > left_eff and base == "swerve_right":
            base = "brake"

    # --- Mode-specific refinements ---
    if mode.startswith("util"):
        # For utilitarian mode: minimize overall harm
        if max_eff < 0.30 and diff_eff < MEANINGFUL_DIFF:
            return "hold_lane"  # Stay in lane if risks are low and similar
        if left_eff < right_eff - MEANINGFUL_DIFF:
            return "swerve_left"  # Swerve toward lower-risk side
        if right_eff < left_eff - MEANINGFUL_DIFF:
            return "swerve_right"
        if max_eff >= HIGH_SIDE_RISK:
            return "brake"  # Brake if one side has very high risk
        return base  # Default to the base decision otherwise

    if mode.startswith("deon"):
        # For deontological mode: follow strict safety duties
        if max_eff >= HIGH_SIDE_RISK:
            return "brake"
        if child == 1:
            return "brake"  # Always brake if a child is present
        if diff_eff >= MEANINGFUL_DIFF and max_eff < HIGH_SIDE_RISK:
            return "hold_lane"  # Stay in lane if difference is meaningful but risks not too high
        return "brake" if base == "brake" else "hold_lane"

    # For virtue ethics mode: act cautiously and compassionately
    if child == 1 or max_eff >= 0.40:
        return "slow_down"  # Slow down if a child is present or moderate risk is detected
    if diff_eff >= MEANINGFUL_DIFF and max_eff < 0.50:
        return "swerve_left" if left_eff < right_eff else "swerve_right"
    return "hold_lane"  # Default cautious action if no other condition applies
