import axios from 'axios';
import type { Document, ChatMessage, SourceChunk } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_URL,
});

export const api = {
  async uploadDocument(file: File, onProgress?: (progress: number) => void): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);
    const { data } = await apiClient.post<Document>('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percentCompleted);
        }
      },
    });
    return data;
  },

  async getDocuments(): Promise<Document[]> {
    const { data } = await apiClient.get<Document[]>('/documents');
    return data;
  },

  async deleteDocument(id: string): Promise<void> {
    await apiClient.delete(`/documents/${id}`);
  },

  streamMessage(
    params: { query: string; document_ids: string[]; session_id: string; history: ChatMessage[] },
    onChunk: (text: string) => void,
    onSources: (sources: SourceChunk[]) => void,
    onDone: () => void,
    onError: (err: string) => void
  ): () => void {
    const abortController = new AbortController();

    const fetchStream = async () => {
      try {
        const response = await fetch(`${API_URL}/chat/stream`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(params),
          signal: abortController.signal,
        });

        if (!response.ok) {
          throw new Error('Failed to start chat streaming');
        }

        const reader = response.body?.pipeThrough(new TextDecoderStream()).getReader();
        if (!reader) throw new Error('No reader available');

        let buffer = '';

        while (true) {
          const { value, done } = await reader.read();
          if (done) break;

          buffer += value;
          const lines = buffer.split('\n\n');
          buffer = lines.pop() || ''; // keep the incomplete part

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              if (data === '[DONE]') {
                onDone();
                return;
              } else if (data.startsWith('[SOURCES]')) {
                const sourcesStr = data.slice(9);
                try {
                  const sources = JSON.parse(sourcesStr);
                  onSources(sources);
                } catch (e) {
                  console.error('Failed to parse sources', e);
                }
              } else {
                try {
                  const parsed = JSON.parse(data);
                  if (parsed.type === 'token') {
                    onChunk(parsed.content);
                  } else if (parsed.type === 'error') {
                    onError(parsed.content);
                  }
                } catch (e) {
                  console.error('Failed to parse token', e);
                }
              }
            }
          }
        }
        onDone();
      } catch (err: any) {
        if (err.name === 'AbortError') return;
        onError(err.message || 'Streaming error');
      }
    };

    fetchStream();

    return () => {
      abortController.abort();
    };
  },
};
