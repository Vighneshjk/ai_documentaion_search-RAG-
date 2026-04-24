import { useState, useEffect, useCallback } from 'react';
import { Document } from '../types';
import { api } from '../lib/api';

export function useDocuments() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDocuments = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await api.getDocuments();
      setDocuments(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch documents');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
    // Simple polling for processing status updates
    const interval = setInterval(() => {
      fetchDocuments();
    }, 5000);
    return () => clearInterval(interval);
  }, [fetchDocuments]);

  const deleteDocument = useCallback(async (id: string) => {
    try {
      await api.deleteDocument(id);
      setDocuments((prev) => prev.filter((d) => d.id !== id));
      setSelectedDocIds((prev) => prev.filter((docId) => docId !== id));
    } catch (err: any) {
      setError(err.message || 'Failed to delete document');
      throw err;
    }
  }, []);

  const toggleSelection = useCallback((id: string) => {
    setSelectedDocIds((prev) =>
      prev.includes(id) ? prev.filter((docId) => docId !== id) : [...prev, id]
    );
  }, []);

  const selectAll = useCallback(() => {
    const readyDocIds = documents.filter(d => d.status === 'ready').map(d => d.id);
    setSelectedDocIds(readyDocIds);
  }, [documents]);

  const deselectAll = useCallback(() => {
    setSelectedDocIds([]);
  }, []);

  return {
    documents,
    selectedDocIds,
    isLoading,
    error,
    fetchDocuments,
    deleteDocument,
    toggleSelection,
    selectAll,
    deselectAll,
  };
}
