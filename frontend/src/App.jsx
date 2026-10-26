import { useCallback, useRef, useState } from "react";
import { askQuestion } from "./api";
import AnswerPanel from "./answer-panel";

export default function App() {
  const [question, setQuestion] = useState("");
  const [state, setState] = useState({ status: "idle" });
  const [elapsedMs, setElapsedMs] = useState(null);
  const startedAt = useRef(null);
  const loading = state.status === "loading";

  async function handleSubmit(event) {
    event.preventDefault();
    startedAt.current = performance.now();
    setState({ status: "loading" });
    setElapsedMs(null);
    try {
      const result = await askQuestion(question.trim());
      setState({
        status: "done",
        result: result,
      });
    } catch {
      setState({ status: "error" });
    }
  }

  const handleAnswerShown = useCallback(() => {
    if (startedAt.current !== null) {
      setElapsedMs(performance.now() - startedAt.current);
    }
  }, []);

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
        <AnswerPanel
          result={state.result}
          elapsedMs={elapsedMs}
          onShown={handleAnswerShown}
        />
      )}
    </main>
  );
}
