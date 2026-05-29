import { Card } from "@/components/ui/Card";

const steps = [
  ["01", "Envie seu vídeo", "Faça upload de uma série de Back Squat."],
  ["02", "A IA detecta sua pose", "O movimento é mapeado frame a frame."],
  ["03", "Calculamos métricas", "Profundidade e controle viram dados."],
  ["04", "Receba feedback", "Ajustes claros para a próxima série."],
];

export function HowItWorks() {
  return (
    <section id="como-funciona" className="border-y border-white/[0.06] bg-white/[0.015]">
      <div className="mx-auto max-w-7xl px-6 py-24 lg:px-8">
        <p className="text-xs font-semibold uppercase tracking-[0.25em] text-cyan-300">Como funciona</p>
        <h2 className="mt-4 text-3xl font-semibold tracking-tight text-[#F4F4F5]">
          Do vídeo ao insight em quatro movimentos.
        </h2>
        <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {steps.map(([number, title, description]) => (
            <Card className="p-7" key={number}>
              <p className="text-xs font-semibold tracking-[0.2em] text-cyan-300">{number}</p>
              <h3 className="mt-8 text-lg font-semibold text-[#F4F4F5]">{title}</h3>
              <p className="mt-3 text-sm leading-6 text-[#A1A1AA]">{description}</p>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
