import { Badge } from "@/components/ui/Badge";
import type { PipelineState } from "@/types/analysis";

const steps: { state: PipelineState; label: string }[] = [
  { state: "uploading", label: "Upload concluído" },
  { state: "processing", label: "Processando vídeo" },
  { state: "extracting_frames", label: "Extraindo frames" },
  { state: "detecting_pose", label: "Detectando pose" },
  { state: "calculating_metrics", label: "Calculando métricas" },
  { state: "analyzing_movement", label: "Analisando reps" },
  { state: "calculating_score", label: "Calculando score" },
  { state: "generating_feedback", label: "Gerando feedback" },
];

const order = steps.map(({ state }) => state);

export function ProcessingSteps({ state }: { state: PipelineState }) {
  const currentIndex = order.indexOf(state);
  const isFinished = state === "completed";

  return (
    <div className="mt-7 border-t border-white/[0.08] pt-6">
      <div className="mb-5 flex items-center justify-between">
        <p className="text-xs font-medium uppercase tracking-[0.2em] text-[#A1A1AA]">Pipeline</p>
        {state === "error" ? (
          <Badge variant="error">Interrompido</Badge>
        ) : isFinished ? (
          <Badge variant="completed">Concluído</Badge>
        ) : (
          <Badge variant="processing">Em execução</Badge>
        )}
      </div>
      <ol className="grid gap-3 sm:grid-cols-2">
        {steps.map((step, index) => {
          const complete = isFinished || (currentIndex !== -1 && index < currentIndex);
          const active = state === step.state;

          return (
            <li className="flex items-center gap-3 text-sm" key={step.state}>
              <span
                className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full border ${
                  complete
                    ? "border-emerald-400/25 bg-emerald-400/10 text-emerald-300"
                    : active
                      ? "border-cyan-300/30 bg-cyan-300/10 text-cyan-300"
                      : "border-white/10 text-slate-600"
                }`}
              >
                {complete ? (
                  <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 16 16">
                    <path d="m3 8 3 3 7-7" stroke="currentColor" strokeWidth="1.8" />
                  </svg>
                ) : active ? (
                  <span className="h-2 w-2 animate-pulse rounded-full bg-cyan-300" />
                ) : (
                  <span className="h-1.5 w-1.5 rounded-full bg-slate-600" />
                )}
              </span>
              <span className={complete || active ? "text-[#F4F4F5]" : "text-[#A1A1AA]"}>
                {step.label}
              </span>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
