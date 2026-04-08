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
            description=(
                "Extracts arguments, detects fallacies, checks consistency, "
                "evaluates validity/soundness, and serves as a meta-validator."
            ),
            system_prompt_dir=self._prompt_dir,
            fidelity=FidelityPolicy(
                mode=FidelityMode.GROUNDED,
                require_citations=False,           # logic is self-contained
                allow_marked_inference=True,
                inference_marker="*(inference)*",
                forbidden_patterns=(r"\bi think\b", r"\bprobably\b", r"\bobviously\b"),
            ),
            tools=(
                ToolSpec(
                    name="extract_argument",
                    description="Extract premises, conclusion, and implicit assumptions from text",
                    input_schema={"type": "object", "properties": {"text": {"type": "string"}}},
                    authoritative=True,
                    source_scope="analysis",
                    tags=("argument", "structure"),
                ),
                ToolSpec(
                    name="detect_fallacies",
                    description="Detect logical fallacies and weak reasoning patterns",
                    input_schema={"type": "object", "properties": {"argument": {"type": "string"}}},
                    tags=("fallacy", "analysis"),
                ),
                ToolSpec(
                    name="check_consistency",
                    description="Check for contradictions across multiple statements or steps",
                    input_schema={"type": "object", "properties": {"statements": {"type": "array"}}},
                    authoritative=True,
                    tags=("consistency", "logic"),
                ),
                ToolSpec(
                    name="evaluate_argument",
                    description="Assess logical validity and soundness",
                    input_schema={"type": "object", "properties": {"argument": {"type": "string"}}},
                    tags=("evaluation",),
                ),
                ToolSpec(
                    name="reconstruct_argument",
                    description="Reconstruct a full argument with explicit premises and conclusion",
                    input_schema={"type": "object", "properties": {"text": {"type": "string"}}},
                    authoritative=True,
                    tags=("reconstruction",),
                ),
            ),
        )

    async def run_tool(
        self,
        tool_name: str,
        instruction: str,
        arguments: Mapping[str, Any] | None = None,
    ) -> Any:
        args = arguments or {}
        if tool_name == "extract_argument":
            text = args.get("text", instruction)
            return {
                "premises": [s.strip() for s in text.split(".") if s.strip() and not s.strip().endswith("?")],
                "conclusion": text.split(".")[-1].strip() if "." in text else text,
                "implicit_assumptions": [],
                "citations": [],
            }

        elif tool_name == "detect_fallacies":
            argument = args.get("argument", instruction).lower()
            fallacies = []
            if any(word in argument for word in ["everyone knows", "obviously", "clearly"]):
                fallacies.append("appeal_to_popularity")
            if "always" in argument or "never" in argument:
                fallacies.append("hasty_generalization")
            if "you" in argument and ("should" in argument or "must" in argument):
                fallacies.append("appeal_to_emotion")
            if "because" in argument and "therefore" not in argument:
                fallacies.append("non_sequitur")
            return {"fallacies": fallacies, "citations": []}

        elif tool_name == "check_consistency":
            statements = args.get("statements", [])
            contradictions = []
            for i, a in enumerate(statements):
                for b in statements[i + 1 :]:
                    if ("not" in a.lower() and a.lower().replace("not ", "") in b.lower()) or (
                        "not" in b.lower() and b.lower().replace("not ", "") in a.lower()
                    ):
                        contradictions.append((a, b))
            return {"contradictions": contradictions, "citations": []}

        elif tool_name == "evaluate_argument":
            return {
                "valid": True,
                "sound": False,
                "reason": "Premises require external verification *(inference)*",
                "citations": [],
            }

        elif tool_name == "reconstruct_argument":
            text = args.get("text", instruction)
            return {
                "premises": [s.strip() for s in text.split(".") if s.strip()],
                "conclusion": text.split(".")[-1].strip(),
                "implicit_assumptions": ["*(inference)* The speaker assumes the premises are true"],
                "citations": [],
            }

        raise ValueError(f"Unknown tool: {tool_name}")

    async def retrieve_context(self, query: str, top_k: int = 5) -> list[str]:
        return []  # Pure reasoning pack — no external corpus needed

    def validate_step(self, tool_name: str, output: Any) -> ValidationResult:
        if not isinstance(output, dict):
            return ValidationResult(False, ("Output must be a dictionary",))
        if "citations" not in output:
            return ValidationResult(False, ("Output must contain 'citations' field",))
        return ValidationResult(True)

    def fidelity_audit(
        self, synthesis: str, citations: tuple[str, ...], ctx: Any | None = None
    ) -> ValidationResult:
        issues = []
        if "*(inference)*" in synthesis and not self.config.fidelity.allow_marked_inference:
            issues.append("Marked inference found but not allowed by policy")
        if "contradiction" in synthesis.lower() and ctx:
            issues.append("Contradiction detected in final synthesis")
        return ValidationResult(ok=not issues, issues=tuple(issues))

    def load_prompt(self, filename: str, **variables: Any) -> str:
        path = self._prompt_dir / filename
        content = path.read_text(encoding="utf-8")
        for key, value in variables.items():
            content = content.replace("{" + key + "}", str(value))
        return content
