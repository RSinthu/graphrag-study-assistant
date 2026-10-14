import { useEffect, useRef, useState } from "react";
import { askQuestion } from "../api.js";

const SUGGESTIONS = [
  "What are the main topics in my notes?",
  "How are the key concepts connected?",
  "Explain the most important idea simply",
];

const ROUTE_LABELS = {
  graph: "🔗 Graph search",
  vector: "📄 Note search",
};

export default function ChatPanel({ onAnswer }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const listRef = useRef(null);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  async function ask(question) {
    const text = question.trim();
    if (!text || loading) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", text }]);
    setLoading(true);
    try {
      const result = await askQuestion(text);
      setMessages((m) => [...m, { role: "assistant", text: result.answer, ...result }]);
      onAnswer(result.answer);
    } catch (error) {
      setMessages((m) => [...m, { role: "error", text: error.message }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card chat-card">
      <h2 className="card-title">Ask your notes</h2>

      <div className="messages" ref={listRef}>
        {messages.length === 0 && (
          <div className="suggestions">
            <p>Try asking:</p>
            {SUGGESTIONS.map((s) => (
              <button key={s} type="button" className="chip" onClick={() => ask(s)}>
                {s}
              </button>
            ))}
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`bubble bubble-${m.role}`}>
            <p>{m.text}</p>
            {m.role === "assistant" && (
              <div className="meta">
                <span className={`badge badge-${m.route}`}>{ROUTE_LABELS[m.route]}</span>
                {m.retries > 0 && <span className="badge">↻ rephrased {m.retries}×</span>}
                {m.sources.length > 0 && (
                  <details>
                    <summary>Sources ({m.sources.length})</summary>
                    <ul>
                      {m.sources.map((s) => <li key={s}>{s}</li>)}
                    </ul>
                  </details>
                )}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="bubble bubble-assistant thinking">
            Tracing constellations<span className="dots"><i>.</i><i>.</i><i>.</i></span>
          </div>
        )}
      </div>

      <form className="ask-form" onSubmit={(e) => { e.preventDefault(); ask(input); }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask anything about your notes…"
          maxLength={2000}
          aria-label="Your question"
        />
        <button type="submit" disabled={loading || !input.trim()} aria-label="Send">➤</button>
      </form>
    </div>
  );
}
