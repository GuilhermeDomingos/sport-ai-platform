"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Card } from "@/components/ui/Card";
import { componentLabel, scoreComponents } from "@/lib/formatters";
import type { AnalysisResult } from "@/types/analysis";

const tooltipStyle = {
  background: "#111827",
  border: "1px solid rgba(255,255,255,0.1)",
  borderRadius: "12px",
  color: "#F4F4F5",
  fontSize: "12px",
  boxShadow: "0 12px 36px rgba(0,0,0,0.25)",
};

export function PerformanceCharts({ result }: { result: AnalysisResult }) {
  const repData = result.reps.map((rep) => ({
    name: `R${rep.rep}`,
    estabilidade: rep.stabilityScore,
    angulo: rep.minKneeAngle,
  }));
  const breakdown = scoreComponents(result.score).map((component) => ({
    name: componentLabel(component.name),
    score: component.score,
  }));

  return (
    <section>
      <p className="text-xs font-semibold uppercase tracking-[0.22em] text-cyan-300">Performance</p>
      <h2 className="mt-3 text-2xl font-semibold text-[#F4F4F5]">Tendências da série</h2>
      <div className="mt-6 grid gap-6 xl:grid-cols-3">
        <ChartCard title="Stability per rep">
          <ResponsiveContainer height={205} width="100%">
            <LineChart data={repData}>
              <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
              <XAxis dataKey="name" stroke="#71717A" tickLine={false} />
              <YAxis domain={[0, 100]} stroke="#71717A" tickLine={false} width={28} />
              <Tooltip contentStyle={tooltipStyle} />
              <Line dataKey="estabilidade" dot={false} stroke="#67E8F9" strokeWidth={2} type="monotone" />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Knee angle per rep">
          <ResponsiveContainer height={205} width="100%">
            <LineChart data={repData}>
              <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
              <XAxis dataKey="name" stroke="#71717A" tickLine={false} />
              <YAxis stroke="#71717A" tickLine={false} width={28} />
              <Tooltip contentStyle={tooltipStyle} />
              <Line dataKey="angulo" dot={false} stroke="#E5E7EB" strokeWidth={2} type="monotone" />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Score breakdown">
          <ResponsiveContainer height={205} width="100%">
            <BarChart data={breakdown}>
              <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
              <XAxis dataKey="name" stroke="#71717A" tickLine={false} fontSize={10} />
              <YAxis domain={[0, 100]} stroke="#71717A" tickLine={false} width={28} />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey="score" fill="#67E8F9" opacity={0.72} radius={[5, 5, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </section>
  );
}

function ChartCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <Card className="p-5">
      <p className="mb-5 text-sm text-[#A1A1AA]">{title}</p>
      {children}
    </Card>
  );
}
