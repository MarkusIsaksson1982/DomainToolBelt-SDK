# techdocs_pack/truth_policy.py
from domaintoolbelt.core.types import FidelityMode, FidelityPolicy

TECHDOCS_FIDELITY_POLICY = FidelityPolicy(
    mode=FidelityMode.GROUNDED,  # Paraphrase allowed for explanations, but citations mandatory
    require_citations=True,
    strict_verbatim_only=False,  # Allow explanatory paraphrase of doc content
    allow_unverified_paraphrase=False,  # But never invent API behavior
    allowed_source_scopes=("api_reference", "concept_graph", "example", "changelog"),
    forbidden_patterns=(
        r"\b(i think|maybe|perhaps|probably|aFAIK)\b",  # No speculation about APIs
        r"\bshould work\b",  # Avoid untested claims
        r"\blikely returns\b",  # Be definitive or cite uncertainty
    ),
    final_checks=("citations", "scope", "tradition", "parameter_accuracy"),
)
