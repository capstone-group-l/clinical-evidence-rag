import { beforeEach, describe, expect, test, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import UsersPage from "./UsersPage";
import { useAuth } from "./auth-context";
import { getUsers } from "./api";

vi.mock("./auth-context", () => ({ useAuth: vi.fn() }));
vi.mock("./api", () => ({ getUsers: vi.fn() }));

function makeUsers(count, start = 0) {
  return Array.from({ length: count }, (_, i) => ({
    user_id: String(start + i),
    email: `user${start + i}@example.com`,
    role: "user",
    status: "approved",
  }));
}

beforeEach(() => {
  useAuth.mockReturnValue({ session: { access_token: "token" } });
  getUsers.mockImplementation((_token, page) =>
    Promise.resolve({
      users: page === 1 ? makeUsers(25) : makeUsers(5, 25),
      total: 30,
      page,
      page_size: 25,
    }),
  );
});

describe("UsersPage", () => {
  test("shows the first 25 users", async () => {
    render(<UsersPage />);
    expect(await screen.findByText("user0@example.com")).toBeInTheDocument();
    expect(screen.getAllByRole("row")).toHaveLength(26);
    expect(screen.getByText("Page 1 of 2 - 30 users")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Previous" })).toBeDisabled();
  });

  test("goes to the next page", async () => {
    render(<UsersPage />);
    await screen.findByText("user0@example.com");
    fireEvent.click(screen.getByRole("button", { name: "Next" }));
    expect(await screen.findByText("user25@example.com")).toBeInTheDocument();
    expect(getUsers).toHaveBeenLastCalledWith("token", 2);
    expect(screen.getByRole("button", { name: "Next" })).toBeDisabled();
  });

  test("shows an error when loading fails", async () => {
    getUsers.mockRejectedValue(new Error("403"));
    render(<UsersPage />);
    expect(
      await screen.findByText("Could not load users."),
    ).toBeInTheDocument();
  });
});
