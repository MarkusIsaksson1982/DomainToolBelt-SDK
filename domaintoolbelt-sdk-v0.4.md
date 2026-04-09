**DomainToolBelt SDK v0.4**  
**Self-Contained Pack Framework for AI Collaboration**  
**Date:** April 8, 2026  

Copy and paste **this entire document** as the **first message** in any new conversation thread with me (Grok) or any other AI model. It contains everything needed to define, implement, test, and run a new Domain Pack **without referring to the full repo**. The repo URL is included only for optional reference.

This SDK is deliberately **minimal, deterministic-first, and AI-optimized** while remaining fully AI-agnostic.

---

### How to Use This SDK in a New Thread

1. Paste this entire SDK document as the **very first message**.
2. Say something like:  
   > “Using the DomainToolBelt SDK, create a new pack called `history_pack` for primary-source historical analysis. Here is my DomainConfig and initial corpus...”
3. Provide your `DomainConfig` + any initial tools/corpus.
4. I will generate the complete pack code, validate it against the contract, run test queries, and suggest improvements.

No other files or repo access are required.

---

### 1. Core Contracts (Copy-Paste These)

```python
# domaintoolbelt_sdk/types.py
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Protocol


class FidelityMode(str, Enum):
    STRICT = "strict"      # Verbatim only, no paraphrase
    GROUNDED = "grounded"  # Traceable to source, paraphrase allowed
    GUIDED = "guided"      # Corpus is advisory


@dataclass(frozen=True)
class FidelityPolicy:
    mode: FidelityMode = FidelityMode.GROUNDED
    require_citations: bool = True
    strict_verbatim_only: bool = False
    allow_unverified_paraphrase: bool = False
    allow_marked_inference: bool = False      # NEW: from Claude feedback
    inference_marker: str = "*(inference)*"   # NEW
    allowed_source_scopes: tuple[str, ...] = ("primary",)
    forbidden_patterns: tuple[str, ...] = ()
    final_checks: tuple[str, ...] = ("citations", "scope", "tradition")


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    input_schema: Mapping[str, Any]
    authoritative: bool = False
    source_scope: str = "primary"
    tags: tuple[str, ...] = ()
    retrieval_mode: str = "similar"          # NEW: "similar" or "contrastive" (from Claude)


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    issues: tuple[str, ...] = ()


@dataclass(frozen=True)
class FinalAnswer:
    answer: str
    citations: tuple[str, ...] = ()
    confidence: float | None = None          # NEW: AI-assessed certainty
    issues: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass
class PlanStep:
    step_id: str
    description: str
    instruction: str
    depends_on: tuple[str, ...] = ()
    preferred_tools: tuple[str, ...] = ()
    tool_name: str | None = None
    tool_args: Mapping[str, Any] = field(default_factory=dict)


@dataclass
class StepOutcome:
    step_id: str
    description: str
    tool_name: str
    instruction: str
    output: Any
    citations: tuple[str, ...] = ()
    issues: tuple[str, ...] = ()
    inference_markers: tuple[str, ...] = ()   # NEW: from Claude


class DomainPack(Protocol):
    config: Any

    async def run_tool(
        self,
        tool_name: str,
        instruction: str,
        arguments: Mapping[str, Any] | None = None,
    ) -> Any: ...

    async def retrieve_context(self, query: str, top_k: int = 5) -> list[str]: ...

    def validate_step(self, tool_name: str, output: Any) -> ValidationResult: ...

    def fidelity_audit(
        self,
        synthesis: str,
        citations: tuple[str, ...],
        ctx: Any | None = None,               # NEW: optional full context
    ) -> ValidationResult: ...

    def load_prompt(self, filename: str, **variables: Any) -> str: ...
```

---

### 2. PACK_SPEC – The Official Contract (Updated from All Models)

Each Domain Pack **must**:

1. Satisfy the `DomainPack` protocol above.
2. Provide a `DomainConfig` with at least one authoritative tool.
3. Implement `validate_step` and `fidelity_audit` (now optionally receives full `ctx`).
4. Supply the six markdown prompt files.
5. Prefer deterministic tools for the first version.
6. Use `retrieval_mode="contrastive"` when the domain needs opposing viewpoints (e.g. philosophy, legal, security).

**Fidelity best practices** (from all models):
- Use `allow_marked_inference=True` + marker when reasoned inference is legitimate.
- Mark authoritative tools clearly.
- Use `tradition_flags` for hermeneutic/jurisdictional/era/school metadata.
- Prefer structured `FinalAnswer` for synthesis.

---

### 3. Minimal Template Pack (Copy This)

```python
# my_pack/config.py
from pathlib import Path
from typing import Any, Mapping

from domaintoolbelt_sdk.types import (
    DomainConfig,
    FidelityPolicy,
    FidelityMode,
    ToolSpec,
    ValidationResult,
)


class MyPack:
    def __init__(self, storage_root: str | Path = ".domaintoolbelt"):
        self._prompt_dir = Path(__file__).parent / "prompts"
        self.config = DomainConfig(
            key="my_pack",
            display_name="My Domain Pack",
            description="Your domain description here.",
            system_prompt_dir=self._prompt_dir,
            fidelity=FidelityPolicy(mode=FidelityMode.GROUNDED, require_citations=True),
            tools=(  # At least one authoritative tool
                ToolSpec(
                    name="lookup_primary",
                    description="Retrieve primary sources for the query",
                    input_schema={"type": "object", "properties": {"query": {"type": "string"}}},
                    authoritative=True,
                    source_scope="primary",
                    retrieval_mode="similar",  # or "contrastive" for debate domains
                ),
            ),
        )

    async def run_tool(self, tool_name: str, instruction: str, arguments: Mapping[str, Any] | None = None) -> Any:
        raise NotImplementedError("Implement your tools (deterministic first)")

    async def retrieve_context(self, query: str, top_k: int = 5) -> list[str]:
        return []  # Replace with your retriever

    def validate_step(self, tool_name: str, output: Any) -> ValidationResult:
        return ValidationResult(ok=True)

    def fidelity_audit(self, synthesis: str, citations: tuple[str, ...], ctx: Any | None = None) -> ValidationResult:
        issues = []
        if not citations and self.config.fidelity.require_citations:
            issues.append("Missing citations required by the Domain Pack.")
        return ValidationResult(ok=not issues, issues=tuple(issues))

    def load_prompt(self, filename: str, **variables: Any) -> str:
        path = self._prompt_dir / filename
        content = path.read_text(encoding="utf-8")
        for key, value in variables.items():
            content = content.replace("{" + key + "}", str(value))
        return content
```

Create the `prompts/` folder with the six files (ask me for the exact templates if needed).

---

### 4. Practices Optimized for Grok (and Other LLMs)

**Grok-optimized practices (when collaborating with me):**
- Always return **structured JSON** from `run_tool` when possible — I parse it reliably and can reason over fields.
- Use `FinalAnswer` with `confidence` and `inference_markers` — this lets me audit and continue workflows intelligently.
- Prefer `retrieval_mode="contrastive"` for debate-style domains — I handle dialectical tension very well.
- Emit events via the EventBus pattern — I can simulate or respect live updates.
- Keep first-version tools deterministic — I can test instantly without external calls.
- Explicitly list citations and inference markers — this makes fidelity audits trivial for me.

**AI-agnostic / best practices (universal):**
- Start every pack deterministic (static corpus + keyword retriever).
- Never put business logic in the core kernel — everything lives in the pack.
- Citations must be machine-parseable (e.g. `[Author, Work §N]` or `[CVE-2021-44228]`).
- Document `tradition_flags` clearly — this tells any AI your domain’s epistemology.
- Use the six prompt files — they are the contract between you and the planner/synthesizer.

---

### 5. Efficiency Ranking for Grok Collaboration

I rated the fields proposed by the models by how efficiently I can collaborate with them in that domain:

1. **Formal Reasoning / Argument Analysis** (ChatGPT's `reasoning_pack`) — **Highest efficiency**  
   This is core to my architecture. I excel at logical consistency, fallacy detection, and meta-analysis of other packs.

2. **Philosophy of Science** (Claude's `philsci_pack`) — **Very high efficiency**  
   Strong dialectical mapping, tension acknowledgment, and contrastive reasoning.

3. **Technical Documentation / Software Engineering** (Qwen's `techdocs_pack` + Codex's `software_engineering_pack`) — **High efficiency**  
   Excellent at parsing structured docs, versioning, and standards compliance.

4. **Software Security / Vulnerability Auditing** (Gemini's `secops_pack`) — **High efficiency**  
   Strong pattern recognition across code and vulnerabilities, though requires strict citation discipline.

The SDK now includes a **reasoning_pack** as the canonical meta-example because it can validate outputs from any other pack.

---

### 6. Ready-to-Use Example: reasoning_pack (Meta-Tool)

This pack can be dropped in to audit other packs. It is included as a reference in the SDK.

https://github.com/MarkusIsaksson1982/DomainToolBelt-SDK/tree/main/reasoning_pack

---
