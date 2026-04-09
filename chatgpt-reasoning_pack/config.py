from pathlib import Path
from typing import Any, Mapping

from domaintoolbelt_sdk.types import (
    DomainConfig,
    FidelityPolicy,
    FidelityMode,
    ToolSpec,
    ValidationResult,
)


class ReasoningPack:
    def __init__(self, storage_root: str | Path = ".domaintoolbelt"):
        self._prompt_dir = Path(__file__).parent / "prompts"

        self.config = DomainConfig(
            key="reasoning_pack",
            display_name="Formal Reasoning & Argument Analysis",
            description="Analyze arguments, detect fallacies, and ensure logical consistency.",
            system_prompt_dir=self._prompt_dir,
            fidelity=FidelityPolicy(
                mode=FidelityMode.GROUNDED,
                require_citations=False,  # logic doesn't always require external sources
            ),
            tools=(
                ToolSpec(
                    name="extract_argument",
                    description="Extract premises and conclusion from text",
                    input_schema={
                        "type": "object",
                        "properties": {"text": {"type": "string"}},
                    },
                    authoritative=True,
                    source_scope="analysis",
                    tags=("argument", "structure"),
                ),
                ToolSpec(
                    name="detect_fallacies",
                    description="Detect logical fallacies in argument",
                    input_schema={
                        "type": "object",
                        "properties": {"argument": {"type": "string"}},
                    },
                    tags=("fallacy", "analysis"),
                ),
                ToolSpec(
                    name="check_consistency",
                    description="Check for contradictions across statements",
                    input_schema={
                        "type": "object",
                        "properties": {"statements": {"type": "array"}},
                    },
                    authoritative=True,
                    tags=("consistency", "logic"),
                ),
                ToolSpec(
                    name="evaluate_argument",
                    description="Assess validity and soundness",
                    input_schema={
                        "type": "object",
                        "properties": {"argument": {"type": "string"}},
                    },
                    tags=("evaluation",),
                ),
            ),
        )

    async def run_tool(
        self,
        tool_name: str,
        instruction: str,
        arguments: Mapping[str, Any] | None = None,
    ) -> Any:

        if tool_name == "extract_argument":
            text = arguments.get("text", instruction)

            # Simple deterministic heuristic
            return {
                "premises": [
                    s.strip() for s in text.split(".")[:-1]
                ],
                "conclusion": text.split(".")[-1].strip(),
                "citations": []
            }

        elif tool_name == "detect_fallacies":
            argument = arguments.get("argument", instruction)

            fallacies = []
            if "everyone knows" in argument:
                fallacies.append("appeal_to_popularity")
            if "you always" in argument:
                fallacies.append("hasty_generalization")

            return {
                "fallacies": fallacies,
                "citations": []
            }

        elif tool_name == "check_consistency":
            statements = arguments.get("statements", [])

            contradictions = []
            if len(statements) >= 2:
                if "not" in statements[0] and statements[0].replace("not ", "") in statements[1]:
                    contradictions.append((statements[0], statements[1]))

            return {
                "contradictions": contradictions,
                "citations": []
            }

        elif tool_name == "evaluate_argument":
            return {
                "valid": True,
                "sound": False,
                "reason": "Premises not verified",
                "citations": []
            }

        raise ValueError(f"Unknown tool: {tool_name}")

    async def retrieve_context(self, query: str, top_k: int = 5) -> list[str]:
        return []

    def validate_step(self, tool_name: str, output: Any) -> ValidationResult:
        if not isinstance(output, dict):
            return ValidationResult(False, ("Output must be dict",))

        if "citations" not in output:
            return ValidationResult(False, ("Missing citations field",))

        return ValidationResult(True)

    def fidelity_audit(self, synthesis: str, citations: tuple[str, ...]) -> ValidationResult:
        issues = []

        # Logic-specific rule
        if "contradiction" in synthesis.lower():
            issues.append("Detected contradiction in final synthesis")

        return ValidationResult(ok=not issues, issues=tuple(issues))

    def load_prompt(self, filename: str, **variables: Any) -> str:
        path = self._prompt_dir / filename
        content = path.read_text(encoding="utf-8")

        for key, value in variables.items():
            content = content.replace("{" + key + "}", str(value))

        return content
