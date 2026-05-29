import { Card } from "@/components/ui/Card";
import { formatDegrees, humanizeDepth, scoreComponents } from "@/lib/formatters";
import type { AnalysisResult } from "@/types/analysis";

export function MetricsCards({ result }: { result: AnalysisResult }) {
  const isSide = result.camera_view === "side";
  const controlScore = scoreComponents(result.score).find((component) =>
    ["motor_control", "consistency"].includes(component.name),
  )?.score;
  const metrics = isSide
    ? [
        ["Angulo minimo do joelho", formatDegrees(result.metrics.minKneeAngle)],
        [
          "Angulo minimo do quadril",
          result.metrics.min_hip_angle === undefined || result.metrics.min_hip_angle === null
            ? "N/A"
            : formatDegrees(result.metrics.min_hip_angle),
        ],
        ["Profundidade", humanizeDepth(result.metrics.depthClassification)],
        [
          "Inclinacao no fundo",
          result.metrics.bottom_trunk_inclination === undefined ||
          result.metrics.bottom_trunk_inclination === null
            ? "N/A"
            : formatDegrees(result.metrics.bottom_trunk_inclination),
        ],
        [
          "Lado visivel",
          result.metrics.visibleSide === "right"
            ? "Direito"
            : result.metrics.visibleSide === "left"
              ? "Esquerdo"
              : "Auto",
        ],
        ["Controle motor", controlScore === undefined ? "N/A" : `${controlScore}/100`],
      ]
    : [
        ["Angulo medio do joelho", formatDegrees(result.metrics.averageKneeAngle)],
        ["Angulo minimo", formatDegrees(result.metrics.minKneeAngle)],
        ["Profundidade", humanizeDepth(result.metrics.depthClassification)],
        ["Estabilidade", `${result.metrics.stabilityScore}/100`],
        ["Simetria", `${result.metrics.symmetryScore}/100`],
        ["Controle motor", controlScore === undefined ? "N/A" : `${controlScore}/100`],
      ];

  return (
    <section>
      <div className="mb-6">
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-cyan-300">Metricas</p>
        <h2 className="mt-3 text-2xl font-semibold text-[#F4F4F5]">Leitura biomecanica</h2>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {metrics.map(([label, value]) => (
          <Card className="p-5" key={label}>
            <p className="text-xs text-[#A1A1AA]">{label}</p>
            <p className="mt-4 text-2xl font-semibold tracking-tight text-[#F4F4F5]">{value}</p>
          </Card>
        ))}
      </div>
    </section>
  );
}
