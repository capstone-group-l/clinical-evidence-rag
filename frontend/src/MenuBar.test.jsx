import { beforeEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import MenuBar from "./MenuBar";
import { useAuth } from "./auth-context";
import { supabase } from "./supabase";

vi.mock("./auth-context", () => ({ useAuth: vi.fn() }));

beforeEach(() => {
  useAuth.mockReturnValue({ session: { user: { email: "a@example.com" } } });
});

function openMenu() {
  render(
    <MemoryRouter>
      <MenuBar />
    </MemoryRouter>,
  );
  fireEvent.click(screen.getByRole("button", { name: "Menu" }));
}

describe("MenuBar", () => {
  test("shows the role at the top for an admin", () => {
    useAuth.mockReturnValue({
      session: { user: { email: "a@example.com" } },
      role: "admin",
    });
    openMenu();
    expect(screen.getByText("admin")).toBeInTheDocument();
  });

  test("shows the Users link for an admin", () => {
    useAuth.mockReturnValue({
      session: { user: { email: "a@example.com" } },
      role: "admin",
    });
    openMenu();
    expect(screen.getByRole("link", { name: "Users" })).toBeInTheDocument();
  });

  test("hides the Users link for a normal user", () => {
    useAuth.mockReturnValue({
      session: { user: { email: "a@example.com" } },
      role: "user",
    });
    openMenu();
    expect(screen.queryByRole("link", { name: "Users" })).toBeNull();
  });

  test("shows no role when the role is unknown", () => {
    openMenu();
    expect(document.querySelector(".menu-role")).toBeNull();
  });

  test("shows the email and links when opened", () => {
    openMenu();
    expect(screen.getByText("a@example.com")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Ask" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Log out" })).toBeInTheDocument();
  });

  test("logs out", () => {
    openMenu();
    fireEvent.click(screen.getByRole("button", { name: "Log out" }));
    expect(supabase.auth.signOut).toHaveBeenCalled();
  });
});
