import json
import re
from pathlib import Path
from typing import Any, Mapping

from domaintoolbelt_sdk.types import (
    DomainConfig,
    FidelityPolicy,
    FidelityMode,
    ToolSpec,
    ValidationResult,
)

# Deterministic Mock Database for Testing
_CVE_DB = {
    "CVE-2021-44228": "Log4Shell: Improper input validation in Apache Log4j leading to RCE.",
    "CVE-2023-4863": "Heap buffer overflow in libwebp allowing out-of-bounds memory write.",
}
_CWE_DB = {
    "CWE-89": "SQL Injection: Improper neutralization of special elements used in an SQL Command.",
    "CWE-79": "Cross-Site Scripting (XSS): Improper neutralization of input during web page generation.",
}

class SecOpsPack:
    def __init__(self, storage_root: str | Path = ".domaintoolbelt"):
        self._prompt_dir = Path(__file__).parent / "prompts"
        self.config = DomainConfig(
            key="secops_pack",
            display_name="Software Security Operations Pack",
            description="Audits code snippets and retrieves authoritative CVE/CWE vulnerability data.",
            system_prompt_dir=self._prompt_dir,
            fidelity=FidelityPolicy(
                mode=FidelityMode.STRICT, 
                require_citations=True,
                strict_verbatim_only=True,
                forbidden_patterns=(r"\bi think\b", r"\bmaybe\b", r"\bprobably\b", r"\blooks like\b")
            ),
            tools=(
                ToolSpec(
                    name="lookup_cve_cwe",
                    description="Retrieve authoritative definitions for specific CVEs or CWEs.",
                    input_schema={"type": "object", "properties": {"identifier": {"type": "string"}}},
                    authoritative=True,
                    source_scope="primary",
                ),
                ToolSpec(
                    name="analyze_code_snippet",
                    description="Analyze a code snippet for known CWE patterns.",
                    input_schema={"type": "object", "properties": {"code": {"type": "string"}}},
                    authoritative=False,
                    source_scope="secondary",
                ),
            ),
            tradition_flags={
                "framework": "OWASP Top 10",
                "focus": "Static Application Security Testing (SAST)",
            }
        )

    async def run_tool(self, tool_name: str, instruction: str, arguments: Mapping[str, Any] | None = None) -> Any:
        args = arguments or {}
        
        if tool_name == "lookup_cve_cwe":
            identifier = args.get("identifier", "").upper()
            if identifier in _CVE_DB:
                return {"data": _CVE_DB[identifier], "citations": [identifier]}
            elif identifier in _CWE_DB:
                return {"data": _CWE_DB[identifier], "citations": [identifier]}
            return {"data": "Identifier not found in registry.", "citations": []}

        if tool_name == "analyze_code_snippet":
            code = args.get("code", instruction).lower()
            detected = []
            citations = []
            if "select *" in code and "+" in code:  # Very naive SQLi detection
                detected.append(_CWE_DB["CWE-89"])
                citations.append("CWE-89")
            if "<script>" in code:
                detected.append(_CWE_DB["CWE-79"])
                citations.append("CWE-79")
            
            if not detected:
                return {"data": "No standard vulnerabilities detected in snippet.", "citations": []}
            return {"data": " | ".join(detected), "citations": citations}

        raise NotImplementedError(f"Tool {tool_name} not implemented.")

    async def retrieve_context(self, query: str, top_k: int = 5) -> list[str]:
        # Minimal keyword retrieval against our mock DBs
        results = []
        for db in (_CVE_DB, _CWE_DB):
            for key, val in db.items():
                if key.lower() in query.lower() or query.lower() in val.lower():
                    results.append(f"[{key}] {val}")
        return results[:top_k]

    def validate_step(self, tool_name: str, output: Any) -> ValidationResult:
        if not isinstance(output, dict) or "citations" not in output:
            return ValidationResult(ok=False, issues=("Tool output must be a dict containing 'citations'.",))
        return ValidationResult(ok=True)

    def fidelity_audit(self, synthesis: str, citations: tuple[str, ...]) -> ValidationResult:
        issues = []
        if not citations and self.config.fidelity.require_citations:
            issues.append("Missing CVE/CWE citations. Security audits must cite specific weakness identifiers.")
        
        # Ensure citations match the required format (CVE-YYYY-NNNN or CWE-NNN)
        valid_citation_re = re.compile(r"^(CVE-\d{4}-\d{4,7}|CWE-\d{1,4})$")
        invalid = [c for c in citations if not valid_citation_re.match(str(c))]
        if invalid:
            issues.append(f"Invalid citation format detected: {', '.join(invalid)}")
            
        return ValidationResult(ok=not issues, issues=tuple(issues))

    def load_prompt(self, filename: str, **variables: Any) -> str:
        # In a real implementation, this reads from the file system.
        # Here we provide a mock router for the 6 required prompts.
        prompts = {
            "create_action_plan.md": "Create a security audit plan for the following request: {request}. Prioritize checking for known CWEs.",
            "intent_disambiguation.md": "Determine if the user wants a code audit, a CVE lookup, or remediation advice for: {request}.",
            "supervisor.md": "You are a strict AppSec supervisor. Ensure no vulnerabilities are hallucinated. Reject speculative findings.",
            "tool_instruction.md": "Execute security tool for step: {step_description}. Request context: {request}.",
            "tool_selection.md": "Select the appropriate security tool. Available: {tools}.",
            "write_final_answer.md": "Synthesize the security report for {request}. Base findings strictly on: {evidence}. Include mitigation strategies."
        }
        content = prompts.get(filename, "Missing prompt file.")
        for key, value in variables.items():
            content = content.replace("{" + key + "}", str(value))
        return content
