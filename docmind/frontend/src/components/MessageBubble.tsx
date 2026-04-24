import React from 'react';
import type { ChatMessage } from '../types';
import { SourceCard } from './SourceCard';
import { cn } from '../lib/utils';
import { Bot, User } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user';

  return (
    <div className={cn("flex w-full gap-4 py-6", isUser ? "bg-background" : "bg-muted/30")}>
      <div className="max-w-4xl mx-auto w-full flex gap-4 px-4 xl:px-0">
        
        <div className={cn("w-8 h-8 shrink-0 rounded-full flex items-center justify-center", isUser ? "bg-primary text-primary-foreground" : "bg-card border")}>
          {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5 text-primary" />}
        </div>
        
        <div className="flex-1 space-y-4">
          <div className="prose prose-sm dark:prose-invert max-w-none prose-p:leading-relaxed prose-pre:bg-muted/50">
            {message.content ? (
              <ReactMarkdown>{message.content}</ReactMarkdown>
            ) : (
              message.isStreaming && <span className="animate-pulse">...</span>
            )}
          </div>
          
          {message.sources && message.sources.length > 0 && (
            <div className="flex flex-col gap-2 mt-4 pt-4 border-t border-border/50">
               <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Sources Consulted</span>
               <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                 {message.sources.map((s, i) => (
                   <SourceCard key={i} source={s} />
                 ))}
               </div>
            </div>
          )}
        </div>
        
      </div>
    </div>
  );
}
