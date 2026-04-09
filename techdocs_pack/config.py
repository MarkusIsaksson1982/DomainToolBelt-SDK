# techdocs_pack/config.py
from __future__ import annotations
from pathlib import Path
from typing import Any, Mapping

from domaintoolbelt.core.prompt_loader import PromptLoader
from domaintoolbelt.core.types import (
    DomainConfig,
    FidelityMode,
    FidelityPolicy,
    GuardrailConfig,
    MemoryConfig,
    RAGConfig,
    ToolRegistryConfig,
    ToolSpec,
    ValidationConfig,
    ValidationResult,
)
from techdocs_pack.mcp_tools import TOOLS, build_retriever, corpus_records
from techdocs_pack.truth_policy import TECHDOCS_FIDELITY_POLICY
from techdocs_pack.validators import validate_techdocs_output
from domaintoolbelt.rag.retriever import KeywordRetriever


class TechDocsPack:
    """Pack for authoritative technical documentation lookup and synthesis."""

    def __init__(self, storage_root: str | Path = ".domaintoolbelt") -> None:
        root = Path(storage_root)
        prompt_dir = Path(__file__).parent / "prompts"
        self._prompt_loader = PromptLoader(prompt_dir)
        self._retriever: KeywordRetriever = build_retriever()

        self.config = DomainConfig(
            key="techdocs_pack",
            display_name="Technical Documentation Pack",
            description="Authoritative API reference and technical documentation lookup with strict citation grounding.",
            system_prompt_dir=prompt_dir,
            fidelity=TECHDOCS_FIDELITY_POLICY,
            tools=(
                ToolSpec(
                    name="lookup_api_reference",
                    description="Retrieve exact API signatures, parameters, and docstrings from authoritative docs.",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "language": {"type": "string"},
                            "version": {"type": "string"},
                        },
                    },
                    authoritative=True,
                    source_scope="api_reference",
                    tags=("primary", "signature", "verbatim"),
                ),
                ToolSpec(
                    name="cross_reference_concepts",
                    description="Find related classes, methods, patterns, or design principles connected to the query.",
                    input_schema={
                        "type": "object",
                        "properties": {"seed_concept": {"type": "string"}},
                    },
                    source_scope="concept_graph",
                    tags=("cross", "reference", "related"),
                ),
                ToolSpec(
                    name="generate_example",
                    description="Produce a usage example grounded in cited API references.",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "api_name": {"type": "string"},
                            "context": {"type": "string"},
                        },
                    },
                    source_scope="example",
                    tags=("example", "usage", "grounded"),
                ),
            ),
            tool_registry=ToolRegistryConfig(max_tools_per_step=3, embedding_model="lexical-overlap"),
            rag=RAGConfig(
                enabled=True,
                corpus_path=root / "techdocs_corpus",
                top_k_retrieval=5,
                similarity_threshold=0.25,
                fidelity_mode=FidelityMode.GROUNDED,
                verbatim_sources=tuple(r["id"] for r in corpus_records()),
            ),
            memory=MemoryConfig(store_path=root / "memory", max_memory_inject=3),
            validation=ValidationConfig(max_retries=2, strict_mode=True),
            guardrails=GuardrailConfig(
                tradition_flags={
                    "language": "python",  # or "typescript", "rust", etc.
                    "framework_version": "3.11+",
                    "doc_source": "official",
                    "citation_format": "[module:class.method@version]",
                },
                require_corpus_citation=True,
                require_primary_source=True,
                partner_mode_enabled=True,
                partner_mode_triggers=("uncertain", "deprecated", "experimental", "check docs"),
            ),
            max_parallel_steps=2,
            tradition_flags={"domain": "technical_docs", "mode": "reference"},
        )

    async def run_tool(
        self,
        tool_name: str,
        instruction: str,
        arguments: Mapping[str, Any] | None = None,
    ) -> Any:
        if tool_name not in TOOLS:
            raise KeyError(f"Unknown techdocs tool: {tool_name}")
        return await TOOLS[tool_name](instruction, arguments, pack_config=self.config)

    async def retrieve_context(self, query: str, top_k: int = 5) -> list[str]:
        matches = self._retriever.search(query, top_k=top_k)
        return [item["text"] for item in matches]

    def validate_step(self, tool_name: str, output: Any) -> ValidationResult:
        return validate_techdocs_output(tool_name, output, config=self.config)

    def fidelity_audit(self, synthesis: str, citations: tuple[str, ...]) -> ValidationResult:
        issues: list[str] = []
        policy = self.config.fidelity

        if policy.require_citations and not citations:
            issues.append("Technical synthesis must include explicit API/documentation citations.")

        # Detect hallucinated parameters or non-existent methods
        if policy.mode == FidelityMode.STRICT:
            import re
            # Pattern: looks like a method call but not cited
            uncited_calls = re.findall(r"\.([a-z_]+\([^)]*\))", synthesis)
            for call in uncited_calls:
                if not any(call.split("(")[0] in cit for cit in citations):
                    issues.append(f"Uncited API usage detected: {call}")

        # Forbidden speculative language in technical docs
        for pattern in policy.forbidden_patterns:
            if re.search(pattern, synthesis, flags=re.IGNORECASE):
                issues.append(f"Forbidden pattern matched: {pattern}")

        return ValidationResult(ok=not issues, issues=tuple(issues))

    def disambiguate_intent(self, query: str) -> str:
        lowered = query.lower()
        if any(kw in lowered for kw in ("how to", "example", "usage")):
            return "User seeks a practical usage example or tutorial."
        if any(kw in lowered for kw in ("signature", "parameters", "returns", "type")):
            return "User seeks precise API signature and type information."
        if any(kw in lowered for kw in ("vs", "compare", "difference")):
            return "User seeks comparative analysis between APIs or versions."
        if "deprecated" in lowered or "removed" in lowered:
            return "User seeks migration guidance or version change notes."
        return "User seeks technical documentation reference."

    def load_prompt(self, filename: str, **variables: Any) -> str:
        return self._prompt_loader.load(filename, **variables)
