import { useCallback, useEffect, useState } from "react";
import { getGraph } from "./api.js";
import UploadZone from "./components/UploadZone.jsx";
import ChatPanel from "./components/ChatPanel.jsx";
import GraphView from "./components/GraphView.jsx";

// Backend sends { nodes, edges }; the graph library wants { nodes, links }.
function toGraphData({ nodes, edges }) {
  const ids = new Set(nodes.map((n) => n.id));
  const links = edges.filter((e) => ids.has(e.source) && ids.has(e.target)).map((e) => ({ ...e }));
  const degree = {};
  for (const link of links) {
    degree[link.source] = (degree[link.source] || 0) + 1;
    degree[link.target] = (degree[link.target] || 0) + 1;
  }
  return { nodes: nodes.map((n) => ({ ...n, degree: degree[n.id] || 0 })), links };
}

export default function App() {
  const [graph, setGraph] = useState({ nodes: [], links: [] });
  const [graphError, setGraphError] = useState("");
  const [highlight, setHighlight] = useState(new Set());

  const loadGraph = useCallback(async () => {
    try {
      setGraph(toGraphData(await getGraph()));
      setGraphError("");
    } catch (error) {
      setGraphError(error.message);
    }
  }, []);

  useEffect(() => {
    loadGraph();
  }, [loadGraph]);

  // Light up the stars that the answer talks about.
  function handleAnswer(answer) {
    const text = answer.toLowerCase();
    const named = graph.nodes.filter((n) => n.id.length > 2 && text.includes(n.id.toLowerCase()));
    setHighlight(new Set(named.map((n) => n.id)));
  }

  return (
    <div className="app">
      <div className="sky" aria-hidden="true" />

      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">✦</span>
          <span>StudyGraph</span>
        </div>
        <div className="stats">
          <span><b>{graph.nodes.length}</b> stars</span>
          <span><b>{graph.links.length}</b> links</span>
        </div>
      </header>

      <main className="layout">
        <aside className="sidebar">
          <UploadZone onUploaded={loadGraph} />
          <ChatPanel onAnswer={handleAnswer} />
        </aside>
        <section className="graph-card">
          <GraphView data={graph} highlight={highlight} error={graphError} onRefresh={loadGraph} />
        </section>
      </main>
    </div>
  );
}
