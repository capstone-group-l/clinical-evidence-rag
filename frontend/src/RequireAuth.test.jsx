import { describe, expect, test, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import RequireAuth from "./RequireAuth";
import { useAuth } from "./auth-context";

vi.mock("./auth-context", () => ({ useAuth: vi.fn() }));

function renderHome() {
  render(
    <MemoryRouter initialEntries={["/"]}>
      <Routes>
        <Route path="/login" element={<p>Login page</p>} />
        <Route
          path="/"
          element={
            <RequireAuth>
              <p>Ask page</p>
            </RequireAuth>
          }
        />
      </Routes>
    </MemoryRouter>,
  );
}

describe("RequireAuth", () => {
  test("sends signed-out users to the login page", () => {
    useAuth.mockReturnValue({ session: null, loading: false });
    renderHome();
    expect(screen.getByText("Login page")).toBeInTheDocument();
  });

  test("shows the page to signed-in users", () => {
    useAuth.mockReturnValue({ session: { access_token: "t" }, loading: false });
    renderHome();
    expect(screen.getByText("Ask page")).toBeInTheDocument();
  });
});
