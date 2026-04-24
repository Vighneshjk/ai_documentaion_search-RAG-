import React from 'react';
import { FileText, Loader2, Trash2, CheckCircle } from 'lucide-react';
import { useDocuments } from '../hooks/useDocuments';
import { cn, formatBytes } from '../lib/utils';
import { UploadZone } from './UploadZone';

interface DocumentListProps {
  documentsContext: ReturnType<typeof useDocuments>;
}

export function DocumentList({ documentsContext }: DocumentListProps) {
  const { documents, selectedDocIds, toggleSelection, deleteDocument, isLoading, fetchDocuments } = documentsContext;

  return (
    <div className="w-full h-full flex flex-col bg-muted/20 border-r">
      <div className="p-4 border-b flex items-center justify-between">
        <h2 className="text-lg font-semibold tracking-tight">Documents</h2>
        <button onClick={fetchDocuments} className="text-xs text-muted-foreground hover:text-foreground transition-colors">Refresh</button>
      </div>
      
      <div className="p-4 border-b">
         <UploadZone onUploadComplete={fetchDocuments} />
      </div>

      <div className="flex-1 overflow-auto p-4 space-y-2">
        {isLoading && documents.length === 0 && (
          <div className="flex center p-4 justify-center text-muted-foreground"><Loader2 className="animate-spin w-5 h-5" /></div>
        )}
        
        {!isLoading && documents.length === 0 && (
          <p className="text-sm text-muted-foreground text-center py-8">No documents uploaded yet.</p>
        )}

        {documents.map(doc => (
          <div key={doc.id} className={cn("flex flex-col gap-2 p-3 rounded-xl border bg-card transition-all cursor-pointer hover:border-primary/50 relative overflow-hidden group", selectedDocIds.includes(doc.id) ? "ring-2 ring-primary border-transparent" : "border-border")} onClick={() => toggleSelection(doc.id)}>
             
             <div className="flex items-start justify-between">
               <div className="flex items-center gap-3">
                 <div className="bg-primary/10 rounded-md p-2">
                   <FileText className="w-5 h-5 text-primary" />
                 </div>
                 <div>
                   <p className="text-sm font-medium line-clamp-1" title={doc.filename}>{doc.filename}</p>
                   <div className="flex items-center gap-2 text-xs text-muted-foreground mt-0.5">
                     <span>{formatBytes(doc.file_size)}</span>
                     <span>•</span>
                     <span>{doc.page_count} pages</span>
                   </div>
                 </div>
               </div>
             </div>

             <div className="flex items-center justify-between border-t border-border/50 pt-2 mt-1">
                <div className="flex text-xs items-center gap-1.5">
                   {doc.status === 'processing' && <><Loader2 className="w-3 h-3 animate-spin"/> Processing</>}
                   {doc.status === 'ready' && <><CheckCircle className="w-3 h-3 text-green-500"/> Ready to chat</>}
                   {doc.status === 'failed' && <span className="text-destructive">Failed to process</span>}
                </div>
                <button 
                  className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 text-muted-foreground hover:text-destructive rounded-md hover:bg-destructive/10"
                  onClick={(e) => { e.stopPropagation(); deleteDocument(doc.id); }}
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
             </div>
          </div>
        ))}
      </div>
    </div>
  );
}
