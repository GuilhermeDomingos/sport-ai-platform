export type CameraView = "front" | "side";

export type UploadResponse = {
  message: string;
  videoId: string;
  filename: string;
  originalFilename: string;
  contentType: string;
  size: number;
  path: string;
  exerciseType: string;
  cameraView: CameraView;
};

export type VideoMetadata = {
  durationSeconds: number;
  fps: number;
  totalFrames: number;
  resolution: {
    width: number;
    height: number;
  };
  fileSizeMb: number;
};

export type ProcessingResponse = {
  videoId: string;
  status: string;
  metadata: VideoMetadata;
};

export type FrameExtractionResponse = {
  videoId: string;
  status: string;
  frameIntervalSeconds: number;
  totalFramesExtracted: number;
  outputDir: string;
  frames: string[];
};

export type PoseDetectionResponse = {
  videoId: string;
  status: string;
  totalFramesProcessed: number;
  framesWithPose: number;
  outputFile: string;
};

export type MetricsResponse = {
  videoId: string;
  status: string;
  movement: string;
  metrics: {
    averageKneeAngle: number;
    minKneeAngle: number;
    averageHipAngle: number;
    torsoInclination: number;
    depthClassification: string;
    symmetryScore: number;
    stabilityScore: number;
    cameraView?: CameraView | null;
    visibleSide?: "left" | "right" | null;
    squat_depth_ratio?: number | null;
    min_hip_angle?: number | null;
    max_knee_angle?: number | null;
    max_hip_angle?: number | null;
    knee_rom?: number | null;
    hip_rom?: number | null;
    hip_vertical_displacement?: number | null;
    range_of_motion?: number | null;
    max_trunk_inclination?: number | null;
    bottom_trunk_inclination?: number | null;
    trunk_variation?: number | null;
    movement_smoothness?: number | null;
    bottom_control?: number | null;
  };
  camera_view?: CameraView | null;
};

export type RepAnalysis = {
  rep: number;
  startFrame: number;
  bottomFrame: number;
  endFrame: number;
  depth: string;
  minKneeAngle: number;
  stabilityScore: number;
  symmetryScore?: number | null;
  durationFrames: number;
  averageVelocity: number;
};

export type MovementAnalysisResponse = {
  videoId: string;
  movement: string;
  camera_view?: CameraView | null;
  visibleSide?: "left" | "right" | null;
  totalReps: number;
  reps: RepAnalysis[];
};

export type ScoreComponentDetail = {
  metric: string;
  value?: unknown;
  status: string;
  message: string;
};

export type ScoreComponent = {
  name: string;
  score: number;
  weight: number;
  status: string;
  details: ScoreComponentDetail[];
};

export type AxonMovementScore = {
  final_score: number | null;
  movement_quality_score: number | null;
  analysis_confidence: number;
  classification: string;
  summary: string;
  components: ScoreComponent[];
  warnings: string[];
  recommendations: string[];
  score_method?: string;
  score_type?: "AXON_FRONTAL_MOVEMENT_SCORE" | "AXON_LATERAL_MOVEMENT_SCORE";
  score_version?: string;
};

export type LegacyScore = {
  overallScore: number | null;
  depthScore: number;
  stabilityScore: number;
  symmetryScore: number;
  consistencyScore: number;
};

export type ScoreResponse = {
  videoId: string;
  status: string;
  movement: string;
  camera_view?: CameraView | null;
  score: AxonMovementScore | LegacyScore;
};

export type FeedbackResponse = {
  videoId: string;
  status: string;
  movement: string;
  summary: string;
  strengths: string[];
  improvements: string[];
  recommendations: string[];
  warnings?: string[];
};

export type AnalysisResult = {
  videoId: string;
  status: string;
  movement: string;
  camera_view?: CameraView | null;
  metadata: VideoMetadata;
  metrics: MetricsResponse["metrics"];
  totalReps: number;
  reps: RepAnalysis[];
  score: ScoreResponse["score"];
  feedback: FeedbackResponse;
};

export type PipelineState =
  | "idle"
  | "uploading"
  | "processing"
  | "extracting_frames"
  | "detecting_pose"
  | "calculating_metrics"
  | "analyzing_movement"
  | "calculating_score"
  | "generating_feedback"
  | "completed"
  | "error";
