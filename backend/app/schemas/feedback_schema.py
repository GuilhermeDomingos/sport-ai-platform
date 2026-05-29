from pydantic import BaseModel, Field


class FeedbackResponse(BaseModel):
    videoId: str
    status: str
    movement: str
    summary: str
    strengths: list[str]
    improvements: list[str]
    recommendations: list[str]
    warnings: list[str] = Field(default_factory=list)
