import { useState, useCallback, useRef } from 'react';
import { ChatMessage, SourceChunk } from '../types';
import { api } from '../lib/api';

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const sessionIdRef = useRef<string>(crypto.randomUUID());
  const cleanupStreamRef = useRef<(() => void) | null>(null);

  const sendMessage = useCallback(async (content: string, documentIds: string[]) => {
    if (!content.trim() || documentIds.length === 0) return;

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    };

    const assistantMessageId = crypto.randomUUID();
    const assistantMessage: ChatMessage = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      isStreaming: true,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage, assistantMessage]);
    setIsStreaming(true);
    setError(null);

    let assistantContent = '';

    const historyPayload = messages.map(({ role, content }) => ({ role, content }));

    cleanupStreamRef.current = api.streamMessage(
      {
        query: content,
        document_ids: documentIds,
        session_id: sessionIdRef.current,
        history: historyPayload as any,
      },
      (token) => {
        assistantContent += token;
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMessageId ? { ...msg, content: assistantContent } : msg
          )
        );
      },
      (sources) => {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMessageId ? { ...msg, sources } : msg
          )
        );
      },
      () => {
        setIsStreaming(false);
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMessageId ? { ...msg, isStreaming: false } : msg
          )
        );
      },
      (err) => {
        setError(err);
        setIsStreaming(false);
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMessageId ? { ...msg, isStreaming: false } : msg
          )
        );
      }
    );
  }, [messages]);

  const clearHistory = useCallback(() => {
    setMessages([]);
    sessionIdRef.current = crypto.randomUUID();
    setError(null);
  }, []);

  const stopStreaming = useCallback(() => {
    if (cleanupStreamRef.current) {
      cleanupStreamRef.current();
      cleanupStreamRef.current = null;
      setIsStreaming(false);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.isStreaming ? { ...msg, isStreaming: false } : msg
        )
      );
    }
  }, []);

  return {
    messages,
    isStreaming,
    error,
    sendMessage,
    clearHistory,
    stopStreaming,
  };
}
