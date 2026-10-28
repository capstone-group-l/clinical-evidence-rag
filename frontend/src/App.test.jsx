// This is a test file for the App component. It uses Vitest and React Testing Library to test the backend health check functionality of the App.
import { afterEach, describe, expect, test } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import App from "./App";

afterEach(() => {
  cleanup();
});

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
});
