"use client";

import React from "react";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Cell,
    ReferenceLine,
} from "recharts";

interface TornadoDataItem {
    variable: string;
    low: number;
    high: number;
    total_swing: number;
}

interface TornadoChartProps {
    data: TornadoDataItem[];
}

export default function TornadoChart({ data }: TornadoChartProps) {
    // Format data for Recharts: low becomes the negative bar, high becomes the positive bar
    const chartData = data.map((d) => ({
        name: d.variable,
        lowValue: d.low * 100, // as percentage point change
        highValue: d.high * 100,
        absSwing: d.total_swing,
    }));

    const CustomTooltip = ({ active, payload, label }: any) => {
        if (active && payload && payload.length) {
            return (
                <div className="glass-card p-3 text-xs border border-white/10 shadow-xl" style={{ background: "#0f172a" }}>
                    <p className="font-bold mb-1">{label}</p>
                    <div className="space-y-1">
                        <p className="text-emerald-400">
                            +20% Variance: {payload[1].value > 0 ? "+" : ""}{payload[1].value.toFixed(1)}% prob.
                        </p>
                        <p className="text-rose-400">
                            -20% Variance: {payload[0].value > 0 ? "+" : ""}{payload[0].value.toFixed(1)}% prob.
                        </p>
                    </div>
                </div>
            );
        }
        return null;
    };

    return (
        <div className="w-full h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
                <BarChart
                    data={chartData}
                    layout="vertical"
                    margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
                >
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
                    <XAxis
                        type="number"
                        tick={{ fontSize: 10, fill: "#64748b" }}
                        axisLine={false}
                        unit="%"
                    />
                    <YAxis
                        dataKey="name"
                        type="category"
                        tick={{ fontSize: 10, fill: "#94a3b8" }}
                        width={100}
                        axisLine={false}
                    />
                    <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
                    <ReferenceLine x={0} stroke="rgba(255,255,255,0.2)" />
                    <Bar dataKey="lowValue" fill="#ef4444" radius={[4, 0, 0, 4]} barSize={12} />
                    <Bar dataKey="highValue" fill="#10b981" radius={[0, 4, 4, 0]} barSize={12} />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}
