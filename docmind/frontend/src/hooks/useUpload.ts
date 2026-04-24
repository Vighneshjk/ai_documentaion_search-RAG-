import { useState, useCallback } from 'react';
import type { UploadProgress } from '../types';
import { api } from '../lib/api';

export function useUpload(onSuccess?: () => void) {
  const [uploads, setUploads] = useState<UploadProgress[]>([]);

  const uploadFile = useCallback(async (file: File) => {
    const uploadRef = { filename: file.name, progress: 0, status: 'uploading' as const };
    setUploads((prev) => [...prev, uploadRef]);

    try {
      const doc = await api.uploadDocument(file, (progress) => {
        setUploads((prev) =>
          prev.map((u) =>
            u.filename === file.name ? { ...u, progress } : u
          )
        );
      });
      
      setUploads((prev) =>
        prev.map((u) =>
          u.filename === file.name
            ? { ...u, progress: 100, status: 'processing', documentId: doc.id }
            : u
        )
      );
      if (onSuccess) onSuccess();
    } catch (error: any) {
      setUploads((prev) =>
        prev.map((u) =>
          u.filename === file.name
            ? { ...u, status: 'failed', error: error.response?.data?.detail || error.message }
            : u
        )
      );
    }
  }, [onSuccess]);

  const clearUploads = useCallback(() => {
    setUploads([]);
  }, []);

  return {
    uploads,
    uploadFile,
    clearUploads
  };
}
