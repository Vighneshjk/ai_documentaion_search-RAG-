import React, { useEffect, useRef } from 'react';
import { useChat } from '../hooks/useChat';
import { MessageBubble } from './MessageBubble';
import { ChatInput } from './ChatInput';
import { AlertCircle, FileText } from 'lucide-react';

interface ChatWindowProps {
  chatContext: ReturnType<typeof useChat>;
  selectedDocIds: string[];
}

export function ChatWindow({ chatContext, selectedDocIds }: ChatWindowProps) {
  const { messages, isStreaming, error, sendMessage, stopStreaming } = chatContext;
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col h-full bg-background relative overflow-hidden">
      {/* Header */}
      <div className="absolute top-0 w-full z-10 bg-background/80 backdrop-blur-md border-b flex items-center px-6 h-14">
        <h2 className="text-sm font-medium tracking-tight">Chat with Documents</h2>
        <div className="ml-auto text-xs text-muted-foreground flex items-center gap-1.5 bg-muted/50 px-2.5 py-1 rounded-full">
           <FileText className="w-3.5 h-3.5" />
           {selectedDocIds.length} active documents
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto pt-14 pb-32">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center text-muted-foreground p-8 animate-in zoom-in-95 duration-500">
            <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mb-6 text-primary">
              <FileText className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-semibold mb-2 text-foreground">Ready to Chat</h3>
            <p className="max-w-sm">Select some documents from the sidebar and ask me any questions about their contents.</p>
          </div>
        ) : (
          <div className="divide-y">
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
            <div ref={bottomRef} className="h-1" />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="absolute bottom-0 w-full bg-gradient-to-t from-background via-background/95 to-transparent pb-6 pt-10 px-4 md:px-8">
        
        {error && (
          <div className="max-w-4xl mx-auto mb-4 bg-destructive/10 text-destructive text-sm px-4 py-3 rounded-lg flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <p>{error}</p>
          </div>
        )}

        <ChatInput 
          onSend={(text) => sendMessage(text, selectedDocIds)}
          isStreaming={isStreaming}
          onStop={stopStreaming}
          disabled={selectedDocIds.length === 0}
        />
        
        {selectedDocIds.length === 0 && (
          <p className="text-xs text-center mt-3 text-muted-foreground">Select at least one document to start chatting.</p>
        )}
      </div>
    </div>
  );
}
