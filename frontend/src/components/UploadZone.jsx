import { useRef, useState } from "react";
import { uploadFile } from "../api.js";

const ACCEPTED = ".pdf,.txt,.md";

export default function UploadZone({ onUploaded }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const [status, setStatus] = useState({ state: "idle" }); // idle | uploading | done | error

  async function handleFile(file) {
    if (!file || status.state === "uploading") return;
    setStatus({ state: "uploading", name: file.name });
    try {
      const result = await uploadFile(file);
      setStatus({ state: "done", result });
      onUploaded();
    } catch (error) {
      setStatus({ state: "error", message: error.message });
    }
  }

  function onDrop(event) {
    event.preventDefault();
    setDragging(false);
    handleFile(event.dataTransfer.files[0]);
  }

  const uploading = status.state === "uploading";

  return (
    <div className="card upload-card">
      <h2 className="card-title">Add notes</h2>

      <button
        type="button"
        className={`dropzone ${dragging ? "is-dragging" : ""} ${uploading ? "is-busy" : ""}`}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        disabled={uploading}
      >
        {uploading ? (
          <>
            <span className="orbit" aria-hidden="true"><span /></span>
            <span className="dropzone-main">Mapping “{status.name}”</span>
            <span className="dropzone-sub">Finding concepts and how they connect. Larger files take a minute.</span>
          </>
        ) : (
          <>
            <span className="dropzone-icon" aria-hidden="true">☄</span>
            <span className="dropzone-main">Drop a file or click to browse</span>
            <span className="dropzone-sub">PDF, TXT or Markdown</span>
          </>
        )}
      </button>

      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED}
        hidden
        onChange={(e) => { handleFile(e.target.files[0]); e.target.value = ""; }}
      />

      {status.state === "done" && (
        <p className="notice notice-ok">
          ✦ <b>{status.result.filename}</b>: {status.result.nodes} stars, {status.result.relationships} links from{" "}
          {status.result.chunks} chunks
        </p>
      )}
      {status.state === "error" && <p className="notice notice-error">{status.message}</p>}
    </div>
  );
}
