import { Card } from "@/components/ui/Card";
import { Reveal } from "@/components/ui/Reveal";

const features = [
  ["Análise por repetição", "Observe a técnica em cada fase do movimento."],
  ["Score biomecânico", "Uma leitura simples de qualidade da execução."],
  ["Feedback acionável", "Correções objetivas para o próximo treino."],
  ["Evolução técnica", "Crie uma base mensurável de performance."],
  ["Detecção de fadiga", "Identifique quedas de controle ao longo da série."],
  ["Visão de performance", "Conecte amplitude, simetria e estabilidade."],
];

export function FeatureCards() {
  return (
    <section id="metricas" className="mx-auto max-w-7xl px-6 py-24 lg:px-8">
      <div className="max-w-xl">
        <p className="text-xs font-semibold uppercase tracking-[0.25em] text-cyan-300">Métricas</p>
        <h2 className="mt-4 text-4xl font-semibold tracking-tight text-[#F4F4F5]">
          Performance explicada com clareza.
        </h2>
      </div>
      <div className="mt-12 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {features.map(([title, description], index) => (
          <Reveal delay={index * 0.035} key={title}>
            <Card className="group h-full p-8 transition duration-300 hover:border-cyan-300/20">
              <div className="mb-8 h-px w-10 bg-cyan-300/65 transition-all duration-300 group-hover:w-16" />
              <h3 className="text-lg font-semibold text-[#F4F4F5]">{title}</h3>
              <p className="mt-3 max-w-xs text-sm leading-7 text-[#A1A1AA]">{description}</p>
            </Card>
          </Reveal>
        ))}
      </div>
    </section>
  );
}
