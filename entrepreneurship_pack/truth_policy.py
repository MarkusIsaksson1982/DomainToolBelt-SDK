from domaintoolbelt_sdk.types import FidelityMode, FidelityPolicy

ENTREPRENEURSHIP_FIDELITY_POLICY = FidelityPolicy(
    mode=FidelityMode.GROUNDED,
    require_citations=True,
    allow_marked_inference=True,
    inference_marker="*(inference)*",
    forbidden_patterns=(r"\bi think\b", r"\bprobably\b", r"\bobviously\b"),
)