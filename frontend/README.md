# Frontend

React + Vite UI for the GraphRAG study assistant ("StudyGraph").

## Run

```bash
npm install
npm run dev
```

Open http://localhost:5174. The backend must be running on port 8000;
Vite forwards `/api/*` to it (see `vite.config.js`).

## Structure

| File | What it does |
|---|---|
| `src/api.js` | Calls `/upload`, `/ask`, `/graph` |
| `src/App.jsx` | Layout and shared state; lights up stars named in an answer |
| `src/components/UploadZone.jsx` | Drag-and-drop upload |
| `src/components/ChatPanel.jsx` | Chat with route badge (graph / note search) and sources |
| `src/components/GraphView.jsx` | Knowledge graph drawn as a star map (react-force-graph-2d) |
| `src/styles.css` | Night-sky theme |
