"use client";

import React, { useRef, useEffect, useState } from "react";
import dynamic from "next/dynamic";

// Dynamic import to avoid SSR issues with canvas/force-graph
const ForceGraph2D = dynamic(() => import("react-force-graph-2d"), {
    ssr: false,
    loading: () => <div className="w-full h-full flex items-center justify-center bg-slate-900/20 rounded-xl">Loading Graph Engine...</div>
});

interface Node {
    id: string;
    label: string;
    val?: number;
}

interface Link {
    source: string;
    target: string;
    weight: number;
    description?: string;
}

interface CausalFlowGraphProps {
    data: {
        nodes: Node[];
        edges: Link[];
    };
}

export default function CausalFlowGraph({ data }: CausalFlowGraphProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

    useEffect(() => {
        if (containerRef.current) {
            setDimensions({
                width: containerRef.current.clientWidth,
                height: 300
            });
        }
    }, [data]);

    // Format data for the graph
    const gData = {
        nodes: data.nodes.map(n => ({ ...n, val: 5 })),
        links: data.edges.map(e => ({
            ...e,
            source: e.source,
            target: e.target
        }))
    };

    return (
        <div ref={containerRef} className="w-full h-[300px] relative rounded-xl overflow-hidden glass-card p-0" style={{ background: "rgba(15, 23, 42, 0.4)" }}>
            <ForceGraph2D
                graphData={gData}
                width={dimensions.width}
                height={dimensions.height}
                backgroundColor="rgba(0,0,0,0)"
                nodeLabel="label"
                nodeColor={() => "#6366f1"}
                linkColor={(link: any) => link.weight > 0 ? "rgba(16, 185, 129, 0.4)" : "rgba(239, 68, 68, 0.4)"}
                linkDirectionalParticles={2}
                linkDirectionalParticleSpeed={(link: any) => Math.abs(link.weight) * 0.01}
                linkDirectionalArrowLength={3}
                linkDirectionalArrowRelPos={1}
                nodeCanvasObject={(node: any, ctx, globalScale) => {
                    const label = node.label;
                    const fontSize = 12 / globalScale;
                    ctx.font = `${fontSize}px Inter, sans-serif`;
                    const textWidth = ctx.measureText(label).width;
                    const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2); // some padding

                    ctx.fillStyle = "rgba(15, 23, 42, 0.8)";
                    ctx.beginPath();
                    ctx.roundRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2, bckgDimensions[0], bckgDimensions[1], 2);
                    ctx.fill();

                    ctx.textAlign = "center";
                    ctx.textBaseline = "middle";
                    ctx.fillStyle = "#e2e8f0";
                    ctx.fillText(label, node.x, node.y);

                    node.__bckgDimensions = bckgDimensions; // to use in nodePointerAreaPaint
                }}
            />
        </div>
    );
}
