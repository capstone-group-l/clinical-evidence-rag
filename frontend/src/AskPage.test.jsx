// Tests for the AskPage component (clinical question form). Uses Vitest and React Testing Library.
import { afterEach, describe, expect, test, vi } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import AskPage from "./AskPage";
import { useAuth } from "./auth-context";

vi.mock("./auth-context", () => ({ useAuth: vi.fn() }));
useAuth.mockReturnValue({
  session: { user: { user_metadata: { display_name: "Juan del Pueblo" } } },
});

afterEach(() => {
  cleanup();
});

describe("Clinical query page", () => {
  test("greets the user by name", () => {
    render(<AskPage />);
    expect(screen.getByText("Hello, Juan del Pueblo")).toBeInTheDocument();
  });

  test("renders the clinical question form", () => {
    render(<AskPage />);

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
    render(<AskPage />);

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
    render(<AskPage />);

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
