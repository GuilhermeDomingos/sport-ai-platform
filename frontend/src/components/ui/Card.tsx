import type { HTMLAttributes } from "react";

export function Card({
  className = "",
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={`rounded-2xl border border-white/[0.08] bg-white/[0.045] shadow-[0_18px_50px_rgba(0,0,0,0.2)] backdrop-blur-sm ${className}`}
      {...props}
    />
  );
}
