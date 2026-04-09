from domaintoolbelt_sdk.types import ValidationResult


def validate_entrepreneurship_output(tool_name: str, output: any) -> ValidationResult:
    if not isinstance(output, dict):
        return ValidationResult(False, ("Output must be a dictionary",))
    if "citations" not in output:
        return ValidationResult(False, ("Output must contain citations field",))
    return ValidationResult(True)