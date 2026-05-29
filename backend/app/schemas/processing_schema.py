from pydantic import BaseModel


class VideoResolution(BaseModel):
    width: int
    height: int


class VideoMetadata(BaseModel):
    durationSeconds: float
    fps: float
    totalFrames: int
    resolution: VideoResolution
    fileSizeMb: float


class VideoProcessingResponse(BaseModel):
    videoId: str
    status: str
    metadata: VideoMetadata
