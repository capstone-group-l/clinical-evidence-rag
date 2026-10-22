/* This component displays the answer and sources for a given question. */
export default function AnswerPanel({ result }) {
  if (result.status === "insufficient_evidence") {
    return <p>Insufficient evidence to answer the question.</p>;
  }
  return (
    <section aria-labelledby="answer-heading">
      <h2 id="answer-heading">Answer</h2>
      <p>
        {result.answer}{" "}
        {result.citations.map((citation, index) => (
          <a key={citation.chunk_id} href={`#source-${index + 1}`}>
            [{index + 1}]
          </a>
        ))}
      </p>
      <h2>Sources</h2>
      <ol>
        {result.citations.map((citation, index) => {
          const source = result.sources.find(
            (source) => source.chunk_id === citation.chunk_id,
          );
          if (!source) {
            return null;
          }
          return (
            <li key={citation.chunk_id} id={`source-${index + 1}`}>
              <strong>{source.chunk.title}</strong> ({citation.chunk_id})
              <p>{source.chunk.text}</p>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
