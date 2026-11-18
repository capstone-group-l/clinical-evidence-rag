import { describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import MenuBar from "./MenuBar";
import { useAuth } from "./auth-context";
import { supabase } from "./supabase";

vi.mock("./auth-context", () => ({ useAuth: vi.fn() }));
useAuth.mockReturnValue({ session: { user: { email: "a@example.com" } } });

describe("MenuBar", () => {
  test("shows the email and links when opened", () => {
    render(
      <MemoryRouter>
        <MenuBar />
      </MemoryRouter>,
    );
    fireEvent.click(screen.getByRole("button", { name: "Menu" }));
    expect(screen.getByText("a@example.com")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Ask" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Log out" })).toBeInTheDocument();
  });

  test("logs out", () => {
    render(
      <MemoryRouter>
        <MenuBar />
      </MemoryRouter>,
    );
    fireEvent.click(screen.getByRole("button", { name: "Menu" }));
    fireEvent.click(screen.getByRole("button", { name: "Log out" }));
    expect(supabase.auth.signOut).toHaveBeenCalled();
  });
});
