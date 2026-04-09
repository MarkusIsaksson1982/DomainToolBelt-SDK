from domaintoolbelt_sdk.types import FidelityMode, FidelityPolicy

REASONING_FIDELITY_POLICY = FidelityPolicy(
    mode=FidelityMode.GROUNDED,
    require_citations=False,
    allow_marked_inference=True,
    inference_marker="*(inference)*",
    forbidden_patterns=(r"\bi think\b", r"\bprobably\b", r"\bobviously\b", r"\bself-evident\b"),
    final_checks=("citations", "inference_markers", "consistency"),
)
