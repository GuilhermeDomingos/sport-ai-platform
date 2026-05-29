from pydantic import BaseModel

from app.schemas.camera_schema import CameraView


class VideoUploadResponse(BaseModel):
    message: str
    videoId: str
    filename: str
    originalFilename: str
    contentType: str
    size: int
    path: str
    exerciseType: str
    cameraView: CameraView


class VideoInfoResponse(BaseModel):
    videoId: str
    filename: str
    exists: bool
    path: str
    exerciseType: str = "squat"
    cameraView: CameraView = CameraView.FRONT
