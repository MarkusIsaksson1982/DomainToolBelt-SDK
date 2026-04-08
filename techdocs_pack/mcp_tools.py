# techdocs_pack/mcp_tools.py
from __future__ import annotations
import re
from typing import Any, Mapping

from domaintoolbelt.core.types import DomainConfig, ToolResult
from domaintoolbelt.rag.retriever import KeywordRetriever


# Sample corpus: replace with real docs ingestion pipeline
_CORPUS = [
    {
        "id": "[requests:Session.request@2.31.0]",
        "text": "[requests:Session.request@2.31.0] def request(method, url, **kwargs) -> Response. Sends an HTTP request. Parameters: method (str), url (str), params, data, headers, cookies, files, auth, timeout, allow_redirects, proxies, verify, cert, json. Returns: Response object.",
    },
    {
        "id": "[requests:Response@2.31.0]",
        "text": "[requests:Response@2.31.0] class Response. Represents the server's response. Attributes: status_code, headers, text, content, json(), ok, raise_for_status().",
    },
    {
        "id": "[PEP8:indentation@2023]",
        "text": "[PEP8:indentation@2023] Use 4 spaces per indentation level. Never mix tabs and spaces.",
    },
    {
        "id": "[typing:Optional@3.11]",
        "text": "[typing:Optional@3.11] Optional[X] is equivalent to Union[X, None]. Used to indicate a parameter or return value may be None.",
    },
]

_CROSS_REFS = {
    "[requests:Session.request@2.31.0]": (
        "[requests:Response@2.31.0]",
        "[typing:Optional@3.11]",
    ),
    "[PEP8:indentation@2023]": ("[PEP8:whitespace@2023]",),
}


def build_retriever() -> KeywordRetriever:
    records = [{"id": r["id"], "text": r["text"]} for r in _CORPUS]
    return KeywordRetriever(records)


def corpus_records() -> list[dict[str, str]]:
    return [{"id": r["id"], "text": r["text"]} for r in _CORPUS]


def _extract_query(instruction: str, arguments: Mapping[str, Any] | None) -> str:
    if arguments:
        for key in ("query", "seed_concept", "api_name", "context"):
            if arguments.get(key):
                return str(arguments[key])
    return instruction


def _parse_citation(text: str) -> str | None:
    """Extract citation like [module:path@version] from text."""
    match = re.search(r"\[([\w.:@\-\s/]+)\]", text)
    return match.group(1) if match else None


async def lookup_api_reference(
    instruction: str,
    arguments: Mapping[str, Any] | None = None,
    pack_config: DomainConfig | None = None,
) -> ToolResult:
    """Retrieve exact API signature and documentation."""
    query = _extract_query(instruction, arguments)
    lang = pack_config.guardrails.tradition_flags.get("language", "python") if pack_config else "python"

    matches = build_retriever().search(f"{lang} {query}", top_k=3)
    citations = tuple(_parse_citation(m["text"]) for m in matches if _parse_citation(m["text"]))

    # Extract structured fields from matched docs
    signatures = []
    parameters = []
    for m in matches:
        text = m["text"]
        # Simple parsing: "def name(...) -> Ret" or "class Name"
        sig_match = re.search(r"(def|class)\s+\w+[^(]*\([^)]*\)(?:\s*->\s*\w+)?", text)
        if sig_match:
            signatures.append(sig_match.group(0))
        # Extract params from "Parameters: a, b, c"
        params_match = re.search(r"Parameters:\s*([^.]+)", text)
        if params_match:
            parameters.extend(p.strip() for p in params_match.group(1).split(","))

    summary = f"API reference for '{query}': " + "; ".join(signatures or ["No exact signature found."])

    return ToolResult(
        content={
            "summary": summary,
            "signatures": signatures,
            "parameters": list(set(parameters)),
            "citations": citations,
        },
        citations=citations,
        metadata={"source_scope": "api_reference", "language": lang},
    )


async def cross_reference_concepts(
    instruction: str,
    arguments: Mapping[str, Any] | None = None,
    pack_config: DomainConfig | None = None,
) -> ToolResult:
    """Find related concepts, classes, or patterns."""
    seed = _extract_query(instruction, arguments)
    seed_cit = _parse_citation(seed) or seed

    related = _CROSS_REFS.get(seed_cit, [])
    if not related and "request" in seed.lower():
        related = ["[requests:Response@2.31.0]", "[typing:Optional@3.11]"]

    rendered = [f"{ref}: {_lookup_text(ref)}" for ref in related]
    citations = tuple(related)
    summary = f"Related to '{seed}': " + "; ".join(r.split(":")[0] for r in rendered)

    return ToolResult(
        content={"summary": summary, "related_concepts": rendered, "citations": citations},
        citations=citations,
        metadata={"source_scope": "concept_graph"},
    )


async def generate_example(
    instruction: str,
    arguments: Mapping[str, Any] | None = None,
    pack_config: DomainConfig | None = None,
) -> ToolResult:
    """Generate a usage example grounded in cited references."""
    api_name = arguments.get("api_name", _extract_query(instruction, arguments)) if arguments else _extract_query(instruction, arguments)
    context = str(arguments.get("context", "")) if arguments else ""

    # Find matching API reference
    matches = build_retriever().search(api_name, top_k=1)
    if not matches:
        return ToolResult(
            content={"summary": f"No reference found for '{api_name}'", "example_code": "", "citations": ()},
            citations=(),
            issues=(f"API '{api_name}' not found in corpus",),
        )

    ref = matches[0]
    citation = _parse_citation(ref["text"]) or ref["id"]

    # Generate deterministic example based on signature
    sig_match = re.search(r"def\s+(\w+)\(([^)]*)\)", ref["text"])
    if sig_match:
        func_name, params = sig_match.groups()
        param_names = [p.strip().split(":")[0].split("=")[0] for p in params.split(",") if p.strip()]
        example_args = ", ".join(f"{p}='value'" for p in param_names[:3]) or ""
        example_code = f"# Example usage of {citation}\nresult = {func_name}({example_args})\nprint(result)"
    else:
        example_code = f"# Example for {citation}\n# See documentation for usage details"

    summary = f"Grounded example for {citation}"
    citations = (citation,)

    return ToolResult(
        content={
            "summary": summary,
            "example_code": example_code,
            "citations": citations,
            "api_reference": ref["text"],
        },
        citations=citations,
        metadata={"source_scope": "example", "generated": True},
    )


TOOLS = {
    "lookup_api_reference": lookup_api_reference,
    "cross_reference_concepts": cross_reference_concepts,
    "generate_example": generate_example,
}


def _lookup_text(citation: str) -> str:
    for record in _CORPUS:
        if record["id"] == citation or citation in record["text"]:
            return record["text"]
    return "Reference text placeholder."
