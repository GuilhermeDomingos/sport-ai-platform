from collections.abc import Iterable

from app.modules.scoring.schemas import ScoreComponent


def clamp_score(value: float | int) -> int:
    return round(max(0.0, min(100.0, float(value))))


def weighted_score(items: Iterable[tuple[int | float, float]]) -> int:
    weighted_sum = 0.0
    total_weight = 0.0
    for score, weight in items:
        weighted_sum += clamp_score(score) * weight
        total_weight += weight

    if total_weight <= 0:
        return 0
    return clamp_score(weighted_sum / total_weight)


def score_status(score: int, confidence_component: bool = False) -> str:
    if confidence_component:
        if score >= 80:
            return "reliable"
        if score >= 60:
            return "acceptable"
        if score >= 40:
            return "limited"
        return "critical"

    if score >= 85:
        return "excellent"
    if score >= 70:
        return "good"
    if score >= 50:
        return "attention"
    if score >= 30:
        return "low"
    return "critical"


def component_by_name(
    components: list[ScoreComponent], name: str
) -> ScoreComponent | None:
    return next((component for component in components if component.name == name), None)
