def compare_values(actual, expected, operator):
    """
    Compare an actual value with the expected value using
    the operator defined in the requirement configuration.
    """

    if operator == "equals":
        return actual == expected

    if operator == "not_equals":
        return actual != expected

    if operator == "greater_than":
        return actual is not None and actual > expected

    if operator == "greater_than_or_equal":
        return actual is not None and actual >= expected

    if operator == "less_than":
        return actual is not None and actual < expected

    if operator == "less_than_or_equal":
        return actual is not None and actual <= expected

    if operator == "contains":
        return (
            actual is not None
            and str(expected).lower() in str(actual).lower()
        )

    if operator == "in":
        return actual in expected

    # Unknown operators must not accidentally produce PASS.
    return False


def evaluate_requirement(parsed_data, requirement):
    """
    Evaluate normalized parser data against a requirement definition.
    """

    result = {
        "requirement": requirement["requirement"],
        "description": requirement["description"],
        "status": "PASS",
        "details": []
    }

    for check in requirement["checks"]:

        key = check["key"]
        expected = check["expected"]

        # Preserve backward compatibility with old requirement files.
        operator = check.get("operator", "equals")

        actual = parsed_data.get(key)

        passed = compare_values(
            actual,
            expected,
            operator
        )

        if not passed:
            result["status"] = "FAIL"

        result["details"].append({
            "setting": key,
            "operator": operator,
            "expected": expected,
            "actual": actual,
            "result": "PASS" if passed else "FAIL"
        })

    return result