// This is a test file for the App component, specifically for accessibility testing. It uses Vitest and React Testing Library to test the frontend accessibility of the App.
import { afterEach, describe, expect, test, vi } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import axe from "axe-core";

import App from "./App";
import { askQuestion } from "./api";

vi.mock("./api", () => ({
  askQuestion: vi.fn(),
}));

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe("Frontend accessibility", () => {
  test("query page has no detected accessibility violations", async () => {
    const { container } = render(<App />);

    const results = await axe.run(container);

    expect(results.violations).toEqual([]);
  });

  test("answer and source UI has no detected accessibility violations", async () => {
    askQuestion.mockResolvedValueOnce({
      status: "answered",
      answer: "This is a test clinical answer.",
      tokens_used: 100,
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
            title: "Example Clinical Evidence Source",
            source_url: "https://example.com/PMC100",
            publish_date: "2026-01-01",
            text: "Example supporting evidence passage.",
          },
        },
      ],
    });

    const { container } = render(<App />);

    fireEvent.change(screen.getByLabelText("Clinical Question"), {
      target: {
        value: "What is hypertension?",
      },
    });

    fireEvent.click(
      screen.getByRole("button", {
        name: "Ask",
      }),
    );

    expect(
      await screen.findByText("This is a test clinical answer."),
    ).toBeInTheDocument();

    const results = await axe.run(container);

    expect(results.violations).toEqual([]);
  });

  test("source control exposes its expanded state", async () => {
    askQuestion.mockResolvedValueOnce({
      status: "answered",
      answer: "This is a test clinical answer.",
      tokens_used: 100,
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
            title: "Example Clinical Evidence Source",
            source_url: "https://example.com/PMC100",
            publish_date: "2026-01-01",
            text: "Example supporting evidence passage.",
          },
        },
      ],
    });

    render(<App />);

    fireEvent.change(screen.getByLabelText("Clinical Question"), {
      target: {
        value: "What is hypertension?",
      },
    });

    fireEvent.click(
      screen.getByRole("button", {
        name: "Ask",
      }),
    );

    const sourceButton = await screen.findByRole("button", {
      name: "Example Clinical Evidence Source",
    });

    expect(sourceButton).toHaveAttribute("aria-expanded", "false");

    fireEvent.click(sourceButton);

    expect(sourceButton).toHaveAttribute("aria-expanded", "true");

    expect(
      screen.getByText("Example supporting evidence passage."),
    ).toBeInTheDocument();
  });
});
