import React from 'react';
import { DocumentList } from '../components/DocumentList';
import { ChatWindow } from '../components/ChatWindow';
import { useDocuments } from '../hooks/useDocuments';
import { useChat } from '../hooks/useChat';

export function Chat() {
  const documentsContext = useDocuments();
  const chatContext = useChat();

  return (
    <div className="flex h-screen bg-background overflow-hidden w-full">
      {/* Sidebar */}
      <aside className="w-80 shrink-0 border-r border-border hidden md:block relative z-20 shadow-xl shadow-background">
        <DocumentList documentsContext={documentsContext} />
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 relative min-w-0">
        <ChatWindow 
          chatContext={chatContext} 
          selectedDocIds={documentsContext.selectedDocIds} 
        />
      </main>

      {/* Mobile Sidebar Toggle - simple implementation */}
      {/* Real app would use a Drawer component here */}
    </div>
  );
}
