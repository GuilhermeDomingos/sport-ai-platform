import { Card } from "@/components/ui/Card";
import { scoreSummary } from "@/lib/formatters";
import type { AnalysisResult } from "@/types/analysis";

export function FeedbackPanel({ result }: { result: AnalysisResult }) {
  const summary = scoreSummary(result.score);
  const warnings = summary.warnings;
  const recommendations = [
    ...summary.recommendations,
    ...result.feedback.recommendations.filter(
      (recommendation) => !summary.recommendations.includes(recommendation),
    ),
  ];

  return (
    <Card className="p-7 lg:p-8">
      <p className="text-xs font-semibold uppercase tracking-[0.22em] text-cyan-300">
        Feedback tecnico
      </p>
      <p className="mt-5 text-xl font-semibold leading-8 text-[#F4F4F5]">
        {summary.summary || result.feedback.summary}
      </p>
      <div className="mt-8 grid gap-5 lg:grid-cols-3">
        <FeedbackSection
          color="text-emerald-300"
          emptyText="Nenhum ponto forte destacado nesta analise."
          items={result.feedback.strengths}
          label="Pontos fortes"
        />
        <FeedbackSection
          color="text-amber-300"
          emptyText="Nenhum alerta relevante nesta analise."
          items={[...warnings, ...result.feedback.improvements]}
          label="Alertas e ajustes"
        />
        <FeedbackSection
          color="text-cyan-300"
          emptyText="Nenhuma recomendacao adicional."
          items={
            summary.isInconclusive
              ? inconclusiveRecommendations(recommendations)
              : recommendations
          }
          label="Recomendacoes"
        />
      </div>
    </Card>
  );
}

function FeedbackSection({
  color,
  emptyText,
  items,
  label,
}: {
  color: string;
  emptyText: string;
  items: string[];
  label: string;
}) {
  return (
    <section className="rounded-xl bg-[#0B0F14]/55 p-5">
      <h3 className={`text-xs font-medium uppercase tracking-[0.16em] ${color}`}>
        {label}
      </h3>
      {items.length ? (
        <ul className="mt-4 space-y-3 text-sm leading-6 text-[#A1A1AA]">
          {items.map((text) => (
            <li className="flex gap-3" key={text}>
              <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-[#A1A1AA]" />
              {text}
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-4 text-sm text-[#A1A1AA]">{emptyText}</p>
      )}
    </section>
  );
}

function inconclusiveRecommendations(recommendations: string[]) {
  const fallback = [
    "Grave novamente com o corpo inteiro visivel.",
    "Evite cortar pes, joelhos, quadril e ombros.",
    "Use boa iluminacao.",
    "Posicione a camera em um angulo estavel.",
    "Grave pelo menos 2 repeticoes completas.",
  ];

  return recommendations.length ? recommendations : fallback;
}
