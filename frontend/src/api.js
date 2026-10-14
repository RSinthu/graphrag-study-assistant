const BASE = "/api";

async function request(path, options) {
  let response;
  try {
    response = await fetch(BASE + path, options);
  } catch {
    throw new Error("Can't reach the backend. Is it running on port 8000?");
  }

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    // FastAPI sends { detail: "..." } or, for validation errors, { detail: [{ msg }] }
    const detail = Array.isArray(data.detail) ? data.detail[0]?.msg : data.detail;
    if (detail) throw new Error(detail);
    if (response.status >= 500) throw new Error("The backend isn't responding. Is it running on port 8000?");
    throw new Error(`Request failed (${response.status})`);
  }
  return data;
}

export const getGraph = () => request("/graph");

export const askQuestion = (question) =>
  request("/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

export const uploadFile = (file) => {
  const form = new FormData();
  form.append("file", file);
  return request("/upload", { method: "POST", body: form });
};
