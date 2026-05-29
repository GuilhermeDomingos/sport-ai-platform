from statistics import mean, pstdev
from typing import Any

from app.modules.scoring.classification import classify_score
from app.modules.scoring.components import clamp_score, score_status, weighted_score
from app.modules.scoring.config import (
    LOW_CONFIDENCE_WARNING,
    MIN_CONFIDENCE_TO_SCORE,
    SCORE_METHOD,
    SCORE_VERSION,
    SCORE_WEIGHTS,
    FRONTAL_SCORE_TYPE,
)
from app.modules.scoring.schemas import ScoreComponent, ScoreDetail, ScoreResult, ScoringInput


DEPTH_SCORES = {
    "below_parallel": 95,
    "parallel": 82,
    "above_parallel": 55,
}


def _metric(metrics: dict[str, Any], name: str, default: float = 0.0) -> float:
    value = metrics.get(name, default)
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _depth_score(metrics: dict[str, Any]) -> int:
    if "squat_depth" in metrics:
        return clamp_score(_metric(metrics, "squat_depth") * 100)
    return DEPTH_SCORES.get(metrics.get("depthClassification"), 55)


def _range_score(value: float, ideal: float, attention: float, low: float) -> int:
    if value <= ideal:
        return 95
    if value <= attention:
        return 85 - ((value - ideal) / (attention - ideal)) * 20
    if value <= low:
        return 65 - ((value - attention) / (low - attention)) * 25
    return 35


def _component(
    name: str,
    score: int,
    weight: float,
    details: list[ScoreDetail],
    confidence_component: bool = False,
) -> ScoreComponent:
    return ScoreComponent(
        name=name,
        score=clamp_score(score),
        weight=weight,
        status=score_status(score, confidence_component=confidence_component),
        details=details,
    )


def _rep_values(reps: list[dict[str, Any]], name: str) -> list[float]:
    values: list[float] = []
    for rep in reps:
        try:
            values.append(float(rep[name]))
        except (KeyError, TypeError, ValueError):
            continue
    return values


def calculate_squat_mobility_score(metrics: dict[str, Any]) -> ScoreComponent:
    weights = SCORE_WEIGHTS["squat"]
    depth = _depth_score(metrics)
    knee = _range_score(_metric(metrics, "minKneeAngle", 180), 95, 120, 145)
    hip = _range_score(_metric(metrics, "averageHipAngle", 180), 120, 145, 165)
    torso = _range_score(_metric(metrics, "torsoInclination", 90), 15, 30, 45)
    score = weighted_score(
        [(depth, 0.40), (knee, 0.25), (hip, 0.20), (torso, 0.15)]
    )
    return _component(
        "mobility",
        score,
        weights["mobility"],
        [
            ScoreDetail(
                metric="squat_depth",
                value=metrics.get("depthClassification", metrics.get("squat_depth")),
                status=score_status(depth),
                message="Profundidade avaliada a partir da posicao do quadril em relacao aos joelhos.",
            ),
            ScoreDetail(
                metric="min_knee_angle",
                value=metrics.get("minKneeAngle"),
                status=score_status(knee),
                message="Menor angulo de joelho usado como sinal de amplitude.",
            ),
            ScoreDetail(
                metric="average_hip_angle",
                value=metrics.get("averageHipAngle"),
                status=score_status(hip),
                message="Angulo medio de quadril usado para estimar mobilidade global.",
            ),
            ScoreDetail(
                metric="torso_inclination",
                value=metrics.get("torsoInclination"),
                status=score_status(torso),
                message="Inclinacao de tronco avaliada dentro de uma faixa tecnica aceitavel.",
            ),
        ],
    )


def calculate_squat_stability_score(
    metrics: dict[str, Any], reps: list[dict[str, Any]] | None = None
) -> ScoreComponent:
    weights = SCORE_WEIGHTS["squat"]
    rep_scores = _rep_values(reps or [], "stabilityScore")
    base = mean(rep_scores) if rep_scores else _metric(metrics, "stabilityScore", 0)
    variation_penalty = pstdev(rep_scores) if len(rep_scores) > 1 else 0
    score = clamp_score(base - variation_penalty * 0.5)
    return _component(
        "stability",
        score,
        weights["stability"],
        [
            ScoreDetail(
                metric="stability_score",
                value=round(base, 2),
                status=score_status(score),
                message="Estabilidade estimada pela variacao da trajetoria dos joelhos.",
            )
        ],
    )


def calculate_squat_symmetry_score(
    metrics: dict[str, Any], reps: list[dict[str, Any]] | None = None
) -> ScoreComponent:
    weights = SCORE_WEIGHTS["squat"]
    rep_scores = _rep_values(reps or [], "symmetryScore")
    base = mean(rep_scores) if rep_scores else _metric(metrics, "symmetryScore", 0)
    variation_penalty = pstdev(rep_scores) * 0.3 if len(rep_scores) > 1 else 0
    score = clamp_score(base - variation_penalty)
    return _component(
        "symmetry",
        score,
        weights["symmetry"],
        [
            ScoreDetail(
                metric="symmetry_score",
                value=round(base, 2),
                status=score_status(score),
                message="Simetria estimada pelas diferencas entre lado esquerdo e direito.",
            )
        ],
    )


def calculate_squat_motor_control_score(
    metrics: dict[str, Any], reps: list[dict[str, Any]] | None = None
) -> ScoreComponent:
    weights = SCORE_WEIGHTS["squat"]
    reps = reps or []
    if not reps:
        consistency = 35
        smoothness = clamp_score((_metric(metrics, "stabilityScore", 0) + _metric(metrics, "symmetryScore", 0)) / 2)
    elif len(reps) == 1:
        consistency = 85
        smoothness = clamp_score(reps[0].get("stabilityScore", 0))
    else:
        knee_angles = _rep_values(reps, "minKneeAngle")
        velocities = _rep_values(reps, "averageVelocity")
        stability = _rep_values(reps, "stabilityScore")
        consistency = clamp_score(
            100
            - (pstdev(knee_angles) * 2 if len(knee_angles) > 1 else 0)
            - (pstdev(stability) if len(stability) > 1 else 0)
        )
        smoothness = clamp_score(
            100 - (pstdev(velocities) * 0.5 if len(velocities) > 1 else 0)
        )

    bottom_control = clamp_score(_metric(metrics, "stabilityScore", smoothness))
    rhythm = clamp_score(100 - abs(_metric(metrics, "averageVelocity", 20) - 20))
    compensation = clamp_score((bottom_control + smoothness) / 2)
    score = weighted_score(
        [
            (consistency, 0.30),
            (smoothness, 0.25),
            (bottom_control, 0.20),
            (rhythm, 0.15),
            (compensation, 0.10),
        ]
    )
    return _component(
        "motor_control",
        score,
        weights["motor_control"],
        [
            ScoreDetail(
                metric="rep_consistency",
                value=consistency,
                status=score_status(consistency),
                message="Consistencia estimada pela variacao entre repeticoes detectadas.",
            ),
            ScoreDetail(
                metric="movement_smoothness",
                value=smoothness,
                status=score_status(smoothness),
                message="Suavidade estimada pela estabilidade e pela variacao de velocidade.",
            ),
        ],
    )


def calculate_squat_analysis_confidence_score(
    metrics: dict[str, Any], pose_quality: dict[str, Any] | None = None
) -> ScoreComponent:
    weights = SCORE_WEIGHTS["squat"]
    pose_quality = pose_quality or {}
    valid_frames = clamp_score(float(pose_quality.get("valid_pose_frame_ratio", 1.0)) * 100)
    avg_visibility = clamp_score(float(pose_quality.get("average_landmark_visibility", 0.85)) * 100)
    critical_visibility = clamp_score(
        float(pose_quality.get("critical_landmark_visibility_ratio", 1.0)) * 100
    )
    valid_reps = int(pose_quality.get("valid_reps", 0))
    rep_score = 100 if valid_reps >= 2 else 70 if valid_reps == 1 else 35
    score = weighted_score(
        [
            (valid_frames, 0.35),
            (avg_visibility, 0.30),
            (critical_visibility, 0.20),
            (rep_score, 0.15),
        ]
    )
    return _component(
        "analysis_confidence",
        score,
        weights["analysis_confidence"],
        [
            ScoreDetail(
                metric="valid_pose_frames",
                value=pose_quality.get("valid_pose_frame_ratio"),
                status=score_status(valid_frames, confidence_component=True),
                message="Percentual de frames com pose detectada.",
            ),
            ScoreDetail(
                metric="average_landmark_visibility",
                value=pose_quality.get("average_landmark_visibility"),
                status=score_status(avg_visibility, confidence_component=True),
                message="Visibilidade media dos landmarks usados na analise.",
            ),
            ScoreDetail(
                metric="valid_reps",
                value=valid_reps,
                status=score_status(rep_score, confidence_component=True),
                message="Quantidade de repeticoes completas detectadas.",
            ),
        ],
        confidence_component=True,
    )


def _recommendations_for_components(components: list[ScoreComponent]) -> list[str]:
    by_name = {component.name: component for component in components}
    recommendations: list[str] = []
    if by_name["mobility"].score < 70:
        recommendations.append(
            "Aumente a amplitude do agachamento de forma progressiva e controlada."
        )
    if by_name["stability"].score < 70:
        recommendations.append(
            "Mantenha o tronco e os joelhos mais estaveis durante descida e subida."
        )
    if by_name["symmetry"].score < 70:
        recommendations.append(
            "Observe o alinhamento dos joelhos e reduza compensacoes entre os lados."
        )
    if by_name["motor_control"].score < 70:
        recommendations.append(
            "Use um ritmo mais constante para preservar controle tecnico ate o fim da serie."
        )
    if by_name["analysis_confidence"].score < LOW_CONFIDENCE_WARNING:
        recommendations.append(
            "Grave novamente com pes, joelhos, quadril e ombros visiveis durante todo o movimento."
        )
    return recommendations


def _summary(final_score: int | None, components: list[ScoreComponent]) -> str:
    if final_score is None:
        return "Nao foi possivel gerar um score confiavel com este video."

    weakest = min(
        [component for component in components if component.name != "analysis_confidence"],
        key=lambda component: component.score,
    )
    labels = {
        "mobility": "mobilidade",
        "stability": "estabilidade",
        "symmetry": "simetria",
        "motor_control": "controle motor",
    }
    return (
        "AXON Movement Score calculado por sub-scores. "
        f"O principal ponto de atencao foi {labels.get(weakest.name, weakest.name)}."
    )


def calculate_squat_score(scoring_input: ScoringInput) -> ScoreResult:
    metrics = scoring_input.metrics
    weights = SCORE_WEIGHTS["squat"]
    mobility = calculate_squat_mobility_score(metrics)
    stability = calculate_squat_stability_score(metrics, scoring_input.reps)
    symmetry = calculate_squat_symmetry_score(metrics, scoring_input.reps)
    motor_control = calculate_squat_motor_control_score(metrics, scoring_input.reps)
    confidence = calculate_squat_analysis_confidence_score(
        metrics, scoring_input.pose_quality
    )
    components = [mobility, stability, symmetry, motor_control, confidence]

    warnings: list[str] = []
    if confidence.score < LOW_CONFIDENCE_WARNING:
        warnings.append(
            "A analise pode estar limitada porque a deteccao corporal ou o enquadramento ficaram abaixo do ideal."
        )

    if confidence.score < MIN_CONFIDENCE_TO_SCORE:
        final_score = None
        movement_quality_score = None
    else:
        movement_quality_score = weighted_score(
            [
                (mobility.score, weights["mobility"]),
                (stability.score, weights["stability"]),
                (symmetry.score, weights["symmetry"]),
                (motor_control.score, weights["motor_control"]),
            ]
        )
        final_score = weighted_score(
            [
                (mobility.score, weights["mobility"]),
                (stability.score, weights["stability"]),
                (symmetry.score, weights["symmetry"]),
                (motor_control.score, weights["motor_control"]),
                (confidence.score, weights["analysis_confidence"]),
            ]
        )

    classification = classify_score(final_score, confidence.score)
    recommendations = _recommendations_for_components(components)
    if final_score is None:
        warnings.append(
            "A qualidade do video ou a deteccao corporal nao foram suficientes para gerar um score confiavel."
        )

    return ScoreResult(
        final_score=final_score,
        movement_quality_score=movement_quality_score,
        analysis_confidence=confidence.score,
        classification=classification,
        summary=_summary(final_score, components),
        components=components,
        warnings=list(dict.fromkeys(warnings)),
        recommendations=list(dict.fromkeys(recommendations)),
        score_method=SCORE_METHOD,
        score_type=FRONTAL_SCORE_TYPE,
        score_version=SCORE_VERSION,
        sub_scores={component.name: component.score for component in components},
    )
