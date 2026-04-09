from pathlib import Path
from typing import Any, Mapping

from domaintoolbelt_sdk.types import (
    DomainConfig,
    FidelityPolicy,
    FidelityMode,
    ToolSpec,
    ValidationResult,
)


class FutureProsperityPack:
    def __init__(self, storage_root: str | Path = ".domaintoolbelt"):
        self._prompt_dir = Path(__file__).parent / "prompts"

        self.config = DomainConfig(
            key="future_prosperity_pack",
            display_name="Future Prosperity Scenarios",
            description="Predictable long-term technological and societal prosperity (AI, energy, biotech, space).",
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
                    name="forecast_scenario",
                    description="Forecast plausible future scenario for a technology or trend",
                    input_schema={"type": "object", "properties": {"trend": {"type": "string"}}},
                    authoritative=True,
                    source_scope="primary",
                    retrieval_mode="contrastive",
                    tags=("forecast", "future"),
                ),
                ToolSpec(
                    name="map_risk_opportunity",
                    description="Map risks and opportunities in emerging tech scenarios",
                    input_schema={"type": "object", "properties": {"scenario": {"type": "string"}}},
                    tags=("risk", "opportunity"),
                ),
                ToolSpec(
                    name="evaluate_optimism_pathway",
                    description="Evaluate definite vs indefinite optimism pathways",
                    input_schema={"type": "object", "properties": {"pathway": {"type": "string"}}},
                    retrieval_mode="contrastive",
                    tags=("optimism", "strategy"),
                ),
            ),
        )

    async def run_tool(
        self,
        tool_name: str,
        instruction: str,
        arguments: Mapping[str, Any] | None = None,
    ) -> Any:
        from future_prosperity_pack.mcp_tools import TOOLS
        if tool_name not in TOOLS:
            raise ValueError(f"Unknown tool: {tool_name}")
        return await TOOLS[tool_name](instruction, arguments)

    async def retrieve_context(self, query: str, top_k: int = 5) -> list[str]:
        from future_prosperity_pack.mcp_tools import build_retriever
        matches = build_retriever().search(query, top_k=top_k)
        return [item["text"] for item in matches]

    def validate_step(self, tool_name: str, output: Any) -> ValidationResult:
        if not isinstance(output, dict) or "citations" not in output:
            return ValidationResult(False, ("Missing citations field",))
        return ValidationResult(True)

    def fidelity_audit(
        self, synthesis: str, citations: tuple[str, ...], ctx: Any | None = None
    ) -> ValidationResult:
        issues = []
        if not citations and self.config.fidelity.require_citations:
            issues.append("Citations required for future prosperity claims")
        return ValidationResult(ok=not issues, issues=tuple(issues))

    def load_prompt(self, filename: str, **variables: Any) -> str:
        path = self._prompt_dir / filename
        content = path.read_text(encoding="utf-8")
        for key, value in variables.items():
            content = content.replace("{" + key + "}", str(value))
        return content