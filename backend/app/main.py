from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.analysis import router as analysis_router
from app.routes.feedback import router as feedback_router
from app.routes.frames import router as frames_router
from app.routes.metrics import router as metrics_router
from app.routes.movement import router as movement_router
from app.routes.pose import router as pose_router
from app.routes.processing import router as processing_router
from app.routes.scoring import router as scoring_router
from app.routes.videos import router as videos_router


app = FastAPI(
    title="Sport AI API",
    description="API para upload e analise de videos esportivos",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(videos_router, prefix="/videos", tags=["Videos"])
app.include_router(analysis_router, prefix="/videos", tags=["Analysis"])
app.include_router(processing_router, prefix="/videos", tags=["Processing"])
app.include_router(frames_router, prefix="/videos", tags=["Frames"])
app.include_router(pose_router, prefix="/videos", tags=["Pose"])
app.include_router(metrics_router, prefix="/videos", tags=["Metrics"])
app.include_router(movement_router, prefix="/videos", tags=["Movement"])
app.include_router(scoring_router, prefix="/videos", tags=["Scoring"])
app.include_router(feedback_router, prefix="/videos", tags=["Feedback"])
