import type {
  AnalysisResult,
  FeedbackResponse,
  FrameExtractionResponse,
  MetricsResponse,
  MovementAnalysisResponse,
  PoseDetectionResponse,
  ProcessingResponse,
  ScoreResponse,
  UploadResponse,
  CameraView,
} from "@/types/analysis";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, init);

  if (!response.ok) {
    let message = "Nao foi possivel concluir a analise.";

    try {
      const error = (await response.json()) as { detail?: string };
      message = error.detail ?? message;
    } catch {
      // Preserve the friendly fallback when an upstream error is not JSON.
    }

    throw new Error(message);
  }

  return (await response.json()) as T;
}

export async function uploadVideo(
  file: File,
  cameraView: CameraView,
  exerciseType = "squat",
): Promise<UploadResponse> {
  const body = new FormData();
  body.append("file", file);
  body.append("exerciseType", exerciseType);
  body.append("cameraView", cameraView);

  return request<UploadResponse>("/videos/upload", {
    method: "POST",
    body,
  });
}

export async function processVideo(videoId: string) {
  return request<ProcessingResponse>(`/videos/${videoId}/process`, {
    method: "POST",
  });
}

export async function extractFrames(videoId: string) {
  return request<FrameExtractionResponse>(`/videos/${videoId}/frames/extract`, {
    method: "POST",
  });
}

export async function detectPose(videoId: string) {
  return request<PoseDetectionResponse>(`/videos/${videoId}/pose/detect`, {
    method: "POST",
  });
}

export async function calculateMetrics(videoId: string) {
  return request<MetricsResponse>(`/videos/${videoId}/metrics/calculate`, {
    method: "POST",
  });
}

export async function analyzeMovement(videoId: string) {
  return request<MovementAnalysisResponse>(
    `/videos/${videoId}/movement/analyze`,
    { method: "POST" },
  );
}

export async function calculateScore(videoId: string) {
  return request<ScoreResponse>(`/videos/${videoId}/score/calculate`, {
    method: "POST",
  });
}

export async function generateFeedback(videoId: string) {
  return request<FeedbackResponse>(`/videos/${videoId}/feedback/generate`, {
    method: "POST",
  });
}

export async function getAnalysis(videoId: string) {
  return request<AnalysisResult>(`/videos/${videoId}/analysis`, {
    cache: "no-store",
  });
}
