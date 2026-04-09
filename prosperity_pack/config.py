from pathlib import Path
from typing import Any, Mapping

from domaintoolbelt_sdk.types import (
    DomainConfig,
    FidelityPolicy,
    FidelityMode,
    ToolSpec,
    ValidationResult,
)


class ProsperityPack:
    def __init__(self, storage_root: str | Path = ".domaintoolbelt"):
        self._prompt_dir = Path(__file__).parent / "prompts"

        self.config = DomainConfig(
            key="prosperity_pack",
            display_name="Foundations of Prosperity",
            description="Economics, political philosophy, and principles of wealth creation and human flourishing.",
            system_prompt_dir=self._prompt_dir,
            fidelity=FidelityPolicy(
                mode=FidelityMode.GROUNDED,
                require_citations=True,
                allow_marked_inference=True,
                inference_marker="*(inference)*",
                forbidden_patterns=(r"\bi think\b", r"\bprobably\b", r"\bobviously\b"),
            ),
            tools=(
                ToolSpec(
                    name="lookup_principle",
                    description="Retrieve primary economic or philosophical principles on prosperity",
                    input_schema={"type": "object", "properties": {"query": {"type": "string"}}},
                    authoritative=True,
                    source_scope="primary",
                    retrieval_mode="similar",
                    tags=("principle", "economics"),
                ),
                ToolSpec(
                    name="cross_reference_thinkers",
                    description="Surface thinkers in dialectical tension (contrastive mode)",
                    input_schema={"type": "object", "properties": {"seed": {"type": "string"}}},
                    source_scope="philosophy",
                    retrieval_mode="contrastive",
                    tags=("debate", "philosophy"),
                ),
                ToolSpec(
                    name="evaluate_policy_impact",
                    description="Assess policy impact on long-term prosperity",
                    input_schema={"type": "object", "properties": {"policy": {"type": "string"}}},
                    tags=("policy", "evaluation"),
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
        if tool_name == "lookup_principle":
            query = args.get("query", instruction)
            from prosperity_pack.mcp_tools import lookup_principle
            return await lookup_principle(query)
        elif tool_name == "cross_reference_thinkers":
            seed = args.get("seed", instruction)
            from prosperity_pack.mcp_tools import cross_reference_thinkers
            return await cross_reference_thinkers(seed)
        elif tool_name == "evaluate_policy_impact":
            policy = args.get("policy", instruction)
            from prosperity_pack.mcp_tools import evaluate_policy_impact
            return await evaluate_policy_impact(policy)
        raise ValueError(f"Unknown tool: {tool_name}")

    async def retrieve_context(self, query: str, top_k: int = 5) -> list[str]:
        from prosperity_pack.mcp_tools import build_retriever
        matches = build_retriever().search(query, top_k=top_k)
        return [item["text"] for item in matches]

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
        if not citations and self.config.fidelity.require_citations:
            issues.append("Citations required for prosperity claims")
        if "*(inference)*" in synthesis and not self.config.fidelity.allow_marked_inference:
            issues.append("Marked inference found but not allowed by policy")
        return ValidationResult(ok=not issues, issues=tuple(issues))

    def load_prompt(self, filename: str, **variables: Any) -> str:
        path = self._prompt_dir / filename
        content = path.read_text(encoding="utf-8")
        for key, value in variables.items():
            content = content.replace("{" + key + "}", str(value))
        return content