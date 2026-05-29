import { Suspense } from "react";

import { Footer } from "@/components/layout/Footer";
import { Header } from "@/components/layout/Header";
import { ResultsDashboard } from "@/components/results/ResultsDashboard";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { demoAnalysis } from "@/lib/formatters";
import { getAnalysis } from "@/services/sportAiApi";

export default function ResultsPage({
  params,
}: {
  params: Promise<{ videoId: string }>;
}) {
  return (
    <>
      <Header />
      <Suspense fallback={<ResultsLoading />}>
        <LoadedResults params={params} />
      </Suspense>
      <Footer />
    </>
  );
}

async function LoadedResults({
  params,
}: {
  params: Promise<{ videoId: string }>;
}) {
  const { videoId } = await params;

  if (videoId === "demo-back-squat") {
    return <ResultsDashboard isDemo result={demoAnalysis(videoId)} />;
  }

  let result;
  try {
    result = await getAnalysis(videoId);
  } catch (error) {
    return (
      <ResultsUnavailable
        message={analysisLoadMessage(error)}
      />
    );
  }

  return <ResultsDashboard result={result} />;
}

function analysisLoadMessage(error: unknown) {
  if (
    error instanceof Error &&
    error.message !== "fetch failed" &&
    error.message !== "Failed to fetch"
  ) {
    return error.message;
  }

  return "O relatorio nao esta disponivel no momento. Verifique a API ou inicie uma nova analise.";
}

function ResultsLoading() {
  return (
    <main className="min-h-screen">
      <div className="mx-auto max-w-7xl px-6 pb-24 pt-12 lg:px-8">
        <Card className="p-8">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-300">
            Analysis report
          </p>
          <p className="mt-5 text-xl font-semibold text-[#F4F4F5]">
            Carregando relatorio...
          </p>
        </Card>
      </div>
    </main>
  );
}

function ResultsUnavailable({ message }: { message: string }) {
  return (
    <main className="min-h-screen">
      <div className="mx-auto max-w-3xl px-6 pb-24 pt-12 lg:px-8">
        <Card className="p-8">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-red-300">
            Relatorio indisponivel
          </p>
          <h1 className="mt-5 text-3xl font-semibold text-[#F4F4F5]">
            Nao foi possivel carregar esta analise
          </h1>
          <p className="mt-4 text-sm leading-7 text-[#A1A1AA]">{message}</p>
          <Button className="mt-8" href="/#upload" variant="secondary">
            Nova analise
          </Button>
        </Card>
      </div>
    </main>
  );
}
