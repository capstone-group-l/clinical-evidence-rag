import { useState } from "react";
import { askQuestion } from "./api";
import AnswerPanel from "./answer-panel";

export default function App() {
  const [question, setQuestion] = useState("");
  const [state, setState] = useState({ status: "idle" });
  const [startedAt, setStartedAt] = useState(null);
  const loading = state.status === "loading";

  async function handleSubmit(event) {
    event.preventDefault();
    const requestStartedAt = performance.now();
    setStartedAt(requestStartedAt);
    setState({ status: "loading" });
    try {
      const result = await askQuestion(question.trim());
      setState({ status: "done", result });
    } catch {
      setState({ status: "error" });
    }
  }

  return (
    <main>
      <header className="masthead">
        <h1>Clinical Evidence RAG</h1>
        <p>Research and education only. Not for clinical decisions.</p>
      </header>
      <form className="ask" onSubmit={handleSubmit}>
        <label htmlFor="question">Clinical Question</label>
        <textarea
          id="question"
          value={question}
          maxLength={500}
          rows={4}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <div className="ask-actions">
          <button
            type="submit"
            disabled={loading || question.trim().length < 3}
          >
            Ask
          </button>
        </div>
      </form>
      {state.status === "loading" && (
        <p className="status status-loading">Searching the evidence…</p>
      )}
      {state.status === "error" && (
        <p className="status" role="alert">
          The answer could not be loaded. Try again.
        </p>
      )}
      {state.status === "done" && (
        <AnswerPanel result={state.result} startedAt={startedAt} />
      )}
    </main>
  );
}
