from domaintoolbelt_sdk.types import ValidationResult


def validate_reasoning_output(tool_name: str, output: Any) -> ValidationResult:
    if not isinstance(output, dict):
        return ValidationResult(False, ("Reasoning output must be a dict",))
    return ValidationResult(True)
