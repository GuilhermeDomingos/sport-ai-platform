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
