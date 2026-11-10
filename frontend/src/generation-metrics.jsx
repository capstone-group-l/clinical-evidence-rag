import { useEffect, useState } from "react";

export default function GenerationMetrics({ tokensUsed, startedAt }) {
  const [elapsedMs, setElapsedMs] = useState(null);

  useEffect(() => {
    const frame = requestAnimationFrame(() => {
      setElapsedMs(Math.max(0, performance.now() - startedAt));
    });
    return () => cancelAnimationFrame(frame);
  }, [startedAt]);

  return (
    <dl className="generation-metrics" aria-label="Generation metrics">
      <div>
        <dt>OpenAI tokens</dt>
        <dd>{tokensUsed ?? "Unavailable"}</dd>
      </div>
      <div>
        <dt>Time taken</dt>
        <dd>
          {elapsedMs === null
            ? "Calculating..."
            : `${(elapsedMs / 1000).toFixed(2)}s`}
        </dd>
      </div>
    </dl>
  );
}
