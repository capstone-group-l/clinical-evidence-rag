// Whenever we run frontend tests, give Vitest access to pretend browser DOM APIs which are provided by jsdom. This is necessary for React Testing Library to work properly.
import "@testing-library/jest-dom/vitest";

import { vi } from "vitest";

vi.mock("./supabase", () => ({
  supabase: {
    auth: {
      signOut: vi.fn(),
      signInWithPassword: vi.fn(),
      signUp: vi.fn(),
    },
  },
}));

import { afterEach } from "vitest";
import { cleanup } from "@testing-library/react";

afterEach(() => cleanup());
