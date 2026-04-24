import React from 'react';
import { UploadZone } from '../components/UploadZone';
import { ArrowRight, Bot, Database, Zap, FileText } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export function Home() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background relative selection:bg-primary/20">
      {/* Decorative background blur */}
      <div className="absolute top-0 -translate-y-12 inset-x-0 h-[500px] bg-primary/20 blur-[120px] rounded-[100%] opacity-50 pointer-events-none" />
      
      <main className="relative max-w-5xl mx-auto px-6 pt-32 pb-20 flex flex-col items-center">
        
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-muted border text-sm font-medium mb-8 animate-in slide-in-from-bottom-4 duration-700">
           <Zap className="w-4 h-4 text-primary" />
           <span>Introducing DocMind AI</span>
        </div>

        <h1 className="text-5xl md:text-7xl font-bold text-center tracking-tight text-balance mb-6 animate-in slide-in-from-bottom-6 duration-700 delay-100">
          Chat with your <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-primary/50">documents</span> in seconds.
        </h1>
        
        <p className="text-lg md:text-xl text-muted-foreground text-center max-w-2xl text-balance mb-12 animate-in slide-in-from-bottom-6 duration-700 delay-200">
          Upload any PDF and let our advanced RAG pipeline find answers, summarize content, and extract key insights instantly.
        </p>

        <div className="w-full animate-in slide-in-from-bottom-8 duration-700 delay-300 relative z-10">
          <UploadZone onUploadComplete={() => navigate('/chat')} />
          <div className="flex justify-center mt-6">
             <button 
                onClick={() => navigate('/chat')}
                className="flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
             >
                Go to Chat Dashboard <ArrowRight className="w-4 h-4" />
             </button>
          </div>
        </div>

        {/* Feature Grid */}
        <div className="grid md:grid-cols-3 gap-8 mt-32 w-full">
           <div className="bg-card border rounded-2xl p-6 shadow-sm">
             <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center text-primary mb-4">
                <Database className="w-6 h-6" />
             </div>
             <h3 className="text-lg font-semibold mb-2">Vector Search</h3>
             <p className="text-muted-foreground text-sm">Semantic similarity search using state-of-the-art embedding models to find exact matches.</p>
           </div>
           
           <div className="bg-card border rounded-2xl p-6 shadow-sm">
             <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center text-primary mb-4">
                <Bot className="w-6 h-6" />
             </div>
             <h3 className="text-lg font-semibold mb-2">GPT-4o Powered</h3>
             <p className="text-muted-foreground text-sm">Advanced language understanding to synthesize and formulate natural conversational answers.</p>
           </div>

           <div className="bg-card border rounded-2xl p-6 shadow-sm">
             <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center text-primary mb-4">
                <FileText className="w-6 h-6" />
             </div>
             <h3 className="text-lg font-semibold mb-2">Accurate Citations</h3>
             <p className="text-muted-foreground text-sm">Every answer includes exact page references and content snippets from your original files.</p>
           </div>
        </div>
      </main>
    </div>
  );
}
