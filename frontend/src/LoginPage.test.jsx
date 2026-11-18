import { afterEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import LoginPage from "./LoginPage";
import { useAuth } from "./auth-context";
import { supabase } from "./supabase";

vi.mock("./auth-context", () => ({ useAuth: vi.fn() }));
useAuth.mockReturnValue({ session: null, loading: false });

function renderLogin() {
  render(
    <MemoryRouter initialEntries={["/login"]}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<p>Ask page</p>} />
      </Routes>
    </MemoryRouter>,
  );
}

function fill(label, value) {
  fireEvent.change(screen.getByLabelText(label), { target: { value } });
}

afterEach(() => vi.clearAllMocks());

describe("LoginPage", () => {
  test("shows an error when the login fails", async () => {
    supabase.auth.signInWithPassword.mockResolvedValue({
      error: { code: "invalid_credentials", status: 400 },
    });
    renderLogin();
    fill("Email", "a@example.com");
    fill("Password", "wrong-password");
    fireEvent.click(screen.getByRole("button", { name: "Log in" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Wrong email or password.",
    );
  });

  test("goes to the Ask page after logging in", async () => {
    supabase.auth.signInWithPassword.mockResolvedValue({ error: null });
    renderLogin();
    fill("Email", "a@example.com");
    fill("Password", "secret123");
    fireEvent.click(screen.getByRole("button", { name: "Log in" }));
    expect(await screen.findByText("Ask page")).toBeInTheDocument();
  });

  test("asks the user to confirm their email after signing up", async () => {
    supabase.auth.signUp.mockResolvedValue({ error: null });
    renderLogin();
    fireEvent.click(screen.getByRole("button", { name: /sign up/i }));
    fill("Name", "Juan del Pueblo");
    fill("Email", "a@example.com");
    fill("Password", "secret123");
    fill("Confirm password", "secret123");
    fireEvent.click(screen.getByRole("button", { name: "Sign up" }));
    expect(await screen.findByText(/check your email/i)).toBeInTheDocument();
  });

  test("shows an error when the passwords do not match", async () => {
    renderLogin();
    fireEvent.click(screen.getByRole("button", { name: /sign up/i }));
    fill("Name", "Juan del Pueblo");
    fill("Email", "a@example.com");
    fill("Password", "secret123");
    fill("Confirm password", "different123");
    fireEvent.click(screen.getByRole("button", { name: "Sign up" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Passwords do not match.",
    );
    expect(supabase.auth.signUp).not.toHaveBeenCalled();
  });
});
