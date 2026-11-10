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
      <h1>Clinical Evidence RAG</h1>
      <form onSubmit={handleSubmit}>
        <label htmlFor="question">Clinical Question</label>
        <textarea
          id="question"
          value={question}
          maxLength={500}
          rows={3}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <button type="submit" disabled={loading || question.trim().length < 3}>
          Ask
        </button>
      </form>
      {state.status === "loading" && <p>Searching Evidence...</p>}
      {state.status === "error" && (
        <p>Error occurred while fetching the answer.</p>
      )}
      {state.status === "done" && (
        <AnswerPanel result={state.result} startedAt={startedAt} />
      )}
    </main>
  );
}
