from statistics import mean, pstdev
from typing import Any

from app.modules.scoring.classification import classify_score
from app.modules.scoring.components import clamp_score, score_status, weighted_score
from app.modules.scoring.config import (
    LATERAL_SCORE_TYPE,
    LOW_CONFIDENCE_WARNING,
    MIN_CONFIDENCE_TO_SCORE,
    SCORE_CONFIG,
    SCORE_VERSION,
)
from app.modules.scoring.schemas import ScoreComponent, ScoreDetail, ScoreResult, ScoringInput
from app.schemas.camera_schema import CameraViewValidationResult, CameraViewValidationStatus


WEIGHTS = SCORE_CONFIG[("squat", "side")]["weights"]


def _metric(metrics: dict[str, Any], name: str, default: float = 0.0) -> float:
    value = metrics.get(name, default)
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _component(
    name: str,
    score: int,
    details: list[ScoreDetail],
    confidence_component: bool = False,
) -> ScoreComponent:
    return ScoreComponent(
        name=name,
        score=clamp_score(score),
        weight=WEIGHTS[name],
        status=score_status(score, confidence_component=confidence_component),
        details=details,
    )


def _range_score(value: float, ideal_max: float, attention_max: float, low_max: float) -> int:
    if value <= ideal_max:
        return 95
    if value <= attention_max:
        return clamp_score(85 - ((value - ideal_max) / (attention_max - ideal_max)) * 20)
    if value <= low_max:
        return clamp_score(65 - ((value - attention_max) / (low_max - attention_max)) * 30)
    return 30


def _minimum_angle_score(value: float, excellent: float, good: float, attention: float) -> int:
    if value <= excellent:
        return 95
    if value <= good:
        return 85
    if value <= attention:
        return 65
    return 40


def _ratio_score(value: float, excellent: float, good: float, attention: float) -> int:
    if value >= excellent:
        return 95
    if value >= good:
        return 82
    if value >= attention:
        return 62
    return 38


def _rep_values(reps: list[dict[str, Any]], name: str) -> list[float]:
    values: list[float] = []
    for rep in reps:
        try:
            values.append(float(rep[name]))
        except (KeyError, TypeError, ValueError):
            continue
    return values


def calculate_amplitude_depth_score(metrics: dict[str, Any]) -> ScoreComponent:
    depth_ratio = _metric(metrics, "squat_depth_ratio", 0.0)
    min_knee = _metric(metrics, "minKneeAngle", 180)
    min_hip = _metric(metrics, "min_hip_angle", _metric(metrics, "averageHipAngle", 180))
    displacement = _metric(metrics, "hip_vertical_displacement", 0.0)
    rom = _metric(metrics, "range_of_motion", 0.0)
    depth_score = _ratio_score(depth_ratio, 0.82, 0.68, 0.50)
    knee_score = _minimum_angle_score(min_knee, 95, 115, 135)
    hip_score = _minimum_angle_score(min_hip, 95, 120, 145)
    displacement_score = _ratio_score(displacement, 0.16, 0.10, 0.06)
    rom_score = _ratio_score(rom, 70, 55, 35)
    score = weighted_score(
        [
            (depth_score, 0.35),
            (knee_score, 0.25),
            (hip_score, 0.15),
            (displacement_score, 0.15),
            (rom_score, 0.10),
        ]
    )
    return _component(
        "amplitude_depth",
        score,
        [
            ScoreDetail(
                metric="squat_depth",
                value=metrics.get("squat_depth_ratio"),
                status=score_status(depth_score),
                message="Profundidade avaliada pelo deslocamento lateral do quadril e flexao do joelho.",
            ),
            ScoreDetail(
                metric="min_knee_angle",
                value=metrics.get("minKneeAngle"),
                status=score_status(knee_score),
                message="Menor angulo de joelho usado como indicador de amplitude.",
            ),
        ],
    )


def calculate_joint_kinematics_score(metrics: dict[str, Any]) -> ScoreComponent:
    knee_rom = _metric(metrics, "knee_rom", 0.0)
    hip_rom = _metric(metrics, "hip_rom", 0.0)
    min_knee = _metric(metrics, "minKneeAngle", 180)
    min_hip = _metric(metrics, "min_hip_angle", _metric(metrics, "averageHipAngle", 180))
    coordination_gap = abs(knee_rom - hip_rom)
    knee_rom_score = _ratio_score(knee_rom, 80, 60, 40)
    hip_rom_score = _ratio_score(hip_rom, 65, 50, 35)
    knee_angle_score = _minimum_angle_score(min_knee, 95, 115, 135)
    hip_angle_score = _minimum_angle_score(min_hip, 95, 120, 145)
    coordination_score = clamp_score(100 - coordination_gap * 0.5)
    score = weighted_score(
        [
            (knee_rom_score, 0.25),
            (hip_rom_score, 0.25),
            (knee_angle_score, 0.20),
            (hip_angle_score, 0.20),
            (coordination_score, 0.10),
        ]
    )
    return _component(
        "joint_kinematics",
        score,
        [
            ScoreDetail(
                metric="knee_rom",
                value=metrics.get("knee_rom"),
                status=score_status(knee_rom_score),
                message="Amplitude angular do joelho durante o agachamento lateral.",
            ),
            ScoreDetail(
                metric="hip_rom",
                value=metrics.get("hip_rom"),
                status=score_status(hip_rom_score),
                message="Amplitude angular do quadril durante o movimento.",
            ),
        ],
    )


def calculate_trunk_posture_score(metrics: dict[str, Any]) -> ScoreComponent:
    bottom = _metric(metrics, "bottom_trunk_inclination", _metric(metrics, "torsoInclination", 45))
    maximum = _metric(metrics, "max_trunk_inclination", bottom)
    variation = _metric(metrics, "trunk_variation", 0)
    bottom_score = _range_score(bottom, 25, 40, 55)
    max_score = _range_score(maximum, 35, 50, 65)
    variation_score = _range_score(variation, 6, 12, 22)
    score = weighted_score(
        [(bottom_score, 0.45), (max_score, 0.30), (variation_score, 0.25)]
    )
    return _component(
        "trunk_posture",
        score,
        [
            ScoreDetail(
                metric="bottom_trunk_inclination",
                value=metrics.get("bottom_trunk_inclination"),
                status=score_status(bottom_score),
                message="Inclinacao do tronco no ponto mais baixo, sem penalizar inclinacao moderada.",
            ),
            ScoreDetail(
                metric="trunk_variation",
                value=metrics.get("trunk_variation"),
                status=score_status(variation_score),
                message="Estabilidade da linha ombro-quadril ao longo do movimento.",
            ),
        ],
    )


def calculate_lateral_motor_control_score(
    metrics: dict[str, Any], reps: list[dict[str, Any]] | None = None
) -> ScoreComponent:
    reps = reps or []
    velocities = _rep_values(reps, "averageVelocity")
    durations = _rep_values(reps, "durationFrames")
    min_angles = _rep_values(reps, "minKneeAngle")
    smoothness = clamp_score(_metric(metrics, "movement_smoothness", 70))
    bottom_control = clamp_score(_metric(metrics, "bottom_control", 70))
    consistency = 85
    if len(reps) > 1:
        consistency = clamp_score(
            100
            - (pstdev(min_angles) * 2 if len(min_angles) > 1 else 0)
            - (pstdev(velocities) * 0.5 if len(velocities) > 1 else 0)
            - (pstdev(durations) * 0.15 if len(durations) > 1 else 0)
        )
    elif not reps:
        consistency = 45

    rhythm = clamp_score(100 - abs((mean(velocities) if velocities else 22) - 22))
    score = weighted_score(
        [
            (smoothness, 0.30),
            (bottom_control, 0.30),
            (consistency, 0.25),
            (rhythm, 0.15),
        ]
    )
    return _component(
        "motor_control",
        score,
        [
            ScoreDetail(
                metric="movement_smoothness",
                value=metrics.get("movement_smoothness"),
                status=score_status(smoothness),
                message="Fluidez estimada pela trajetoria lateral do quadril.",
            ),
            ScoreDetail(
                metric="bottom_control",
                value=metrics.get("bottom_control"),
                status=score_status(bottom_control),
                message="Controle no ponto mais baixo antes da subida.",
            ),
        ],
    )


def calculate_lateral_analysis_confidence_score(
    metrics: dict[str, Any],
    reps: list[dict[str, Any]] | None = None,
    camera_view_validation: CameraViewValidationResult | None = None,
) -> ScoreComponent:
    reps = reps or []
    valid_frames = clamp_score(_metric(metrics, "valid_pose_frame_ratio", 0) * 100)
    side_confidence = clamp_score(
        _metric(metrics, "visible_side_landmark_confidence", 0) * 100
    )
    critical = clamp_score(
        _metric(metrics, "critical_landmarks_visible_ratio", 0) * 100
    )
    rep_score = 100 if len(reps) >= 2 else 75 if len(reps) == 1 else 35
    camera_view_score = 100
    if camera_view_validation is not None:
        camera_view_score = (
            min(camera_view_validation.confidence, 60)
            if camera_view_validation.status is CameraViewValidationStatus.UNCERTAIN
            else camera_view_validation.confidence
        )
    score = weighted_score(
        [
            (valid_frames, 0.30),
            (side_confidence, 0.25),
            (critical, 0.20),
            (rep_score, 0.05),
            (camera_view_score, 0.20),
        ]
    )
    return _component(
        "analysis_confidence",
        score,
        [
            ScoreDetail(
                metric="valid_pose_frame_ratio",
                value=metrics.get("valid_pose_frame_ratio"),
                status=score_status(valid_frames, confidence_component=True),
                message="Percentual de frames com pose detectada no video lateral.",
            ),
            ScoreDetail(
                metric="visible_side_landmark_confidence",
                value=metrics.get("visible_side_landmark_confidence"),
                status=score_status(side_confidence, confidence_component=True),
                message="Confianca media dos landmarks do lado mais visivel.",
            ),
            ScoreDetail(
                metric="valid_reps_count",
                value=len(reps),
                status=score_status(rep_score, confidence_component=True),
                message="Quantidade de repeticoes completas detectadas.",
            ),
            ScoreDetail(
                metric="camera_view_validation",
                value=(
                    camera_view_validation.status.value
                    if camera_view_validation is not None
                    else "not_available"
                ),
                status=score_status(camera_view_score, confidence_component=True),
                message="Confianca da validacao do angulo do video.",
            ),
        ],
        confidence_component=True,
    )


def _summary(final_score: int | None, components: list[ScoreComponent]) -> str:
    if final_score is None:
        return "Nao foi possivel gerar um score confiavel para este video lateral."

    weakest = min(
        [component for component in components if component.name != "analysis_confidence"],
        key=lambda component: component.score,
    )
    labels = {
        "amplitude_depth": "amplitude e profundidade",
        "joint_kinematics": "cinematica de joelho e quadril",
        "trunk_posture": "postura de tronco",
        "motor_control": "controle motor",
    }
    return (
        "AXON Lateral Movement Score calculado para o plano lateral. "
        f"O principal ponto de atencao foi {labels.get(weakest.name, weakest.name)}."
    )


def _recommendations_for_components(components: list[ScoreComponent]) -> list[str]:
    by_name = {component.name: component for component in components}
    recommendations: list[str] = []
    if by_name["amplitude_depth"].score < 70:
        recommendations.append(
            "Busque maior profundidade mantendo controle durante toda a descida."
        )
    if by_name["joint_kinematics"].score < 70:
        recommendations.append(
            "Trabalhe uma flexao mais coordenada de joelho e quadril no agachamento."
        )
    if by_name["trunk_posture"].score < 70:
        recommendations.append(
            "Tente manter o tronco mais estavel, especialmente no ponto mais baixo."
        )
    if by_name["motor_control"].score < 70:
        recommendations.append(
            "Use um ritmo constante, com descida e subida controladas."
        )
    if by_name["analysis_confidence"].score < LOW_CONFIDENCE_WARNING:
        recommendations.append(
            "Grave novamente de lado, com ombro, quadril, joelho, tornozelo e pe visiveis."
        )
    return recommendations


def calculate_squat_side_score(scoring_input: ScoringInput) -> ScoreResult:
    metrics = scoring_input.metrics
    amplitude_depth = calculate_amplitude_depth_score(metrics)
    joint_kinematics = calculate_joint_kinematics_score(metrics)
    trunk_posture = calculate_trunk_posture_score(metrics)
    motor_control = calculate_lateral_motor_control_score(metrics, scoring_input.reps)
    confidence = calculate_lateral_analysis_confidence_score(
        metrics, scoring_input.reps, scoring_input.camera_view_validation
    )
    components = [
        amplitude_depth,
        joint_kinematics,
        trunk_posture,
        motor_control,
        confidence,
    ]

    warnings: list[str] = []
    if confidence.score < LOW_CONFIDENCE_WARNING:
        warnings.append(
            "A analise lateral foi gerada com confianca limitada. Tente gravar novamente com o corpo inteiro visivel, principalmente ombro, quadril, joelho e tornozelo."
        )
    if (
        scoring_input.camera_view_validation is not None
        and scoring_input.camera_view_validation.status is CameraViewValidationStatus.UNCERTAIN
    ):
        warnings.extend(scoring_input.camera_view_validation.warnings)

    if confidence.score < MIN_CONFIDENCE_TO_SCORE:
        final_score = None
        movement_quality_score = None
        warnings.extend(
            [
                "O corpo nao ficou suficientemente visivel no video lateral.",
                "A analise foi limitada pela baixa confianca dos landmarks.",
            ]
        )
    else:
        movement_quality_score = weighted_score(
            [
                (amplitude_depth.score, WEIGHTS["amplitude_depth"]),
                (joint_kinematics.score, WEIGHTS["joint_kinematics"]),
                (trunk_posture.score, WEIGHTS["trunk_posture"]),
                (motor_control.score, WEIGHTS["motor_control"]),
            ]
        )
        final_score = weighted_score(
            [
                (amplitude_depth.score, WEIGHTS["amplitude_depth"]),
                (joint_kinematics.score, WEIGHTS["joint_kinematics"]),
                (trunk_posture.score, WEIGHTS["trunk_posture"]),
                (motor_control.score, WEIGHTS["motor_control"]),
                (confidence.score, WEIGHTS["analysis_confidence"]),
            ]
        )

    recommendations = _recommendations_for_components(components)
    if final_score is None:
        recommendations.extend(
            [
                "Grave novamente com o corpo inteiro visivel de lado.",
                "Evite cortar pes, joelhos, quadril, tronco e cabeca.",
                "Mantenha a camera parada durante todo o movimento.",
                "Use boa iluminacao.",
            ]
        )

    return ScoreResult(
        final_score=final_score,
        movement_quality_score=movement_quality_score,
        analysis_confidence=confidence.score,
        classification=classify_score(final_score, confidence.score),
        summary=_summary(final_score, components),
        components=components,
        warnings=list(dict.fromkeys(warnings)),
        recommendations=list(dict.fromkeys(recommendations)),
        score_method=LATERAL_SCORE_TYPE,
        score_type=LATERAL_SCORE_TYPE,
        score_version=SCORE_VERSION,
        sub_scores={component.name: component.score for component in components},
    )
