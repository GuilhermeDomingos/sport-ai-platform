import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";

export function DemoPreview() {
  return (
    <Card className="overflow-hidden p-6 sm:p-8">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-[0.22em] text-[#A1A1AA]">Movement</p>
          <p className="mt-3 text-lg font-semibold text-[#F4F4F5]">Back Squat</p>
        </div>
        <Badge variant="completed">Analysis Ready</Badge>
      </div>
      <div className="my-8 flex items-end justify-between border-y border-white/[0.08] py-8">
        <div>
          <p className="text-xs font-medium uppercase tracking-[0.2em] text-[#A1A1AA]">Overall score</p>
          <p className="mt-3 text-6xl font-semibold tracking-[-0.08em] text-[#F4F4F5]">
            84<span className="text-2xl font-medium text-[#A1A1AA]">/100</span>
          </p>
        </div>
        <div className="text-right">
          <p className="text-xs font-medium uppercase tracking-[0.2em] text-[#A1A1AA]">Total reps</p>
          <p className="mt-3 text-4xl font-semibold text-[#F4F4F5]">08</p>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="rounded-xl bg-[#0B0F14]/55 p-4">
          <p className="text-xs font-medium uppercase tracking-[0.18em] text-[#A1A1AA]">Stability</p>
          <p className="mt-2 text-2xl font-semibold text-[#F4F4F5]">
            81<span className="text-sm text-[#A1A1AA]">/100</span>
          </p>
        </div>
        <div className="rounded-xl bg-[#0B0F14]/55 p-4">
          <p className="text-xs font-medium uppercase tracking-[0.18em] text-cyan-300">Control</p>
          <p className="mt-2 text-2xl font-semibold text-[#F4F4F5]">Good</p>
        </div>
      </div>
      <div className="mt-4 rounded-xl bg-[#0B0F14]/55 p-4">
        <p className="text-xs font-medium uppercase tracking-[0.18em] text-cyan-300">
          Insight
        </p>
        <p className="mt-3 text-sm leading-6 text-[#A1A1AA]">
          Boa profundidade, com leve perda de estabilidade nas últimas reps.
        </p>
      </div>
      <div className="mt-7 flex gap-2">
        {[88, 84, 86, 82, 79, 76, 72].map((level, index) => (
          <span
            key={level}
            className="flex-1 rounded-full bg-white/[0.06]"
            aria-hidden="true"
          >
            <span
              className={`block rounded-full ${index > 4 ? "bg-amber-300/55" : "bg-cyan-300/65"}`}
              style={{ height: `${level / 2}px`, marginTop: `${48 - level / 2}px` }}
            />
          </span>
        ))}
      </div>
    </Card>
  );
}
