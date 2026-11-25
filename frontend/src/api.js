const API_URL = import.meta.env.VITE_API_URL;

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

export async function isPipelineReady() {
  const response = await fetch(`${API_URL}/v1/ready`);
  return response.ok;
}

export async function getMe(accessToken) {
  const response = await fetch(`${API_URL}/v1/me`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
  if (!response.ok) {
    return null;
  }
  return response.json();
}

export async function getUsers(accessToken, page) {
  const response = await fetch(`${API_URL}/v1/admin/users?page=${page}`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
  if (!response.ok) {
    throw new Error(`Server responded with ${response.status}`);
  }
  return response.json();
}
