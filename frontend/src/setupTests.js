// Whenever we run frontend tests, give Vitest access to pretend browser DOM APIs which are provided by jsdom. This is necessary for React Testing Library to work properly.
import "@testing-library/jest-dom/vitest";
