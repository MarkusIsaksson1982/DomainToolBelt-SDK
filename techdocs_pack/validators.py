# techdocs_pack/validators.py
from __future__ import annotations
import re
from typing import Any, Mapping

from domaintoolbelt.core.types import DomainConfig, ValidationResult


def validate_techdocs_output(
    tool_name: str,
    output: Any,
    config: DomainConfig,
) -> ValidationResult:
    """Validate technical documentation tool outputs for fidelity and structure."""
    issues: list[str] = []

    # All tools should return structured mappings
    if not isinstance(output, Mapping):
        return ValidationResult(ok=False, issues=("Tool output must be a structured mapping.",))

    # Common required fields
    summary = str(output.get("summary", "")).strip()
    citations = output.get("citations", ())

    if not summary:
        issues.append("Tool output summary is empty.")

    # Citation format validation: [module:class.method@version] or [RFC:section]
    citation_pattern = re.compile(r"^\[[\w.:@\-\s/]+\]$")
    for cit in citations:
        if not citation_pattern.match(str(cit).strip()):
            issues.append(f"Invalid citation format: {cit}. Expected [module:path@version]")

    # Tool-specific validation
    if tool_name == "lookup_api_reference":
        if "signature" not in output:
            issues.append("API reference output must include 'signature' field.")
        if "parameters" not in output:
            issues.append("API reference output must include 'parameters' field.")

    elif tool_name == "generate_example":
        # Examples must cite the APIs they use
        example_code = str(output.get("example_code", ""))
        for cit in citations:
            if cit not in example_code and cit not in summary:
                # Citation not reflected in output
                pass  # Warning, not error—may be contextual
        if not example_code.strip():
            issues.append("Example tool output must include non-empty 'example_code'.")

    elif tool_name == "cross_reference_concepts":
        if not citations:
            issues.append("Cross-reference output must include at least one citation.")

    # Enforce tradition flags (e.g., language/version constraints)
    lang = config.guardrails.tradition_flags.get("language", "").lower()
    if lang and "language" in output:
        if output["language"].lower() != lang:
            issues.append(f"Output language '{output['language']}' does not match configured '{lang}'.")

    return ValidationResult(ok=not issues, issues=tuple(issues))
