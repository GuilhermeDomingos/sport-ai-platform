from pydantic import BaseModel


class PoseDetectionResponse(BaseModel):
    videoId: str
    status: str
    totalFramesProcessed: int
    framesWithPose: int
    outputFile: str
