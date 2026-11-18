import { useState } from "react";
import { askQuestion } from "./api";
import AnswerPanel from "./answer-panel";
import { useAuth } from "./auth-context";

const MAX_LENGTH = 500;

export default function AskPage() {
  const { session } = useAuth();
  const name = session?.user?.user_metadata?.display_name?.trim();
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
      {name && <p className="greeting">Hello, {name}</p>}
      <div className="intro">
        <p>
          Ask a clinical question in plain English and get an answer drawn from
          the indexed medical evidence, with numbered citations to the sources
          it used.
        </p>
        <ul>
          <li>Be specific and concise. Avoid vague quesitons.</li>
          <li>Type your question below and press Ask.</li>
          <li>Click a citation number or source title to read the evidence.</li>
        </ul>
      </div>

      <form className="query-form" onSubmit={handleSubmit}>
        <label htmlFor="question">Clinical Question</label>
        <textarea
          id="question"
          value={question}
          maxLength={MAX_LENGTH}
          rows={3}
          placeholder="e.g. What are the risks of long-term PPI use?"
          readOnly={loading}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <div className="form-footer">
          <span className="char-count">
            {question.length}/{MAX_LENGTH}
          </span>
          <button
            type="submit"
            className="ask-button"
            disabled={loading || question.trim().length < 3}
          >
            {loading && <span className="spinner" />}
            {loading ? "Searching..." : "Ask"}
          </button>
        </div>
      </form>

      {state.status === "error" && (
        <div className="status status-error">
          <p>
            Something went wrong while fetching the answer. Please try again.
          </p>
        </div>
      )}

      {state.status === "done" && (
        <AnswerPanel result={state.result} startedAt={startedAt} />
      )}
    </main>
  );
}
