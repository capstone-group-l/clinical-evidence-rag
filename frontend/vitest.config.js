// This is the Vitest configuration file for the frontend. It sets up the testing environment and includes necessary plugins for React testing.
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: "./src/setupTests.js",
  },
});
