import { Card } from "@/components/ui/Card";
import { formatDegrees, humanizeDepth } from "@/lib/formatters";
import type { RepAnalysis } from "@/types/analysis";

export function RepBreakdownTable({ reps }: { reps: RepAnalysis[] }) {
  return (
    <Card className="overflow-hidden">
      <div className="px-6 pb-5 pt-6">
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-cyan-300">Repetições</p>
        <h2 className="mt-3 text-2xl font-semibold text-[#F4F4F5]">Detalhamento por rep</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="border-y border-white/[0.08] bg-[#0B0F14]/45 text-xs uppercase tracking-[0.15em] text-[#A1A1AA]">
            <tr>
              <th className="px-6 py-4 font-medium">Rep</th>
              <th className="px-4 py-4 font-medium">Profundidade</th>
              <th className="px-4 py-4 font-medium">Estabilidade</th>
              <th className="px-4 py-4 font-medium">Min knee angle</th>
              <th className="px-4 py-4 font-medium">Duração</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.06] text-[#A1A1AA]">
            {reps.map((rep) => (
              <tr key={rep.rep}>
                <td className="px-6 py-4 font-semibold text-[#F4F4F5]">{String(rep.rep).padStart(2, "0")}</td>
                <td className="px-4 py-4">{humanizeDepth(rep.depth)}</td>
                <td className="px-4 py-4">{rep.stabilityScore}/100</td>
                <td className="px-4 py-4">{formatDegrees(rep.minKneeAngle)}</td>
                <td className="px-4 py-4">{rep.durationFrames} frames</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
