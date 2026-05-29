import type {
  AnalysisResult,
  AxonMovementScore,
  LegacyScore,
  ScoreComponent,
  ScoreResponse,
} from "@/types/analysis";

export function formatScore(value: number | null) {
  if (value === null) return "Inconclusivo";
  return `${Math.round(value)}`;
}

export function formatDegrees(value: number) {
  return `${value.toFixed(1)} deg`;
}

export function formatSeconds(value: number) {
  return `${value.toFixed(1)}s`;
}

export function formatMegabytes(value: number) {
  return `${value.toFixed(1)} MB`;
}

export function humanizeDepth(depth: string) {
  const values: Record<string, string> = {
    deep: "Profunda",
    parallel: "Paralela",
    shallow: "Acima do ideal",
    below_parallel: "Abaixo do paralelo",
    above_parallel: "Acima do paralelo",
  };

  return values[depth.toLowerCase()] ?? depth;
}

export function scoreClassification(score: number) {
  if (score >= 85) return "Excelente padrao de movimento";
  if (score >= 70) return "Bom padrao, com pequenos ajustes";
  if (score >= 50) return "Compensacoes relevantes detectadas";
  if (score >= 30) return "Baixa competencia de movimento";
  return "Analise critica ou muito limitada";
}

function legacyOverallScore(score: LegacyScore) {
  return score.overallScore ?? 0;
}

export function movementLabel(movement: string) {
  return movement.toLowerCase() === "squat" ? "Back Squat" : movement;
}

export function isAxonMovementScore(
  score: ScoreResponse["score"],
): score is AxonMovementScore {
  return "final_score" in score;
}

export function componentLabel(name: string) {
  const labels: Record<string, string> = {
    mobility: "Mobilidade",
    stability: "Estabilidade",
    symmetry: "Simetria",
    amplitude_depth: "Amplitude e profundidade",
    joint_kinematics: "Cinematica articular",
    trunk_posture: "Postura de tronco",
    motor_control: "Controle motor",
    analysis_confidence: "Confiabilidade",
    depth: "Profundidade",
    consistency: "Consistencia",
  };

  return labels[name] ?? name.replaceAll("_", " ");
}

export function cameraViewLabel(cameraView?: AnalysisResult["camera_view"]) {
  if (cameraView === "side") return "Lateral";
  return "Frontal";
}

export function cameraViewNotice(cameraView?: AnalysisResult["camera_view"]) {
  if (cameraView === "side") {
    return "Esta analise lateral prioriza profundidade, angulos de joelho, quadril, tronco e controle do movimento. Metricas de simetria frontal podem ser limitadas neste angulo.";
  }

  return "Esta analise frontal prioriza simetria, alinhamento dos joelhos e estabilidade lateral. Metricas de profundidade podem ser limitadas neste angulo.";
}

export function statusLabel(status: string) {
  const labels: Record<string, string> = {
    excellent: "Excelente",
    good: "Bom",
    attention: "Atencao",
    poor: "Baixo",
    low: "Baixo",
    critical: "Critico",
    reliable: "Confiavel",
    acceptable: "Aceitavel",
    limited: "Limitada",
  };

  return labels[status] ?? status;
}

export function confidenceLabel(confidence: number) {
  if (confidence >= 80) return "Confiavel";
  if (confidence >= 60) return "Aceitavel com alerta";
  if (confidence >= 40) return "Limitada";
  return "Inconclusiva";
}

export function scoreStatusTone(status: string) {
  if (["excellent", "good", "reliable"].includes(status)) return "text-emerald-300";
  if (["attention", "limited"].includes(status)) return "text-amber-300";
  if (["poor", "low", "critical"].includes(status)) return "text-red-300";
  return "text-cyan-300";
}

export function confidenceBadgeVariant(confidence: number) {
  if (confidence >= 80) return "completed";
  if (confidence >= 40) return "warning";
  return "error";
}

export function scoreComponents(score: ScoreResponse["score"]): ScoreComponent[] {
  if (isAxonMovementScore(score)) return score.components;

  return legacyScoreComponents(score);
}

export function scoreSummary(score: ScoreResponse["score"]) {
  if (isAxonMovementScore(score)) {
    return {
      finalScore: score.final_score,
      movementQualityScore: score.movement_quality_score,
      analysisConfidence: score.analysis_confidence,
      classification: score.classification,
      summary: score.summary,
      components: score.components ?? [],
      warnings: score.warnings ?? [],
      recommendations: score.recommendations ?? [],
      method: score.score_method ?? "AXON_MOVEMENT_SCORE",
      type: score.score_type,
      version: score.score_version,
      isAxon: true,
      isInconclusive: score.final_score === null,
    };
  }

  return {
    finalScore: score.overallScore,
    movementQualityScore: score.overallScore,
    analysisConfidence: 100,
    classification: scoreClassification(legacyOverallScore(score)),
    summary: "Relatorio gerado com o contrato de score anterior.",
    components: legacyScoreComponents(score),
    warnings: ["Este resultado usa o contrato legado de score."],
    recommendations: [],
    method: "LEGACY_SCORE",
    type: undefined,
    version: undefined,
    isAxon: false,
    isInconclusive: false,
  };
}

function legacyScoreComponents(score: LegacyScore): ScoreComponent[] {
  return [
    { name: "depth", score: score.depthScore, weight: 0.3, status: legacyStatus(score.depthScore), details: [] },
    { name: "stability", score: score.stabilityScore, weight: 0.25, status: legacyStatus(score.stabilityScore), details: [] },
    { name: "symmetry", score: score.symmetryScore, weight: 0.2, status: legacyStatus(score.symmetryScore), details: [] },
    { name: "consistency", score: score.consistencyScore, weight: 0.25, status: legacyStatus(score.consistencyScore), details: [] },
  ];
}

function legacyStatus(score: number) {
  if (score >= 85) return "excellent";
  if (score >= 70) return "good";
  if (score >= 50) return "attention";
  if (score >= 30) return "poor";
  return "critical";
}

export function demoAnalysis(videoId = "demo-back-squat"): AnalysisResult {
  const reps = [
    [1, "parallel", 87.4, 89, 2.1],
    [2, "parallel", 85.6, 88, 2.2],
    [3, "deep", 83.2, 86, 2.3],
    [4, "parallel", 86.7, 85, 2.3],
    [5, "parallel", 87.1, 82, 2.5],
    [6, "parallel", 89.8, 80, 2.5],
    [7, "shallow", 94.3, 75, 2.7],
    [8, "shallow", 96.1, 72, 2.8],
  ].map(([rep, depth, angle, stability, seconds]) => ({
    rep: rep as number,
    startFrame: (rep as number) * 30,
    bottomFrame: (rep as number) * 30 + 12,
    endFrame: (rep as number) * 30 + 25,
    depth: depth as string,
    minKneeAngle: angle as number,
    stabilityScore: stability as number,
    symmetryScore: 88,
    durationFrames: Math.round((seconds as number) * 30),
    averageVelocity: 35,
  }));

  return {
    videoId,
    status: "completed",
    movement: "squat",
    camera_view: "front",
    metadata: {
      durationSeconds: 22.8,
      fps: 30,
      totalFrames: 684,
      fileSizeMb: 18.4,
      resolution: { width: 1080, height: 1920 },
    },
    metrics: {
      averageKneeAngle: 90.2,
      minKneeAngle: 83.2,
      averageHipAngle: 91.5,
      torsoInclination: 17.6,
      depthClassification: "parallel",
      stabilityScore: 81,
      symmetryScore: 88,
    },
    totalReps: 8,
    reps,
    score: {
      final_score: 78,
      movement_quality_score: 76,
      analysis_confidence: 91,
      classification: "Bom padrao, com pequenos ajustes",
      summary:
        "Seu agachamento apresenta boa mobilidade geral, com leve assimetria e perda de estabilidade no fim da serie.",
      components: [
        {
          name: "mobility",
          score: 82,
          weight: 0.2,
          status: "good",
          details: [
            {
              metric: "squat_depth",
              value: 0.84,
              status: "good",
              message: "Boa profundidade de agachamento.",
            },
          ],
        },
        {
          name: "stability",
          score: 74,
          weight: 0.2,
          status: "good",
          details: [],
        },
        {
          name: "symmetry",
          score: 69,
          weight: 0.2,
          status: "attention",
          details: [
            {
              metric: "knee_symmetry",
              value: 14,
              status: "attention",
              message: "Foi detectada leve diferenca entre os joelhos.",
            },
          ],
        },
        {
          name: "motor_control",
          score: 80,
          weight: 0.25,
          status: "good",
          details: [],
        },
        {
          name: "analysis_confidence",
          score: 91,
          weight: 0.15,
          status: "reliable",
          details: [],
        },
      ],
      warnings: [],
      recommendations: [
        "Observe o alinhamento dos joelhos durante a descida.",
        "Mantenha o tronco estavel no ponto mais baixo do movimento.",
      ],
      score_method: "AXON_MOVEMENT_SCORE",
      score_version: "1.0.0",
    },
    feedback: {
      videoId,
      status: "feedback_generated",
      movement: "squat",
      summary:
        "Boa profundidade, com leve perda de estabilidade nas ultimas repeticoes.",
      strengths: [
        "Profundidade consistente nas seis primeiras repeticoes.",
        "Boa simetria durante a fase de subida.",
      ],
      improvements: [
        "Controle dos joelhos diminuiu nas duas ultimas repeticoes.",
      ],
      recommendations: [
        "Reduza ligeiramente a carga para preservar estabilidade no fim da serie.",
        "Priorize cadencia controlada na descida.",
      ],
    },
  };
}
