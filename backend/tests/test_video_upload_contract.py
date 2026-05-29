from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import video_service


client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_storage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(video_service, "UPLOAD_DIR", tmp_path / "uploads")
    monkeypatch.setattr(video_service, "OUTPUT_DIR", tmp_path / "outputs")


def test_upload_requires_camera_view() -> None:
    response = client.post(
        "/videos/upload",
        files={"file": ("squat.mp4", b"video", "video/mp4")},
        data={"exerciseType": "squat"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "cameraView is required and must be either 'front' or 'side'."


def test_upload_rejects_invalid_camera_view() -> None:
    response = client.post(
        "/videos/upload",
        files={"file": ("squat.mp4", b"video", "video/mp4")},
        data={"exerciseType": "squat", "cameraView": "diagonal"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "cameraView is required and must be either 'front' or 'side'."


def test_upload_persists_camera_view_manifest() -> None:
    response = client.post(
        "/videos/upload",
        files={"file": ("squat.mp4", b"video", "video/mp4")},
        data={"exerciseType": "squat", "cameraView": "side"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["cameraView"] == "side"
    assert client.get(f"/videos/{body['videoId']}").json()["cameraView"] == "side"

