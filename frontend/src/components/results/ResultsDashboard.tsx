import { FeedbackPanel } from "@/components/results/FeedbackPanel";
import { MetricsCards } from "@/components/results/MetricsCards";
import { PerformanceCharts } from "@/components/results/PerformanceCharts";
import { RepBreakdownTable } from "@/components/results/RepBreakdownTable";
import { ScoreSummary } from "@/components/results/ScoreSummary";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import {
  cameraViewLabel,
  cameraViewNotice,
  formatSeconds,
} from "@/lib/formatters";
import type { AnalysisResult } from "@/types/analysis";

export function ResultsDashboard({
  result,
  isDemo = false,
}: {
  result: AnalysisResult;
  isDemo?: boolean;
}) {
  return (
    <main className="min-h-screen">
      <div className="mx-auto max-w-7xl px-6 pb-24 pt-12 lg:px-8">
        <div className="mb-9 flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
          <div>
            <div className="flex items-center gap-3">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-300">Analysis report</p>
              {isDemo && <Badge variant="neutral">Demo data</Badge>}
              <Badge variant="neutral">
                Analise {cameraViewLabel(result.camera_view)}
              </Badge>
            </div>
            <h1 className="mt-4 text-4xl font-semibold tracking-tight text-[#F4F4F5]">
              Relatório de performance
            </h1>
            <p className="mt-3 text-sm text-[#A1A1AA]">
              {result.totalReps} reps analisadas em {formatSeconds(result.metadata.durationSeconds)}
            </p>
            <p className="mt-3 max-w-2xl text-xs leading-5 text-[#A1A1AA]">
              {cameraViewNotice(result.camera_view)}
            </p>
          </div>
          <Button href="/#upload" variant="secondary">
            Nova análise
          </Button>
        </div>

        {result.camera_view_validation && (
          <div
            className={`mb-8 rounded-xl border p-5 ${
              result.camera_view_validation.status === "uncertain"
                ? "border-amber-400/20 bg-amber-400/[0.08]"
                : "border-emerald-400/15 bg-emerald-400/[0.06]"
            }`}
          >
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p
                  className={`text-xs font-semibold uppercase tracking-[0.18em] ${
                    result.camera_view_validation.status === "uncertain"
                      ? "text-amber-300"
                      : "text-emerald-300"
                  }`}
                >
                  Validacao do tipo de video
                </p>
                <p className="mt-2 text-sm leading-6 text-[#D4D4D8]">
                  {result.camera_view_validation.message}
                </p>
              </div>
              <div className="grid min-w-0 gap-3 sm:grid-cols-3">
                <ValidationStat
                  label="Selecionado"
                  value={cameraViewLabel(result.camera_view_validation.selected_camera_view)}
                />
                <ValidationStat
                  label="Detectado"
                  value={
                    result.camera_view_validation.detected_camera_view === "unknown"
                      ? "Indefinido"
                      : cameraViewLabel(result.camera_view_validation.detected_camera_view)
                  }
                />
                <ValidationStat
                  label="Confianca"
                  value={`${result.camera_view_validation.confidence}%`}
                />
              </div>
            </div>
            {result.camera_view_validation.status === "uncertain" &&
              result.camera_view_validation.warnings.length > 0 && (
                <p className="mt-4 text-sm leading-6 text-amber-100/85">
                  {result.camera_view_validation.warnings[0]}
                </p>
              )}
          </div>
        )}

        <div className="grid gap-6 lg:grid-cols-[0.42fr_0.58fr]">
          <ScoreSummary result={result} />
          <FeedbackPanel result={result} />
        </div>
        <div className="mt-10">
          <MetricsCards result={result} />
        </div>
        <div className="mt-10">
          <PerformanceCharts result={result} />
        </div>
        <div className="mt-10">
          <RepBreakdownTable reps={result.reps} />
        </div>
      </div>
    </main>
  );
}

function ValidationStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl bg-[#0B0F14]/55 px-4 py-3">
      <p className="text-xs text-[#A1A1AA]">{label}</p>
      <p className="mt-2 whitespace-nowrap text-sm font-semibold text-[#F4F4F5]">
        {value}
      </p>
    </div>
  );
}
