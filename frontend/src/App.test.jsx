// This is a test file for the App component.
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";

import App from "./App";
import { askQuestion } from "./api";

vi.mock("./api", () => ({
  askQuestion: vi.fn(),
}));

beforeEach(() => {
  vi.clearAllMocks();
});

afterEach(() => {
  cleanup();
});

function submitQuestion(question = "What is hypertension?") {
  render(<App />);

  const questionBox = screen.getByLabelText("Clinical Question");
  const askButton = screen.getByRole("button", {
    name: "Ask",
  });

  fireEvent.change(questionBox, {
    target: {
      value: question,
    },
  });

  fireEvent.click(askButton);

  return {
    questionBox,
    askButton,
  };
}

const successfulResponse = {
  status: "answered",
  answer:
    "Reduced expression of the OprD porin is a common mechanism of carbapenem resistance.",
  tokens_used: 1200,
  citations: [
    {
      chunk_id: "PMC100:0001",
    },
  ],
  sources: [
    {
      chunk: {
        id: "PMC100:0001",
        document_id: "PMC100",
        title: "Carbapenem Resistance in Pseudomonas aeruginosa",
        source_url: "https://example.com/PMC100",
        publish_date: "2026-01-15",
        text: "OprD loss or reduced expression contributes to carbapenem resistance.",
      },
    },
  ],
};

describe("Clinical query page", () => {
  test("renders the clinical question form", () => {
    render(<App />);

    expect(
      screen.getByRole("heading", {
        name: "Clinical Evidence RAG",
      }),
    ).toBeInTheDocument();

    expect(screen.getByLabelText("Clinical Question")).toBeInTheDocument();

    expect(
      screen.getByRole("button", {
        name: "Ask",
      }),
    ).toBeInTheDocument();
  });

  test("Ask button is disabled when the question is too short", () => {
    render(<App />);

    const questionBox = screen.getByLabelText("Clinical Question");

    const askButton = screen.getByRole("button", {
      name: "Ask",
    });

    expect(askButton).toBeDisabled();

    fireEvent.change(questionBox, {
      target: {
        value: "Hi",
      },
    });

    expect(askButton).toBeDisabled();
  });

  test("Ask button becomes enabled for a valid question", () => {
    render(<App />);

    const questionBox = screen.getByLabelText("Clinical Question");

    const askButton = screen.getByRole("button", {
      name: "Ask",
    });

    fireEvent.change(questionBox, {
      target: {
        value: "What is hypertension?",
      },
    });

    expect(askButton).toBeEnabled();
  });

  test("shows a loading state while waiting for an answer", () => {
    askQuestion.mockReturnValueOnce(new Promise(() => {}));

    const { askButton } = submitQuestion();

    expect(screen.getByText("Searching Evidence...")).toBeInTheDocument();

    expect(askButton).toBeDisabled();
  });

  test("displays a successful answer and its source", async () => {
    askQuestion.mockResolvedValueOnce(successfulResponse);

    submitQuestion("What causes carbapenem resistance?");

    expect(
      await screen.findByText(successfulResponse.answer),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("link", {
        name: "[1]",
      }),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("button", {
        name: "Carbapenem Resistance in Pseudomonas aeruginosa",
      }),
    ).toBeInTheDocument();
  });

  test("displays multiple returned sources", async () => {
    const multipleSourceResponse = {
      status: "answered",
      answer: "The answer is supported by multiple retrieved passages.",
      tokens_used: 900,
      citations: [
        {
          chunk_id: "PMC200:0001",
        },
        {
          chunk_id: "PMC300:0002",
        },
      ],
      sources: [
        {
          chunk: {
            id: "PMC200:0001",
            document_id: "PMC200",
            title: "Clinical Evidence Study One",
            source_url: "https://example.com/PMC200",
            publish_date: "2026-02-01",
            text: "Supporting passage from the first source.",
          },
        },
        {
          chunk: {
            id: "PMC300:0002",
            document_id: "PMC300",
            title: "Clinical Evidence Study Two",
            source_url: "https://example.com/PMC300",
            publish_date: "2026-03-01",
            text: "Supporting passage from the second source.",
          },
        },
      ],
    };

    askQuestion.mockResolvedValueOnce(multipleSourceResponse);

    submitQuestion("What evidence supports this treatment?");

    expect(
      await screen.findByText(multipleSourceResponse.answer),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("button", {
        name: "Clinical Evidence Study One",
      }),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("button", {
        name: "Clinical Evidence Study Two",
      }),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("link", {
        name: "[1]",
      }),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("link", {
        name: "[2]",
      }),
    ).toBeInTheDocument();
  });

  test("displays the insufficient evidence state", async () => {
    askQuestion.mockResolvedValueOnce({
      status: "insufficient_evidence",
      answer: "",
      tokens_used: 650,
      citations: [],
      sources: [],
    });

    submitQuestion("What is an unsupported medical question?");

    expect(
      await screen.findByText("Insufficient evidence to answer the question."),
    ).toBeInTheDocument();
  });

  test("displays an error when the API request fails", async () => {
    askQuestion.mockRejectedValueOnce(new Error("Network unavailable"));

    submitQuestion();

    expect(
      await screen.findByText("Error occurred while fetching the answer."),
    ).toBeInTheDocument();
  });

  test("sends the trimmed question to the API", async () => {
    askQuestion.mockResolvedValueOnce(successfulResponse);

    submitQuestion("   What is hypertension?   ");

    expect(askQuestion).toHaveBeenCalledWith("What is hypertension?");

    expect(
      await screen.findByText(successfulResponse.answer),
    ).toBeInTheDocument();
  });
});
