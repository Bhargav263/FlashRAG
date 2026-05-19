import axios from 'axios';

const API_URL = 'http://localhost:8001';

const api = axios.create({
  baseURL: API_URL,
  timeout: 120000, // 2 min for LLM responses
});

/**
 * Upload documents for ingestion.
 * @param {File[]} files
 * @param {{ strategy: string, chunk_size: number, chunk_overlap: number }} opts
 */
export async function uploadDocuments(files, opts) {
  const formData = new FormData();
  files.forEach((f) => formData.append('files', f));
  formData.append('strategy', opts.strategy);
  formData.append('chunk_size', opts.chunk_size);
  formData.append('chunk_overlap', opts.chunk_overlap);

  const res = await api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
}

/** Poll backend ingestion metrics. */
export async function getMetrics() {
  const res = await api.get('/metrics');
  return res.data;
}

/**
 * Send a chat query.
 * @param {string} query
 * @param {string} sessionId
 */
export async function sendChat(query, sessionId) {
  const res = await api.get('/chat', {
    params: { query, session_id: sessionId },
  });
  return res.data;
}

/**
 * Send a chat query and stream the response.
 * @param {string} query
 * @param {string} sessionId
 * @param {function} onChunk
 */
export async function streamChat(query, sessionId, onEvent) {
  const url = new URL(`${API_URL}/chat`);
  url.searchParams.append('query', query);
  if (sessionId) {
    url.searchParams.append('session_id', sessionId);
  }

  const response = await fetch(url.toString(), {
    method: 'GET',
    headers: {
      'Accept': 'text/event-stream',
    }
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Error ${response.status}: ${errorText}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder('utf-8');
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let boundary = buffer.indexOf('\n\n');
    while (boundary !== -1) {
      const message = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 2);

      if (message.startsWith('data: ')) {
        const jsonStr = message.slice(6);
        try {
          const data = JSON.parse(jsonStr);
          onEvent(data);
        } catch (err) {
          console.error("Failed to parse SSE JSON:", err, jsonStr);
        }
      }
      boundary = buffer.indexOf('\n\n');
    }
  }
}
