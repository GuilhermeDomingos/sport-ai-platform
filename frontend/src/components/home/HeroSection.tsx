import { DemoPreview } from "@/components/home/DemoPreview";
import { Button } from "@/components/ui/Button";
import { Reveal } from "@/components/ui/Reveal";

export function HeroSection() {
  return (
    <section className="relative mx-auto grid max-w-7xl gap-14 px-6 pb-24 pt-16 lg:grid-cols-[1.02fr_0.78fr] lg:items-center lg:px-8 lg:pb-28 lg:pt-24">
      <div className="pointer-events-none absolute left-0 top-8 -z-10 h-96 w-96 rounded-full bg-cyan-400/[0.06] blur-3xl" />
      <Reveal>
        <p className="mb-7 inline-flex items-center gap-3 text-xs font-semibold uppercase tracking-[0.28em] text-cyan-300">
          <span className="h-px w-9 bg-cyan-300/70" />
          Precision training intelligence
        </p>
        <h1 className="max-w-3xl text-5xl font-semibold leading-[1.08] tracking-[-0.065em] text-[#F4F4F5] sm:text-6xl lg:text-[4.4rem]">
          Transforme seus vídeos de treino em métricas biomecânicas inteligentes.
        </h1>
        <p className="mt-7 max-w-xl text-lg leading-8 text-[#A1A1AA]">
          Envie seu vídeo de Crossfit, acompanhe sua execução e receba score,
          reps e feedback técnico com apoio de IA.
        </p>
        <div className="mt-11 flex flex-col gap-4 sm:flex-row">
          <Button href="/#upload">Analisar meu treino</Button>
          <Button href="/results/demo-back-squat" variant="secondary">
            Ver demonstração
          </Button>
        </div>
      </Reveal>
      <Reveal delay={0.12}>
        <DemoPreview />
      </Reveal>
    </section>
  );
}
