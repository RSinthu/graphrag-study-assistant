import axios from "axios";

const client = axios.create({ baseURL: "/api" });

// Normalize errors: FastAPI sends { detail: "..." } or { detail: [{ msg }] }
function handleError(err) {
  if (err.response) {
    const data = err.response.data ?? {};
    const detail = Array.isArray(data.detail) ? data.detail[0]?.msg : data.detail;
    if (detail) throw new Error(detail);
    if (err.response.status >= 500) throw new Error("The backend isn't responding. Is it running on port 8000?");
    throw new Error(`Request failed (${err.response.status})`);
  }
  // Network / no response
  throw new Error("Can't reach the backend. Is it running on port 8000?");
}

export const getGraph = () =>
  client.get("/graph").then((r) => r.data).catch(handleError);

export const askQuestion = (question) =>
  client.post("/ask", { question }).then((r) => r.data).catch(handleError);

export const uploadFile = (file) => {
  const form = new FormData();
  form.append("file", file);
  return client.post("/upload", form).then((r) => r.data).catch(handleError);
};
