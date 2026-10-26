export default function GenerationMetrics({ tokenCount, elapsedMs }) {
  const metrics = [
    tokenCount == null
      ? null
      : { label: "OpenAI tokens", value: tokenCount.toLocaleString() },
    elapsedMs == null
      ? null
      : { label: "Time taken", value: `${(elapsedMs / 1000).toFixed(2)}s` },
  ].filter(Boolean);

  if (metrics.length === 0) {
    return null;
  }

  return (
    <dl className="generation-metrics" aria-label="Generation metrics">
      {metrics.map((metric) => (
        <div key={metric.label}>
          <dt>{metric.label}</dt>
          <dd>{metric.value}</dd>
        </div>
      ))}
    </dl>
  );
}
