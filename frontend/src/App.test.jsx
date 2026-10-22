// This is a test file for the App component. It uses Vitest and React Testing Library to test the backend health check functionality of the App.
import { afterEach, describe, expect, test, vi } from "vitest";
import { cleanup, render, screen } from "@testing-library/react";
import App from "./App";

// This function basically resets the testing environment after each test. It cleans up the DOM and restores any mocked functions to their original implementations.
afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

// This function is a placeholder for the actual backend health check function. It simulates a successful response from the backend.
describe("App backend health check", () => {
  test("shows the backend version when the health request succeeds", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({
        status: "ok",
        version: "1.0.0",
      }),
    });

    render(<App />); // Pretends to render the App component in a test environment.

    expect(screen.getByText("Checking the backend...")).toBeInTheDocument();

    expect(
      await screen.findByText("Backend is up and running (version 1.0.0)"),
    ).toBeInTheDocument();
  });

  // This function tests the behavior of the App component when the backend health check request fails. It simulates a network error and checks if the appropriate error message is displayed.
  test("shows an error when the backend request fails", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(
      // When App tries to fetch the backend health check, it will simulate a network error by rejecting the promise with a new Error.
      new Error("Network unavailable"), // This is the error message that will be thrown when the fetch request fails. It simulates a network failure scenario for testing purposes.
    );

    render(<App />);

    expect(
      await screen.findByText(
        "Backend check failed: Network unavailable", // This checks if the error message is displayed in the document when the backend request fails.
      ),
    ).toBeInTheDocument();
  });
});
