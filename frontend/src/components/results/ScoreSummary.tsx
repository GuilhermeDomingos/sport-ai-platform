import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import {
  componentLabel,
  cameraViewLabel,
  confidenceBadgeVariant,
  confidenceLabel,
  formatScore,
  movementLabel,
  scoreStatusTone,
  scoreSummary,
  statusLabel,
} from "@/lib/formatters";
import type { AnalysisResult } from "@/types/analysis";

export function ScoreSummary({ result }: { result: AnalysisResult }) {
  const summary = scoreSummary(result.score);

  return (
    <Card className="p-7 lg:p-8">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-medium uppercase tracking-[0.22em] text-[#A1A1AA]">
            AXON Movement Score
          </p>
          <p className="mt-5 text-7xl font-semibold tracking-[-0.08em] text-[#F4F4F5]">
            {formatScore(summary.finalScore)}
            {summary.finalScore !== null && (
              <span className="ml-1 text-2xl font-medium text-[#A1A1AA]">/100</span>
            )}
          </p>
          <p className="mt-4 max-w-xl text-sm leading-6 text-[#A1A1AA]">
            {summary.isInconclusive
              ? "Nao foi possivel gerar um score confiavel com este video."
              : summary.summary}
          </p>
        </div>
        <div className="flex flex-col items-start gap-3 sm:items-end">
          <Badge variant={summary.isInconclusive ? "error" : "completed"}>
            {summary.isInconclusive ? "Analise inconclusiva" : "Analysis Complete"}
          </Badge>
          <Badge variant={confidenceBadgeVariant(summary.analysisConfidence)}>
            Confianca {summary.analysisConfidence}% - {confidenceLabel(summary.analysisConfidence)}
          </Badge>
        </div>
      </div>
      <div className="mt-9 grid grid-cols-3 gap-4 border-t border-white/[0.08] pt-6">
        <div>
          <p className="text-xs text-[#A1A1AA]">Movimento</p>
          <p className="mt-2 text-sm font-semibold text-[#F4F4F5]">
            {movementLabel(result.movement)}
          </p>
        </div>
        <div>
          <p className="text-xs text-[#A1A1AA]">Tipo</p>
          <p className="mt-2 text-sm font-semibold text-[#F4F4F5]">
            {cameraViewLabel(result.camera_view)}
          </p>
        </div>
        <div>
          <p className="text-xs text-[#A1A1AA]">Classificacao</p>
          <p className="mt-2 text-sm font-semibold text-cyan-300">
            {summary.classification}
          </p>
        </div>
      </div>
      <div className="mt-7 grid gap-3 sm:grid-cols-2">
        {summary.components.map((component) => (
          <div className="rounded-xl bg-[#0B0F14]/55 p-4" key={component.name}>
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs text-[#A1A1AA]">{componentLabel(component.name)}</p>
                <p
                  className={`mt-2 text-xs font-semibold uppercase tracking-[0.16em] ${scoreStatusTone(
                    component.status,
                  )}`}
                >
                  {statusLabel(component.status)}
                </p>
              </div>
              <p className="text-2xl font-semibold text-[#F4F4F5]">{component.score}</p>
            </div>
            {component.details[0]?.message && (
              <p className="mt-3 text-xs leading-5 text-[#A1A1AA]">
                {component.details[0].message}
              </p>
            )}
          </div>
        ))}
      </div>
      {!summary.isAxon && (
        <p className="mt-5 text-xs leading-5 text-amber-300">
          Resultado em modo compatibilidade: o backend retornou o contrato antigo de score.
        </p>
      )}
    </Card>
  );
}
