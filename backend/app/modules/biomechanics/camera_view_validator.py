from dataclasses import dataclass
from statistics import mean

from app.modules.biomechanics.camera_view_config import CAMERA_VIEW_VALIDATION_CONFIG
from app.schemas.camera_schema import (
    CameraView,
    CameraViewInferenceResult,
    CameraViewValidationResult,
    CameraViewValidationStatus,
    DetectedCameraView,
)


LEFT_CRITICAL = ["left_shoulder", "left_hip", "left_knee", "left_ankle"]
RIGHT_CRITICAL = ["right_shoulder", "right_hip", "right_knee", "right_ankle"]
LANDMARK_PAIRS = [
    ("left_shoulder", "right_shoulder"),
    ("left_hip", "right_hip"),
    ("left_knee", "right_knee"),
    ("left_ankle", "right_ankle"),
]


@dataclass(frozen=True)
class CameraViewFeatures:
    valid_frame_count: int
    both_shoulders_visible: bool
    both_hips_visible: bool
    both_knees_visible: bool
    both_ankles_visible: bool
    avg_shoulder_width_ratio: float
    avg_hip_width_ratio: float
    knees_horizontal_distance_ratio: float
    ankles_horizontal_distance_ratio: float
    left_right_confidence_diff: float
    dominant_side_confidence: float


def _clamp_score(value: float) -> int:
    return round(max(0.0, min(100.0, value)))


def _visibility(landmark: dict | None) -> float:
    if not landmark:
        return 0.0
    try:
        return float(landmark.get("visibility", 0.0))
    except (TypeError, ValueError):
        return 0.0


def _x(landmark: dict | None) -> float | None:
    if not landmark:
        return None
    try:
        return float(landmark["x"])
    except (KeyError, TypeError, ValueError):
        return None


def _average_landmark_visibility(points: dict[str, dict], names: list[str]) -> float:
    values = [_visibility(points.get(name)) for name in names]
    return mean(values) if values else 0.0


def _horizontal_distance(points: dict[str, dict], left: str, right: str) -> float | None:
    left_x = _x(points.get(left))
    right_x = _x(points.get(right))
    if left_x is None or right_x is None:
        return None
    return abs(left_x - right_x)


def _sample_frames(pose_frames: list[dict]) -> list[dict]:
    detected = [
        frame
        for frame in pose_frames
        if frame.get("poseDetected") and isinstance(frame.get("landmarks"), list)
    ]
    if len(detected) <= 30:
        return detected

    step = (len(detected) - 1) / 29
    indexes = [round(index * step) for index in range(30)]
    return [detected[index] for index in indexes]


def _visible_in_frame(points: dict[str, dict], names: list[str], threshold: float) -> bool:
    return all(_visibility(points.get(name)) >= threshold for name in names)


def extract_camera_view_features(pose_frames: list[dict]) -> CameraViewFeatures:
    config = CAMERA_VIEW_VALIDATION_CONFIG
    min_visibility = config["min_landmark_visibility"]
    sampled_frames = _sample_frames(pose_frames)
    valid_points: list[dict[str, dict]] = []

    for frame in sampled_frames:
        points = {
            landmark.get("name"): landmark
            for landmark in frame.get("landmarks", [])
            if isinstance(landmark, dict) and landmark.get("name")
        }
        if all(name in points for pair in LANDMARK_PAIRS for name in pair):
            avg_visibility = _average_landmark_visibility(
                points, LEFT_CRITICAL + RIGHT_CRITICAL
            )
            if avg_visibility >= min_visibility * 0.6:
                valid_points.append(points)

    if not valid_points:
        return CameraViewFeatures(
            valid_frame_count=0,
            both_shoulders_visible=False,
            both_hips_visible=False,
            both_knees_visible=False,
            both_ankles_visible=False,
            avg_shoulder_width_ratio=0.0,
            avg_hip_width_ratio=0.0,
            knees_horizontal_distance_ratio=0.0,
            ankles_horizontal_distance_ratio=0.0,
            left_right_confidence_diff=1.0,
            dominant_side_confidence=0.0,
        )

    def visible_ratio(names: list[str]) -> float:
        return sum(
            1 for points in valid_points if _visible_in_frame(points, names, min_visibility)
        ) / len(valid_points)

    def average_distance(left: str, right: str) -> float:
        values = [
            distance
            for points in valid_points
            if (distance := _horizontal_distance(points, left, right)) is not None
        ]
        return mean(values) if values else 0.0

    left_confidences = [
        _average_landmark_visibility(points, LEFT_CRITICAL) for points in valid_points
    ]
    right_confidences = [
        _average_landmark_visibility(points, RIGHT_CRITICAL) for points in valid_points
    ]
    avg_left = mean(left_confidences)
    avg_right = mean(right_confidences)

    return CameraViewFeatures(
        valid_frame_count=len(valid_points),
        both_shoulders_visible=visible_ratio(["left_shoulder", "right_shoulder"]) >= 0.7,
        both_hips_visible=visible_ratio(["left_hip", "right_hip"]) >= 0.7,
        both_knees_visible=visible_ratio(["left_knee", "right_knee"]) >= 0.7,
        both_ankles_visible=visible_ratio(["left_ankle", "right_ankle"]) >= 0.7,
        avg_shoulder_width_ratio=average_distance("left_shoulder", "right_shoulder"),
        avg_hip_width_ratio=average_distance("left_hip", "right_hip"),
        knees_horizontal_distance_ratio=average_distance("left_knee", "right_knee"),
        ankles_horizontal_distance_ratio=average_distance("left_ankle", "right_ankle"),
        left_right_confidence_diff=abs(avg_left - avg_right),
        dominant_side_confidence=max(avg_left, avg_right),
    )


def calculate_front_view_likelihood(features: CameraViewFeatures) -> int:
    config = CAMERA_VIEW_VALIDATION_CONFIG["front"]
    score = 0

    if features.both_shoulders_visible:
        score += 15
    if features.both_hips_visible:
        score += 15
    if features.both_knees_visible:
        score += 15
    if features.both_ankles_visible:
        score += 10
    if features.avg_shoulder_width_ratio >= config["min_shoulder_width_ratio"]:
        score += 20
    if features.avg_hip_width_ratio >= config["min_hip_width_ratio"]:
        score += 15
    if features.left_right_confidence_diff <= config["max_left_right_confidence_diff"]:
        score += 10
    if features.knees_horizontal_distance_ratio >= config["min_knee_distance_ratio"]:
        score += 5
    if features.ankles_horizontal_distance_ratio >= config["min_ankle_distance_ratio"]:
        score += 5

    return _clamp_score(score)


def calculate_side_view_likelihood(features: CameraViewFeatures) -> int:
    config = CAMERA_VIEW_VALIDATION_CONFIG["side"]
    score = 0

    if features.avg_shoulder_width_ratio <= config["max_shoulder_width_ratio"]:
        score += 20
    if features.avg_hip_width_ratio <= config["max_hip_width_ratio"]:
        score += 20
    if features.left_right_confidence_diff >= config["min_left_right_confidence_diff"]:
        score += 15
    if features.knees_horizontal_distance_ratio <= config["max_knee_distance_ratio"]:
        score += 15
    if features.ankles_horizontal_distance_ratio <= config["max_ankle_distance_ratio"]:
        score += 10
    if features.dominant_side_confidence >= config["min_dominant_side_confidence"]:
        score += 20

    return _clamp_score(score)


def infer_camera_view(pose_frames: list[dict]) -> CameraViewInferenceResult:
    config = CAMERA_VIEW_VALIDATION_CONFIG
    features = extract_camera_view_features(pose_frames)

    if features.valid_frame_count < config["min_valid_frames"]:
        return CameraViewInferenceResult(
            detected_camera_view=DetectedCameraView.UNKNOWN,
            confidence=0,
            front_score=0,
            side_score=0,
            reasons=["Poucos frames validos para inferir o angulo do video."],
        )

    front_score = calculate_front_view_likelihood(features)
    side_score = calculate_side_view_likelihood(features)
    diff = abs(front_score - side_score)
    confidence = max(front_score, side_score)

    if diff < config["min_score_diff_to_detect"]:
        return CameraViewInferenceResult(
            detected_camera_view=DetectedCameraView.UNKNOWN,
            confidence=confidence,
            front_score=front_score,
            side_score=side_score,
            reasons=[
                "Diferenca insuficiente entre os sinais de video frontal e lateral."
            ],
        )

    if front_score > side_score:
        return CameraViewInferenceResult(
            detected_camera_view=DetectedCameraView.FRONT,
            confidence=confidence,
            front_score=front_score,
            side_score=side_score,
            reasons=[
                "O video apresenta caracteristicas compativeis com visao frontal.",
                "Os dois lados do corpo aparecem com boa visibilidade.",
                "Ombros e quadris apresentam separacao horizontal relevante.",
            ],
        )

    return CameraViewInferenceResult(
        detected_camera_view=DetectedCameraView.SIDE,
        confidence=confidence,
        front_score=front_score,
        side_score=side_score,
        reasons=[
            "O video apresenta caracteristicas compativeis com visao lateral.",
            "Ha predominancia visual de um lado do corpo.",
            "A separacao horizontal entre ombros e quadris e menor.",
        ],
    )


def build_camera_view_mismatch_message(
    selected_camera_view: CameraView,
    detected_camera_view: DetectedCameraView,
) -> str:
    selected_label = "frontal" if selected_camera_view is CameraView.FRONT else "lateral"
    detected_label = "frontal" if detected_camera_view is DetectedCameraView.FRONT else "lateral"
    return (
        f"Voce selecionou video {selected_label}, mas o video enviado parece "
        f"estar em visao {detected_label}."
    )


def camera_view_recommendations(
    selected_camera_view: CameraView,
    detected_camera_view: DetectedCameraView,
) -> list[str]:
    if selected_camera_view is CameraView.SIDE and detected_camera_view is DetectedCameraView.FRONT:
        return [
            "Altere o tipo do video para Frontal e envie novamente.",
            "Ou grave um novo video lateral, com ombro, quadril, joelho e tornozelo visiveis.",
        ]
    if selected_camera_view is CameraView.FRONT and detected_camera_view is DetectedCameraView.SIDE:
        return [
            "Altere o tipo do video para Lateral e envie novamente.",
            "Ou grave um novo video frontal, com os dois lados do corpo visiveis.",
        ]
    return ["Confira o tipo selecionado e envie o video novamente."]


def validate_camera_view(
    selected_camera_view: CameraView,
    pose_frames: list[dict],
) -> CameraViewValidationResult:
    inference = infer_camera_view(pose_frames)
    config = CAMERA_VIEW_VALIDATION_CONFIG

    if inference.detected_camera_view == DetectedCameraView.UNKNOWN:
        return CameraViewValidationResult(
            selected_camera_view=selected_camera_view,
            detected_camera_view=DetectedCameraView.UNKNOWN,
            confidence=inference.confidence,
            status=CameraViewValidationStatus.UNCERTAIN,
            is_valid=True,
            should_block_analysis=False,
            message="Nao foi possivel confirmar com seguranca se o video e frontal ou lateral.",
            reasons=inference.reasons,
            warnings=[
                "A analise pode ter menor precisao porque o angulo do video nao foi confirmado com alta confianca."
            ],
        )

    if (
        inference.detected_camera_view.value != selected_camera_view.value
        and inference.confidence >= config["min_confidence_to_block"]
    ):
        return CameraViewValidationResult(
            selected_camera_view=selected_camera_view,
            detected_camera_view=inference.detected_camera_view,
            confidence=inference.confidence,
            status=CameraViewValidationStatus.MISMATCH,
            is_valid=False,
            should_block_analysis=True,
            message=build_camera_view_mismatch_message(
                selected_camera_view, inference.detected_camera_view
            ),
            reasons=inference.reasons,
            warnings=[],
        )

    if inference.detected_camera_view.value != selected_camera_view.value:
        return CameraViewValidationResult(
            selected_camera_view=selected_camera_view,
            detected_camera_view=inference.detected_camera_view,
            confidence=inference.confidence,
            status=CameraViewValidationStatus.UNCERTAIN,
            is_valid=True,
            should_block_analysis=False,
            message="A validacao do tipo de video ficou incerta.",
            reasons=inference.reasons,
            warnings=[
                "A analise pode ter menor precisao porque os sinais de camera nao foram conclusivos."
            ],
        )

    return CameraViewValidationResult(
        selected_camera_view=selected_camera_view,
        detected_camera_view=inference.detected_camera_view,
        confidence=inference.confidence,
        status=CameraViewValidationStatus.VALID,
        is_valid=True,
        should_block_analysis=False,
        message="Tipo de video validado com sucesso.",
        reasons=inference.reasons,
        warnings=[],
    )
