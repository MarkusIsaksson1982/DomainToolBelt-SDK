from domaintoolbelt_sdk.types import ToolResult


_CORPUS = [
    {"id": "Adam Smith - Invisible Hand", "text": "[Adam Smith, Wealth of Nations] The invisible hand leads individuals pursuing self-interest to promote societal prosperity."},
    {"id": "Hayek - Knowledge Problem", "text": "[Hayek, Use of Knowledge in Society] Centralized planning fails because knowledge is dispersed and local."},
    {"id": "Schumpeter - Creative Destruction", "text": "[Schumpeter] Innovation drives prosperity through creative destruction of old industries."},
    {"id": "Locke - Property Rights", "text": "[John Locke] Secure property rights are the foundation of liberty and prosperity."},
    {"id": "Milton Friedman - Free to Choose", "text": "[Milton Friedman] Economic freedom is essential for political freedom and prosperity."},
    {"id": "Cowen - Great Stagnation", "text": "[Tyler Cowen] Easy growth is over; future prosperity depends on high-hanging fruit and innovation."},
    {"id": "Thiel - Zero to One", "text": "[Peter Thiel] True progress comes from creating new things (0 to 1) rather than copying (1 to n)."},
    {"id": "Hayek - Spontaneous Order", "text": "[Hayek] Complex systems emerge from spontaneous order, not central planning."},
    {"id": "Smith - Division of Labor", "text": "[Adam Smith] Division of labor increases productivity and wealth."},
    {"id": "Friedman - Monetarism", "text": "[Milton Friedman] Inflation is always and everywhere a monetary phenomenon."},
]

_CROSS_REFS = {
    "Adam Smith - Invisible Hand": ["Hayek - Knowledge Problem", "Friedman - Free to Choose"],
    "Hayek - Knowledge Problem": ["Adam Smith - Invisible Hand", "Schumpeter - Creative Destruction"],
    "Schumpeter - Creative Destruction": ["Hayek - Spontaneous Order", "Thiel - Zero to One"],
    "Locke - Property Rights": ["Milton Friedman - Free to Choose", "Hayek - Knowledge Problem"],
    "Cowen - Great Stagnation": ["Thiel - Zero to One", "Schumpeter - Creative Destruction"],
    "Thiel - Zero to One": ["Cowen - Great Stagnation", "Schumpeter - Creative Destruction"],
}


class KeywordRetriever:
    def __init__(self, records):
        self._records = records

    def search(self, query: str, top_k: int = 5):
        query_terms = set(query.lower().split())
        results = []
        for record in self._records:
            text = record["text"].lower()
            score = sum(1 for term in query_terms if term in text)
            if score > 0:
                results.append({"id": record["id"], "text": record["text"], "score": score})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]


def build_retriever():
    records = [{"id": r["id"], "text": r["text"]} for r in _CORPUS]
    return KeywordRetriever(records)


async def lookup_principle(query: str) -> dict:
    retriever = build_retriever()
    matches = retriever.search(query, top_k=5)
    return {
        "principles": [{"id": m["id"], "text": m["text"]} for m in matches],
        "citations": tuple(m["id"] for m in matches),
    }


async def cross_reference_thinkers(seed: str) -> dict:
    matches = build_retriever().search(seed, top_k=1)
    if not matches:
        return {"references": [], "citations": ()}
    seed_id = matches[0]["id"]
    references = _CROSS_REFS.get(seed_id, [])
    return {
        "references": references,
        "citations": (seed_id,),
    }


async def evaluate_policy_impact(policy: str) -> dict:
    policy_lower = policy.lower()
    issues = []
    if any(word in policy_lower for word in ["tax", "subsidy", "regulation", "control", "central"]):
        issues.append("Review: policy may interfere with price signals *(inference)*")
    if "property" in policy_lower and "right" in policy_lower:
        issues.append("Property rights protection supports prosperity")
    return {
        "impact_assessment": issues if issues else ["Policy appears neutral on prosperity *(inference)*"],
        "citations": ("Locke - Property Rights", "Hayek - Knowledge Problem"),
    }