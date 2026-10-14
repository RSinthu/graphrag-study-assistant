import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import ForceGraph2D from "react-force-graph-2d";
import { colorForType } from "../colors.js";

const nodeRadius = (node) => 3 + Math.sqrt(node.degree || 1) * 2;
const endId = (end) => (typeof end === "object" ? end.id : end); // the library swaps ids for node objects

export default function GraphView({ data, highlight, error, onRefresh }) {
  const wrapRef = useRef(null);
  const graphRef = useRef();
  const fittedRef = useRef(false);
  const [size, setSize] = useState({ width: 0, height: 0 });
  const [selected, setSelected] = useState(null);

  // The canvas needs explicit pixel sizes, so follow the card's size.
  useEffect(() => {
    const observer = new ResizeObserver(([entry]) => {
      const { width, height } = entry.contentRect;
      setSize({ width, height });
    });
    observer.observe(wrapRef.current);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    fittedRef.current = false;
    setSelected(null);
  }, [data]);

  const types = useMemo(() => [...new Set(data.nodes.map((n) => n.type || "Concept"))], [data]);

  const connections = useMemo(() => {
    if (!selected) return [];
    return data.links
      .filter((l) => endId(l.source) === selected.id || endId(l.target) === selected.id)
      .map((l) => {
        const outgoing = endId(l.source) === selected.id;
        return { relation: l.relation, other: outgoing ? endId(l.target) : endId(l.source), outgoing };
      });
  }, [selected, data]);

  const isLit = useCallback(
    (node) => highlight.has(node.id) || node.id === selected?.id,
    [highlight, selected]
  );

  const drawNode = useCallback(
    (node, ctx, scale) => {
      if (!Number.isFinite(node.x) || !Number.isFinite(node.y)) return; // not placed yet
      const color = colorForType(node.type);
      const lit = isLit(node);
      const r = nodeRadius(node);
      const glowR = r * (lit ? 5 : 3);

      const glow = ctx.createRadialGradient(node.x, node.y, 0, node.x, node.y, glowR);
      glow.addColorStop(0, color + (lit ? "cc" : "55"));
      glow.addColorStop(1, color + "00");
      ctx.fillStyle = glow;
      ctx.beginPath();
      ctx.arc(node.x, node.y, glowR, 0, 2 * Math.PI);
      ctx.fill();

      ctx.fillStyle = lit ? "#ffffff" : color;
      ctx.beginPath();
      ctx.arc(node.x, node.y, r, 0, 2 * Math.PI);
      ctx.fill();

      if (lit || scale > 1.4 || node.degree >= 3) {
        ctx.font = `${lit ? 600 : 400} ${12 / scale}px Inter, sans-serif`;
        ctx.textAlign = "center";
        ctx.textBaseline = "top";
        ctx.fillStyle = lit ? "#ffffff" : "rgba(226, 232, 240, 0.8)";
        ctx.fillText(node.id, node.x, node.y + r + 3 / scale);
      }
    },
    [isLit]
  );

  const paintPointerArea = useCallback((node, color, ctx) => {
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(node.x, node.y, nodeRadius(node) + 3, 0, 2 * Math.PI);
    ctx.fill();
  }, []);

  // A link glows when it touches the selected star, or joins two highlighted stars.
  const linkLit = (link) => {
    const source = endId(link.source);
    const target = endId(link.target);
    if (selected && (source === selected.id || target === selected.id)) return true;
    return highlight.has(source) && highlight.has(target);
  };

  return (
    <div className="graph-wrap" ref={wrapRef}>
      {size.width > 0 && (
        <ForceGraph2D
          ref={graphRef}
          width={size.width}
          height={size.height}
          graphData={data}
          backgroundColor="rgba(0,0,0,0)"
          nodeCanvasObject={drawNode}
          nodePointerAreaPaint={paintPointerArea}
          nodeLabel={(n) => `${n.id} · ${n.type || "Concept"}`}
          linkLabel={(l) => l.relation}
          linkColor={(l) => (linkLit(l) ? "rgba(255,255,255,0.85)" : "rgba(148,163,184,0.22)")}
          linkWidth={(l) => (linkLit(l) ? 1.6 : 0.8)}
          linkDirectionalArrowLength={3}
          linkDirectionalArrowRelPos={0.9}
          linkDirectionalParticles={(l) => (linkLit(l) ? 3 : 0)}
          linkDirectionalParticleWidth={2}
          linkDirectionalParticleColor={() => "#fde68a"}
          onNodeClick={(node) => setSelected(node)}
          onBackgroundClick={() => setSelected(null)}
          cooldownTicks={120}
          onEngineStop={() => {
            if (!fittedRef.current && data.nodes.length) {
              graphRef.current?.zoomToFit(600, 60);
              fittedRef.current = true;
            }
          }}
        />
      )}

      <div className="graph-toolbar">
        <span className="graph-title">Knowledge sky</span>
        <button type="button" className="ghost-btn" onClick={() => graphRef.current?.zoomToFit(600, 60)}>Fit</button>
        <button type="button" className="ghost-btn" onClick={onRefresh}>Refresh</button>
      </div>

      {types.length > 0 && (
        <ul className="legend">
          {types.map((t) => (
            <li key={t}><span className="dot" style={{ background: colorForType(t) }} />{t}</li>
          ))}
        </ul>
      )}

      {selected && (
        <div className="node-card">
          <button type="button" className="close" onClick={() => setSelected(null)} aria-label="Close">×</button>
          <span className="node-type" style={{ color: colorForType(selected.type) }}>{selected.type || "Concept"}</span>
          <h3>{selected.id}</h3>
          <ul>
            {connections.map((c, i) => (
              <li key={i}>
                {c.outgoing ? "→" : "←"} <em>{c.relation.replaceAll("_", " ").toLowerCase()}</em> {c.other}
              </li>
            ))}
          </ul>
        </div>
      )}

      {error ? (
        <div className="graph-empty">
          <span className="big-star">✧</span>
          <p>{error}</p>
          <button type="button" className="ghost-btn" onClick={onRefresh}>Try again</button>
        </div>
      ) : (
        data.nodes.length === 0 && (
          <div className="graph-empty">
            <span className="big-star">✦</span>
            <p>Your sky is still dark.</p>
            <p className="muted">Upload some notes to light up your first constellation.</p>
          </div>
        )
      )}
    </div>
  );
}
