import { useEffect, useRef, useState } from "react";
import GenerationMetrics from "./generation-metrics";

/* This component displays the answer and sources for a given question. */
export default function AnswerPanel({ result, startedAt }) {
  const [expanded, setExpanded] = useState(new Set());

  const scrollTarget = useRef(null);

  useEffect(() => {
    if (scrollTarget.current === null) {
      return;
    }
    const sourceElement = document.getElementById(
      `source-${scrollTarget.current}`,
    );
    sourceElement?.scrollIntoView({ block: "start" });
    scrollTarget.current = null;
  }, [expanded]);

  function toggle(number) {
    setExpanded((previous) => {
      const next = new Set(previous);
      if (next.has(number)) {
        next.delete(number);
      } else {
        next.add(number);
      }
      return next;
    });
  }

  // A citation number opens its source, then scrolls to it.
  function openCitation(event, number) {
    event.preventDefault();
    scrollTarget.current = number;
    setExpanded((previous) => new Set(previous).add(number));
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
          {result.citations.map((citation, index) => {
            const number = index + 1;
            return (
              <a
                key={number}
                className="citation"
                href={`#source-${number}`}
                onClick={(event) => openCitation(event, number)}
              >
                [{number}]
              </a>
            );
          })}
        </p>
        <h2>Sources</h2>
        <ul className="sources">
          {result.citations.map((citation, index) => {
            const number = index + 1;
            const source = result.sources.find(
              (source) => source.chunk.id === citation.chunk_id,
            );
            if (!source) {
              return null;
            }
            const isOpen = expanded.has(number);
            const bodyId = `source-body-${number}`;
            return (
              <li key={number} id={`source-${number}`} className="source-item">
                <button
                  type="button"
                  className="source-toggle"
                  aria-expanded={isOpen}
                  aria-controls={bodyId}
                  onClick={() => toggle(number)}
                >
                  <span className="source-numbers">[{number}]</span>{" "}
                  {source.chunk.title}
                </button>
                {isOpen && (
                  <div id={bodyId} className="source-body">
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
        </ul>
      </section>
    </>
  );
}
