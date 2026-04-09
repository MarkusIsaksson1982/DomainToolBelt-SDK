from pathlib import Path
from typing import Any, Mapping

from domaintoolbelt_sdk.types import (
    DomainConfig,
    FidelityPolicy,
    FidelityMode,
    ToolSpec,
    ValidationResult,
)


class EntrepreneurshipPack:
    def __init__(self, storage_root: str | Path = ".domaintoolbelt"):
        self._prompt_dir = Path(__file__).parent / "prompts"

        self.config = DomainConfig(
            key="entrepreneurship_pack",
            display_name="Entrepreneurship & Innovation",
            description="Startups, innovation, technology-driven value creation, and future scenarios (AI, biotech, energy, space).",
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
                    name="analyze_startup_case",
                    description="Analyze a startup or business case for success factors",
                    input_schema={"type": "object", "properties": {"company": {"type": "string"}}},
                    authoritative=True,
                    source_scope="primary",
                    retrieval_mode="similar",
                    tags=("startup", "analysis"),
                ),
                ToolSpec(
                    name="forecast_tech_impact",
                    description="Forecast technology impact on future scenarios",
                    input_schema={"type": "object", "properties": {"technology": {"type": "string"}}},
                    source_scope="primary",
                    retrieval_mode="contrastive",
                    tags=("technology", "forecast"),
                ),
                ToolSpec(
                    name="evaluate_innovation_pathway",
                    description="Evaluate innovation strategy and market opportunities",
                    input_schema={"type": "object", "properties": {"strategy": {"type": "string"}}},
                    tags=("innovation", "strategy"),
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
        if tool_name == "analyze_startup_case":
            company = args.get("company", instruction)
            from entrepreneurship_pack.mcp_tools import analyze_startup_case
            return await analyze_startup_case(company)
        elif tool_name == "forecast_tech_impact":
            technology = args.get("technology", instruction)
            from entrepreneurship_pack.mcp_tools import forecast_tech_impact
            return await forecast_tech_impact(technology)
        elif tool_name == "evaluate_innovation_pathway":
            strategy = args.get("strategy", instruction)
            from entrepreneurship_pack.mcp_tools import evaluate_innovation_pathway
            return await evaluate_innovation_pathway(strategy)
        raise ValueError(f"Unknown tool: {tool_name}")

    async def retrieve_context(self, query: str, top_k: int = 5) -> list[str]:
        from entrepreneurship_pack.mcp_tools import build_retriever
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
            issues.append("Citations required for entrepreneurship claims")
        if "*(inference)*" in synthesis and not self.config.fidelity.allow_marked_inference:
            issues.append("Marked inference found but not allowed by policy")
        return ValidationResult(ok=not issues, issues=tuple(issues))

    def load_prompt(self, filename: str, **variables: Any) -> str:
        path = self._prompt_dir / filename
        content = path.read_text(encoding="utf-8")
        for key, value in variables.items():
            content = content.replace("{" + key + "}", str(value))
        return content