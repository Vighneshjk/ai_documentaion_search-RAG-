import React, { useState } from 'react';
import { FileText, ChevronDown, ChevronUp } from 'lucide-react';
import type { SourceChunk } from '../types';

export function SourceCard({ source }: { source: SourceChunk }) {
  const [expanded, setExpanded] = useState(false);
  
  // Format percentage
  const scorePct = Math.round((1 - Math.min(1, Math.max(0, source.score))) * 100);

  return (
    <div className="border border-border/50 bg-muted/20 rounded-lg p-3 text-sm">
      <div 
        className="flex items-center justify-between cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors font-medium">
          <FileText className="w-4 h-4" />
          <span className="truncate max-w-[200px]">{source.filename}</span>
          <span className="px-1.5 py-0.5 rounded-md bg-secondary text-xs">Page {source.page_number}</span>
          {/* <span className="text-xs opacity-50">Match ~{scorePct}%</span> */}
        </div>
        <button className="text-muted-foreground">
          {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
      </div>
      
      {expanded && (
        <div className="mt-3 pt-3 border-t border-border/50 text-foreground/80 leading-relaxed text-xs font-mono">
          {source.content}
        </div>
      )}
    </div>
  );
}
