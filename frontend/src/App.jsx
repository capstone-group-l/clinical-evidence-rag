import { useEffect, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export default function App() {
  const [status, setStatus] = useState("Checking the backend...");

  useEffect(() => {
    async function checkBackend() {
      try {
        const response = await fetch(`${API_URL}/v1/health`);
        if (!response.ok) {
          throw new Error(`Server responded with ${response.status}`);
        }

        const health = await response.json();
        setStatus(`Backend is up and running (version ${health.version})`);
      } catch (error) {
        setStatus(`Backend check failed: ${error.message}`);
      }
    }

    checkBackend();
  }, []);

  return (
    <main>
      <h1>Clinical Evidence RAG</h1>
      <p>{status}</p>
    </main>
  );
}
