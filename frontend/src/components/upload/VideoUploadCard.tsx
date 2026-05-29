"use client";

import { useRouter } from "next/navigation";
import {
  type ChangeEvent,
  type DragEvent,
  type SyntheticEvent,
  useEffect,
  useRef,
  useState,
} from "react";

import { ProcessingSteps } from "@/components/upload/ProcessingSteps";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { formatMegabytes } from "@/lib/formatters";
import {
  analyzeMovement,
  calculateMetrics,
  calculateScore,
  detectPose,
  extractFrames,
  generateFeedback,
  isCameraViewMismatchError,
  processVideo,
  uploadVideo,
} from "@/services/sportAiApi";
import type {
  CameraView,
  CameraViewMismatchErrorPayload,
  PipelineState,
} from "@/types/analysis";

export function VideoUploadCard() {
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [duration, setDuration] = useState<number | null>(null);
  const [state, setState] = useState<PipelineState>("idle");
  const [error, setError] = useState<string | null>(null);
  const [cameraViewMismatch, setCameraViewMismatch] =
    useState<CameraViewMismatchErrorPayload | null>(null);
  const [dragging, setDragging] = useState(false);
  const [cameraView, setCameraView] = useState<CameraView | null>(null);

  useEffect(() => {
    return () => {
      if (preview) URL.revokeObjectURL(preview);
    };
  }, [preview]);

  function chooseFile(nextFile: File | undefined) {
    if (!nextFile) return;
    if (!nextFile.type.startsWith("video/")) {
      setError("Selecione um arquivo de vídeo válido.");
      return;
    }

    setFile(nextFile);
    setPreview(URL.createObjectURL(nextFile));
    setDuration(null);
    setState("idle");
    setError(null);
    setCameraViewMismatch(null);
  }

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    chooseFile(event.target.files?.[0]);
  }

  function handleDrop(event: DragEvent<HTMLButtonElement>) {
    event.preventDefault();
    setDragging(false);
    chooseFile(event.dataTransfer.files?.[0]);
  }

  async function handleAnalyze(cameraViewOverride?: CameraView) {
    const selectedCameraView = cameraViewOverride ?? cameraView;
    if (!file || !selectedCameraView) return;

    setError(null);
    setCameraViewMismatch(null);
    try {
      setState("uploading");
      const uploaded = await uploadVideo(file, selectedCameraView);

      setState("processing");
      await processVideo(uploaded.videoId);

      setState("extracting_frames");
      await extractFrames(uploaded.videoId);

      setState("detecting_pose");
      await detectPose(uploaded.videoId);

      setState("calculating_metrics");
      await calculateMetrics(uploaded.videoId);

      setState("analyzing_movement");
      await analyzeMovement(uploaded.videoId);

      setState("calculating_score");
      await calculateScore(uploaded.videoId);

      setState("generating_feedback");
      await generateFeedback(uploaded.videoId);

      setState("completed");
      router.push(`/results/${uploaded.videoId}`);
    } catch (requestError) {
      setState("error");
      if (isCameraViewMismatchError(requestError)) {
        setCameraViewMismatch(requestError.payload);
        setError(null);
        return;
      }
      setError(
        requestError instanceof Error
          ? requestError.message
          : "A análise foi interrompida. Tente novamente.",
      );
    }
  }

  function handleUseDetectedView() {
    if (!cameraViewMismatch) return;
    const nextCameraView = cameraViewMismatch.detected_camera_view;
    setCameraView(nextCameraView);
    void handleAnalyze(nextCameraView);
  }

  const running = state !== "idle" && state !== "completed" && state !== "error";
  const canAnalyze = Boolean(file && cameraView && !running);

  return (
    <Card className="p-6 sm:p-8">
      <div className="flex items-start justify-between gap-6">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-cyan-300">Nova análise</p>
          <h3 className="mt-3 text-2xl font-semibold text-[#F4F4F5]">Envie seu vídeo</h3>
        </div>
        <p className="hidden text-right text-xs leading-6 text-[#A1A1AA] sm:block">
          MP4, MOV, AVI, MKV ou WEBM
          <br />
          Máximo 200 MB
        </p>
      </div>

      <input
        accept="video/mp4,video/quicktime,video/x-msvideo,video/x-matroska,video/webm"
        className="hidden"
        onChange={handleFileChange}
        ref={inputRef}
        type="file"
      />

      <button
        className={`mt-7 flex min-h-48 w-full flex-col items-center justify-center rounded-2xl border border-dashed px-6 transition ${
          dragging
            ? "border-cyan-300/55 bg-cyan-300/[0.07]"
            : "border-white/[0.14] bg-[#0B0F14]/50 hover:border-cyan-300/35 hover:bg-white/[0.03]"
        }`}
        disabled={running}
        onClick={() => inputRef.current?.click()}
        onDragEnter={(event) => {
          event.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDragOver={(event) => event.preventDefault()}
        onDrop={handleDrop}
        type="button"
      >
        <span className="flex h-12 w-12 items-center justify-center rounded-full border border-cyan-300/20 bg-cyan-300/[0.08] text-cyan-300">
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24">
            <path d="M12 16V5m0 0-4 4m4-4 4 4M5 18v1h14v-1" stroke="currentColor" strokeWidth="1.5" />
          </svg>
        </span>
        <span className="mt-5 text-sm font-semibold text-[#F4F4F5]">
          Arraste um vídeo ou clique para selecionar
        </span>
        <span className="mt-2 text-xs text-[#A1A1AA]">Uma série lateral ou frontal funciona melhor</span>
      </button>

      {file && preview && (
        <div className="mt-6 grid gap-5 sm:grid-cols-[132px_1fr] sm:items-center">
          <video
            className="h-24 w-full rounded-xl bg-black object-cover sm:w-32"
            muted
            onLoadedMetadata={(event: SyntheticEvent<HTMLVideoElement>) =>
              setDuration(event.currentTarget.duration)
            }
            src={preview}
          />
          <div>
            <p className="truncate text-sm font-semibold text-[#F4F4F5]">{file.name}</p>
            <p className="mt-2 text-xs text-[#A1A1AA]">
              {formatMegabytes(file.size / 1024 / 1024)}
              {duration ? `  /  ${duration.toFixed(1)}s` : ""}
            </p>
            <div className="mt-5">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#A1A1AA]">
                Tipo do video
              </p>
              <div className="mt-3 grid gap-3 sm:grid-cols-2">
                {[
                  {
                    value: "front" as const,
                    label: "Frontal",
                    description:
                      "Avalia simetria, alinhamento dos joelhos e estabilidade lateral.",
                  },
                  {
                    value: "side" as const,
                    label: "Lateral",
                    description:
                      "Avalia profundidade, angulos de joelho/quadril, tronco e controle.",
                  },
                ].map((option) => (
                  <label
                    className={`cursor-pointer rounded-xl border p-4 transition ${
                      cameraView === option.value
                        ? "border-cyan-300/55 bg-cyan-300/[0.08]"
                        : "border-white/[0.12] bg-[#0B0F14]/45 hover:border-cyan-300/30"
                    }`}
                    key={option.value}
                  >
                    <input
                      checked={cameraView === option.value}
                      className="sr-only"
                      disabled={running}
                      name="camera-view"
                      onChange={() => setCameraView(option.value)}
                      type="radio"
                      value={option.value}
                    />
                    <span className="text-sm font-semibold text-[#F4F4F5]">
                      {option.label}
                    </span>
                    <span className="mt-2 block text-xs leading-5 text-[#A1A1AA]">
                      {option.description}
                    </span>
                  </label>
                ))}
              </div>
            </div>
            <Button
              className="mt-4 w-full py-3 sm:w-auto"
              disabled={!canAnalyze}
              onClick={() => void handleAnalyze()}
              type="button"
            >
              {running ? "Analisando vídeo..." : "Analisar vídeo"}
            </Button>
            {!cameraView && (
              <p className="mt-3 text-xs text-amber-200">
                Selecione se o video e frontal ou lateral antes de iniciar.
              </p>
            )}
          </div>
        </div>
      )}

      {error && (
        <p className="mt-6 rounded-xl border border-red-400/20 bg-red-400/[0.08] px-4 py-3 text-sm text-red-200">
          {error}
        </p>
      )}
      {cameraViewMismatch && (
        <div className="mt-6 rounded-xl border border-amber-400/25 bg-amber-400/[0.08] p-5 text-sm text-amber-100">
          <p className="text-base font-semibold text-amber-100">
            Tipo de video diferente do selecionado
          </p>
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            <MismatchStat
              label="Selecionado"
              value={cameraViewLabel(cameraViewMismatch.selected_camera_view)}
            />
            <MismatchStat
              label="Detectado"
              value={cameraViewLabel(cameraViewMismatch.detected_camera_view)}
            />
            <MismatchStat
              label="Confianca"
              value={`${cameraViewMismatch.confidence}%`}
            />
          </div>
          <p className="mt-4 leading-6 text-amber-100/85">
            {cameraViewMismatch.message}
          </p>
          {cameraViewMismatch.recommendations.length > 0 && (
            <ul className="mt-4 space-y-2 text-amber-100/80">
              {cameraViewMismatch.recommendations.map((recommendation) => (
                <li className="flex gap-3" key={recommendation}>
                  <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-amber-200" />
                  {recommendation}
                </li>
              ))}
            </ul>
          )}
          <div className="mt-5 flex flex-col gap-3 sm:flex-row">
            <Button onClick={handleUseDetectedView} type="button">
              Alterar para {cameraViewLabel(cameraViewMismatch.detected_camera_view)} e reenviar
            </Button>
            <Button
              onClick={() => inputRef.current?.click()}
              type="button"
              variant="secondary"
            >
              Escolher outro video
            </Button>
          </div>
        </div>
      )}
      {state !== "idle" && <ProcessingSteps state={state} />}
    </Card>
  );
}

function cameraViewLabel(cameraView: CameraView) {
  return cameraView === "side" ? "Lateral" : "Frontal";
}

function MismatchStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl bg-[#0B0F14]/55 px-4 py-3">
      <p className="text-xs uppercase tracking-[0.16em] text-amber-100/60">
        {label}
      </p>
      <p className="mt-2 text-sm font-semibold text-amber-50">{value}</p>
    </div>
  );
}
