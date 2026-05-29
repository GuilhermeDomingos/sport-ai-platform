from pydantic import BaseModel


class FrameExtractionResponse(BaseModel):
    videoId: str
    status: str
    frameIntervalSeconds: float
    totalFramesExtracted: int
    outputDir: str
    frames: list[str]
