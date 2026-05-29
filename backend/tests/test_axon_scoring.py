from app.modules.scoring.classification import classify_score
from app.modules.scoring.components import clamp_score, weighted_score
from app.modules.scoring.engine import calculate_score
from app.modules.scoring.exercises.squat import (
    calculate_squat_analysis_confidence_score,
    calculate_squat_mobility_score,
    calculate_squat_motor_control_score,
    calculate_squat_stability_score,
    calculate_squat_symmetry_score,
)
from app.modules.scoring.exercises.squat_side import (
    calculate_amplitude_depth_score,
    calculate_joint_kinematics_score,
    calculate_lateral_analysis_confidence_score,
    calculate_lateral_motor_control_score,
    calculate_squat_side_score,
    calculate_trunk_posture_score,
)
from app.modules.scoring.schemas import ScoringInput
from app.schemas.camera_schema import CameraView


def _metrics(**overrides: object) -> dict:
    metrics = {
        "averageKneeAngle": 130.0,
        "minKneeAngle": 88.0,
        "averageHipAngle": 118.0,
        "torsoInclination": 12.0,
        "depthClassification": "below_parallel",
        "symmetryScore": 92,
        "stabilityScore": 90,
    }
    metrics.update(overrides)
    return metrics


def _reps(**overrides: object) -> list[dict]:
    reps = [
        {
            "rep": 1,
            "depth": "below_parallel",
            "minKneeAngle": 88.0,
            "stabilityScore": 91,
            "symmetryScore": 92,
            "durationFrames": 10,
            "averageVelocity": 19.0,
        },
        {
            "rep": 2,
            "depth": "below_parallel",
            "minKneeAngle": 90.0,
            "stabilityScore": 89,
            "symmetryScore": 91,
            "durationFrames": 11,
            "averageVelocity": 20.0,
        },
    ]
    for rep in reps:
        rep.update(overrides)
    return reps


def _pose_quality(**overrides: object) -> dict:
    quality = {
        "valid_pose_frame_ratio": 0.96,
        "average_landmark_visibility": 0.92,
        "critical_landmark_visibility_ratio": 0.95,
        "valid_reps": 2,
    }
    quality.update(overrides)
    return quality


def _input(
    metrics: dict | None = None,
    reps: list[dict] | None = None,
    pose_quality: dict | None = None,
) -> ScoringInput:
    return ScoringInput(
        analysis_id="analysis-1",
        exercise_type="squat",
        metrics=metrics or _metrics(),
        reps=reps if reps is not None else _reps(),
        pose_quality=pose_quality or _pose_quality(),
    )


def _side_metrics(**overrides: object) -> dict:
    metrics = {
        "averageKneeAngle": 130.0,
        "minKneeAngle": 88.0,
        "averageHipAngle": 116.0,
        "torsoInclination": 18.0,
        "depthClassification": "below_parallel",
        "symmetryScore": 100,
        "stabilityScore": 88,
        "cameraView": "side",
        "visibleSide": "right",
        "squat_depth_ratio": 0.88,
        "min_hip_angle": 92.0,
        "max_knee_angle": 174.0,
        "max_hip_angle": 168.0,
        "knee_rom": 86.0,
        "hip_rom": 76.0,
        "hip_vertical_displacement": 0.18,
        "range_of_motion": 81.0,
        "max_trunk_inclination": 28.0,
        "bottom_trunk_inclination": 22.0,
        "trunk_variation": 4.0,
        "movement_smoothness": 92,
        "bottom_control": 90,
        "valid_pose_frame_ratio": 0.95,
        "visible_side_landmark_confidence": 0.94,
        "critical_landmarks_visible_ratio": 0.93,
    }
    metrics.update(overrides)
    return metrics


def _side_input(
    metrics: dict | None = None,
    reps: list[dict] | None = None,
) -> ScoringInput:
    return ScoringInput(
        analysis_id="analysis-1",
        exercise_type="squat",
        camera_view=CameraView.SIDE,
        metrics=metrics or _side_metrics(),
        reps=reps if reps is not None else _reps(),
    )


def test_helpers_clamp_and_weighted_score() -> None:
    assert clamp_score(-10) == 0
    assert clamp_score(101.6) == 100
    assert weighted_score([(80, 0.25), (100, 0.75)]) == 95


def test_classify_score_ranges_and_inconclusive() -> None:
    assert classify_score(None, 95) == "Analise inconclusiva"
    assert classify_score(90, 95) == "Excelente padrao de movimento"
    assert classify_score(75, 95) == "Bom padrao, com pequenos ajustes"
    assert classify_score(55, 95) == "Compensacoes relevantes detectadas"


def test_component_calculators_return_bounded_scores() -> None:
    extreme_metrics = _metrics(
        minKneeAngle=-20,
        averageHipAngle=300,
        torsoInclination=300,
        symmetryScore=150,
        stabilityScore=-10,
    )
    components = [
        calculate_squat_mobility_score(extreme_metrics),
        calculate_squat_stability_score(extreme_metrics, _reps()),
        calculate_squat_symmetry_score(extreme_metrics, _reps()),
        calculate_squat_motor_control_score(extreme_metrics, _reps()),
        calculate_squat_analysis_confidence_score(
            extreme_metrics,
            _pose_quality(
                valid_pose_frame_ratio=2,
                average_landmark_visibility=-1,
                critical_landmark_visibility_ratio=3,
            ),
        ),
    ]

    assert all(0 <= component.score <= 100 for component in components)


def test_excellent_squat_scores_high() -> None:
    result = calculate_score(_input())

    assert result.final_score is not None
    assert result.final_score >= 85
    assert result.classification == "Excelente padrao de movimento"
    assert not result.warnings
    assert result.sub_scores["analysis_confidence"] >= 85


def test_good_squat_with_asymmetry_recommends_alignment() -> None:
    result = calculate_score(
        _input(
            metrics=_metrics(symmetryScore=45),
            reps=_reps(symmetryScore=45),
        )
    )

    assert result.final_score is not None
    assert 70 <= result.final_score <= 84
    assert result.sub_scores["symmetry"] < result.sub_scores["mobility"]
    assert any("joelhos" in item for item in result.recommendations)


def test_low_mobility_penalizes_score_and_recommends_amplitude() -> None:
    result = calculate_score(
        _input(
            metrics=_metrics(
                minKneeAngle=145,
                averageHipAngle=165,
                torsoInclination=38,
                depthClassification="above_parallel",
            )
        )
    )

    assert result.sub_scores["mobility"] < 70
    assert result.final_score is not None
    assert result.final_score < 85
    assert any("amplitude" in item for item in result.recommendations)


def test_low_confidence_returns_inconclusive_without_final_score() -> None:
    result = calculate_score(
        _input(
            pose_quality=_pose_quality(
                valid_pose_frame_ratio=0.2,
                average_landmark_visibility=0.3,
                critical_landmark_visibility_ratio=0.2,
                valid_reps=0,
            )
        )
    )

    assert result.final_score is None
    assert result.movement_quality_score is None
    assert result.classification == "Analise inconclusiva"
    assert result.warnings


def test_side_component_calculators_return_bounded_scores() -> None:
    metrics = _side_metrics(
        squat_depth_ratio=3,
        minKneeAngle=-20,
        min_hip_angle=300,
        bottom_trunk_inclination=300,
        valid_pose_frame_ratio=2,
    )
    components = [
        calculate_amplitude_depth_score(metrics),
        calculate_joint_kinematics_score(metrics),
        calculate_trunk_posture_score(metrics),
        calculate_lateral_motor_control_score(metrics, _reps()),
        calculate_lateral_analysis_confidence_score(metrics, _reps()),
    ]

    assert all(0 <= component.score <= 100 for component in components)


def test_calculate_score_routes_side_squat_to_lateral_score() -> None:
    result = calculate_score(_side_input())

    assert result.final_score is not None
    assert result.final_score >= 85
    assert result.score_type == "AXON_LATERAL_MOVEMENT_SCORE"
    assert result.sub_scores["amplitude_depth"] >= 85


def test_side_squat_with_limited_depth_is_penalized() -> None:
    result = calculate_squat_side_score(
        _side_input(
            metrics=_side_metrics(
                squat_depth_ratio=0.42,
                minKneeAngle=142,
                hip_vertical_displacement=0.04,
                range_of_motion=32,
            )
        )
    )

    assert result.sub_scores["amplitude_depth"] < 70
    assert result.final_score is not None
    assert any("profundidade" in item.lower() for item in result.recommendations)


def test_side_squat_with_excessive_trunk_inclination_is_penalized() -> None:
    result = calculate_squat_side_score(
        _side_input(
            metrics=_side_metrics(
                bottom_trunk_inclination=58,
                max_trunk_inclination=70,
                trunk_variation=24,
            )
        )
    )

    assert result.sub_scores["trunk_posture"] < 70
    assert any("tronco" in item.lower() for item in result.recommendations)


def test_side_low_confidence_returns_inconclusive_without_zero_score() -> None:
    result = calculate_squat_side_score(
        _side_input(
            metrics=_side_metrics(
                valid_pose_frame_ratio=0.2,
                visible_side_landmark_confidence=0.25,
                critical_landmarks_visible_ratio=0.2,
            ),
            reps=[],
        )
    )

    assert result.final_score is None
    assert result.classification == "Analise inconclusiva"
    assert result.score_type == "AXON_LATERAL_MOVEMENT_SCORE"
    assert result.warnings
