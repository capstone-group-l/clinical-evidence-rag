const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

/* This function sends a question to the backend API and returns the response. */
export async function askQuestion(question) {
  const response = await fetch(`${API_URL}/v1/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question }),
  });
  if (!response.ok) {
    throw new Error(`Server responded with ${response.status}`);
  }
  return response.json();
}
