import type { ReactNode } from "react";

type BadgeVariant = "completed" | "processing" | "warning" | "error" | "neutral";

const variants: Record<BadgeVariant, string> = {
  completed: "border-emerald-400/20 bg-emerald-400/10 text-emerald-300",
  processing: "border-cyan-400/20 bg-cyan-400/10 text-cyan-300",
  warning: "border-amber-400/20 bg-amber-400/10 text-amber-300",
  error: "border-red-400/20 bg-red-400/10 text-red-300",
  neutral: "border-white/10 bg-white/[0.05] text-[#A1A1AA]",
};

export function Badge({
  children,
  variant = "neutral",
}: {
  children: ReactNode;
  variant?: BadgeVariant;
}) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-medium tracking-wide ${variants[variant]}`}
    >
      {children}
    </span>
  );
}
