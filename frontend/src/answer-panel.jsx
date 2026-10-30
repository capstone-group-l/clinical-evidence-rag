import { useState } from "react";
import GenerationMetrics from "./generation-metrics";

/* This component displays the answer and sources for a given question. */
export default function AnswerPanel({ result, startedAt }) {
  // Chunk IDs of the sources that are expanded. Several can be open at once.
  const [expanded, setExpanded] = useState(new Set());

  function toggle(chunkId) {
    setExpanded((previous) => {
      const next = new Set(previous);
      if (next.has(chunkId)) {
        next.delete(chunkId);
      } else {
        next.add(chunkId);
      }
      return next;
    });
  }

  // A citation number only opens its source; the link then scrolls to it.
  function open(chunkId) {
    setExpanded((previous) => new Set(previous).add(chunkId));
  }

  if (result.status === "insufficient_evidence") {
    return (
      <>
        <GenerationMetrics
          tokensUsed={result.tokens_used}
          startedAt={startedAt}
        />
        <p>Insufficient evidence to answer the question.</p>
      </>
    );
  }
  return (
    <>
      <GenerationMetrics
        tokensUsed={result.tokens_used}
        startedAt={startedAt}
      />
      <section aria-labelledby="answer-heading">
        <h2 id="answer-heading">Answer</h2>
        <p>
          {result.answer}{" "}
          {result.citations.map((citation, index) => (
            <a
              key={citation.chunk_id}
              href={`#source-${index + 1}`}
              onClick={() => open(citation.chunk_id)}
            >
              [{index + 1}]
            </a>
          ))}
        </p>
        <h2>Sources</h2>
        <ol className="sources">
          {result.citations.map((citation, index) => {
            const source = result.sources.find(
              (source) => source.chunk.id === citation.chunk_id,
            );
            if (!source) {
              return null;
            }
            const isOpen = expanded.has(citation.chunk_id);
            return (
              <li key={citation.chunk_id} id={`source-${index + 1}`}>
                <button
                  type="button"
                  className="source-toggle"
                  aria-expanded={isOpen}
                  aria-controls={`source-body-${index + 1}`}
                  onClick={() => toggle(citation.chunk_id)}
                >
                  {source.chunk.title}
                </button>
                {isOpen && (
                  <div id={`source-body-${index + 1}`} className="source-body">
                    <dl>
                      <dt>Document</dt>
                      <dd>
                        {source.chunk.source_url ? (
                          <a
                            href={source.chunk.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            {source.chunk.document_id} ↗
                          </a>
                        ) : (
                          source.chunk.document_id
                        )}
                      </dd>
                      <dt>Chunk</dt>
                      <dd>{source.chunk.id}</dd>
                      {source.chunk.publish_date && (
                        <>
                          <dt>Published</dt>
                          <dd>{source.chunk.publish_date}</dd>
                        </>
                      )}
                    </dl>
                    <p>{source.chunk.text}</p>
                  </div>
                )}
              </li>
            );
          })}
        </ol>
      </section>
    </>
  );
}
