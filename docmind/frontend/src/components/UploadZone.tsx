import React, { useCallback } from 'react';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { useUpload } from '../hooks/useUpload';
import { cn, formatBytes } from '../lib/utils';

export function UploadZone({ onUploadComplete }: { onUploadComplete?: () => void }) {
  const { uploads, uploadFile } = useUpload(onUploadComplete);
  const [isDragging, setIsDragging] = React.useState(false);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') setIsDragging(true);
    else if (e.type === 'dragleave') setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      Array.from(e.dataTransfer.files).filter(f => f.type === 'application/pdf').forEach(uploadFile);
    }
  }, [uploadFile]);

  return (
    <div className="w-full max-w-2xl mx-auto flex flex-col gap-4">
      <div
        className={cn(
          "border-2 border-dashed rounded-xl p-10 flex flex-col items-center justify-center text-center transition-all cursor-pointer bg-card hover:bg-muted/50",
          isDragging ? "border-primary bg-muted/50" : "border-border"
        )}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => document.getElementById('file-upload')?.click()}
      >
        <UploadCloud className="w-12 h-12 text-muted-foreground mb-4" />
        <h3 className="text-lg font-semibold mb-1">Upload Documents</h3>
        <p className="text-sm text-muted-foreground mb-4">Drag & drop your PDFs here, or click to browse</p>
        <p className="text-xs text-muted-foreground/75">Supports PDF up to 50MB</p>
        <input
          id="file-upload"
          type="file"
          accept=".pdf"
          className="hidden"
          multiple
          onChange={(e) => {
            if (e.target.files) {
              Array.from(e.target.files).forEach(uploadFile);
            }
          }}
        />
      </div>

      {uploads.length > 0 && (
        <div className="space-y-3">
          {uploads.map((u, i) => (
            <div key={i} className="flex items-center p-3 rounded-lg border bg-card gap-4 shadow-sm animate-in fade-in slide-in-from-bottom-2">
              <FileText className="w-8 h-8 text-primary shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{u.filename}</p>
                {u.status === 'uploading' && (
                  <div className="w-full bg-border h-1.5 rounded-full mt-2 overflow-hidden">
                    <div className="bg-primary h-full transition-all duration-300" style={{ width: `${u.progress}%` }} />
                  </div>
                )}
                {u.status === 'processing' && <p className="text-xs text-muted-foreground mt-1">Processing document...</p>}
                {u.error && <p className="text-xs text-destructive mt-1">{u.error}</p>}
              </div>
              <div>
                {u.status === 'uploading' && <span className="text-xs font-medium text-muted-foreground">{u.progress}%</span>}
                {u.status === 'processing' && <Loader2 className="w-5 h-5 text-primary animate-spin" />}
                {u.status === 'ready' && <CheckCircle2 className="w-5 h-5 text-green-500" />}
                {u.status === 'failed' && <AlertCircle className="w-5 h-5 text-destructive" />}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
