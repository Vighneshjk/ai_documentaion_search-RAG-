import React, { useState, KeyboardEvent, useRef, useEffect } from 'react';
import { Send, StopCircle } from 'lucide-react';
import { cn } from '../lib/utils';

interface ChatInputProps {
  onSend: (message: string) => void;
  isStreaming: boolean;
  onStop: () => void;
  disabled: boolean;
}

export function ChatInput({ onSend, isStreaming, onStop, disabled }: ChatInputProps) {
  const [value, setValue] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`;
    }
  }, [value]);

  const handleSend = () => {
    if (!value.trim() || disabled) return;
    onSend(value);
    setValue('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="relative flex items-end w-full max-w-4xl mx-auto p-4 py-2 border rounded-2xl bg-card shadow-sm shadow-primary/5 focus-within:shadow-md focus-within:border-primary/50 transition-all">
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={disabled ? "Select a document to start chatting..." : "Ask me anything about your documents..."}
        className="w-full max-h-[150px] bg-transparent resize-none outline-none py-3 px-2 text-sm text-foreground overflow-y-auto disabled:opacity-50 placeholder:text-muted-foreground"
        rows={1}
        disabled={disabled || isStreaming}
      />
      
      <div className="flex mb-1 ml-2 shrink-0">
        {isStreaming ? (
          <button
            onClick={onStop}
            className="p-3 bg-destructive text-destructive-foreground rounded-xl transition-transform active:scale-95 hover:bg-destructive/90"
          >
            <StopCircle className="w-5 h-5" />
          </button>
        ) : (
          <button
            onClick={handleSend}
            disabled={!value.trim() || disabled}
            className={cn("p-3 rounded-xl transition-all active:scale-95", 
              value.trim() && !disabled 
                ? "bg-primary text-primary-foreground hover:bg-primary/90 shadow-md shadow-primary/20" 
                : "bg-muted text-muted-foreground"
            )}
          >
            <Send className="w-5 h-5" />
          </button>
        )}
      </div>
    </div>
  );
}
