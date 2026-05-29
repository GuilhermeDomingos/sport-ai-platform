import json
import shutil
from pathlib import Path

import cv2
import mediapipe as mp
from fastapi import HTTPException, status

from app.core.config import OUTPUT_DIR
from app.services.video_service import get_video_info


POSE_LANDMARK_NAMES = {
    0: "nose",
    1: "left_eye_inner",
    2: "left_eye",
    3: "left_eye_outer",
    4: "right_eye_inner",
    5: "right_eye",
    6: "right_eye_outer",
    7: "left_ear",
    8: "right_ear",
    9: "mouth_left",
    10: "mouth_right",
    11: "left_shoulder",
    12: "right_shoulder",
    13: "left_elbow",
    14: "right_elbow",
    15: "left_wrist",
    16: "right_wrist",
    17: "left_pinky",
    18: "right_pinky",
    19: "left_index",
    20: "right_index",
    21: "left_thumb",
    22: "right_thumb",
    23: "left_hip",
    24: "right_hip",
    25: "left_knee",
    26: "right_knee",
    27: "left_ankle",
    28: "right_ankle",
    29: "left_heel",
    30: "right_heel",
    31: "left_foot_index",
    32: "right_foot_index",
}


def get_frames_dir(video_id: str) -> Path:
    return OUTPUT_DIR / video_id / "frames"


def prepare_pose_output_dir(video_id: str) -> Path:
    output_dir = OUTPUT_DIR / video_id / "pose"

    if output_dir.exists():
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def _public_output_file(video_id: str) -> str:
    return f"app/outputs/{video_id}/pose/landmarks.json"


def serialize_landmarks(pose_landmarks) -> list[dict]:
    return [
        {
            "index": index,
            "name": POSE_LANDMARK_NAMES.get(index, f"landmark_{index}"),
            "x": landmark.x,
            "y": landmark.y,
            "z": landmark.z,
            "visibility": landmark.visibility,
        }
        for index, landmark in enumerate(pose_landmarks.landmark)
    ]


def detect_pose(video_id: str) -> dict:
    video_info = get_video_info(video_id)
    normalized_id = video_info["videoId"]
    frames_dir = get_frames_dir(normalized_id)

    if not frames_dir.is_dir():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Frames nao encontrados. Extraia os frames antes de detectar a pose.",
        )

    frame_files = sorted(frames_dir.glob("*.jpg"))
    if not frame_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum frame encontrado para deteccao de pose.",
        )

    pose_output_dir = prepare_pose_output_dir(normalized_id)
    output_file = pose_output_dir / "landmarks.json"
    frames_result: list[dict] = []
    frames_with_pose = 0

    with mp.solutions.pose.Pose(
        static_image_mode=True,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.5,
    ) as pose:
        for frame_file in frame_files:
            image = cv2.imread(str(frame_file))
            if image is None:
                frames_result.append(
                    {
                        "frame": frame_file.name,
                        "poseDetected": False,
                        "landmarks": [],
                    }
                )
                continue

            result = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            pose_detected = result.pose_landmarks is not None
            landmarks = (
                serialize_landmarks(result.pose_landmarks) if pose_detected else []
            )
            if pose_detected:
                frames_with_pose += 1

            frames_result.append(
                {
                    "frame": frame_file.name,
                    "poseDetected": pose_detected,
                    "landmarks": landmarks,
                }
            )

    with output_file.open("w", encoding="utf-8") as output:
        json.dump(
            {"videoId": normalized_id, "frames": frames_result},
            output,
            ensure_ascii=True,
            indent=2,
        )

    return {
        "videoId": normalized_id,
        "status": "pose_detected",
        "totalFramesProcessed": len(frame_files),
        "framesWithPose": frames_with_pose,
        "outputFile": _public_output_file(normalized_id),
    }
