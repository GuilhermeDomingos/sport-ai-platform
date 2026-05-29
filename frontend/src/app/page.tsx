import { FeatureCards } from "@/components/home/FeatureCards";
import { HeroSection } from "@/components/home/HeroSection";
import { HowItWorks } from "@/components/home/HowItWorks";
import { Footer } from "@/components/layout/Footer";
import { Header } from "@/components/layout/Header";
import { VideoUploadCard } from "@/components/upload/VideoUploadCard";

export default function Home() {
  return (
    <>
      <Header />
      <main className="overflow-hidden">
        <HeroSection />
        <HowItWorks />
        <FeatureCards />
        <section className="relative px-6 pb-24 pt-4 lg:px-8" id="upload">
          <div className="pointer-events-none absolute bottom-12 left-1/2 -z-10 h-72 w-3/5 -translate-x-1/2 bg-cyan-300/[0.05] blur-3xl" />
          <div className="mx-auto grid max-w-7xl items-start gap-14 lg:grid-cols-[0.72fr_1fr]">
            <div className="lg:sticky lg:top-32">
              <p className="text-xs font-semibold uppercase tracking-[0.25em] text-cyan-300">Upload</p>
              <h2 className="mt-4 max-w-md text-4xl font-semibold tracking-tight text-[#F4F4F5]">
                Sua próxima evolução começa aqui.
              </h2>
              <p className="mt-5 max-w-sm text-base leading-7 text-[#A1A1AA]">
                Escolha uma gravação de Back Squat. Processamos movimento, score e
                orientações de performance em uma sequência precisa.
              </p>
              <div className="mt-10 space-y-4 text-sm text-[#A1A1AA]">
                {["Análise frame a frame", "Score por execução", "Feedback direto"].map(
                  (label) => (
                    <p className="flex items-center gap-3" key={label}>
                      <span className="h-1.5 w-1.5 rounded-full bg-cyan-300" />
                      {label}
                    </p>
                  ),
                )}
              </div>
            </div>
            <VideoUploadCard />
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
