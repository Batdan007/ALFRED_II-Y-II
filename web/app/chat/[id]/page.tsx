'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Send, Loader2 } from 'lucide-react';
import { getAgent, chatWithAgent } from '@/lib/api';
import { useAuthStore } from '@/lib/store';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function ChatPage() {
  const router = useRouter();
  const params = useParams();
  const token = useAuthStore((s) => s.token);

  const [agent, setAgent] = useState<any>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const agentId = Number(params.id);

  useEffect(() => {
    if (!token) {
      router.push('/login');
      return;
    }
    loadAgent();
  }, [token, agentId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadAgent = async () => {
    if (!token) return;
    setLoading(true);
    try {
      const data = await getAgent(token, agentId);
      setAgent(data);
    } catch (err) {
      console.error('Failed to load agent:', err);
      router.push('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const handleSend = async () => {
    if (!token || !input.trim() || sending) return;

    const userMessage = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setSending(true);

    try {
      // Build context from recent messages
      const context = messages.slice(-10).map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const res = await chatWithAgent(token, agentId, userMessage, context);
      setMessages((prev) => [...prev, { role: 'assistant', content: res.response }]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `Error: ${err.message || 'Failed to get response'}` },
      ]);
    } finally {
      setSending(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!token) return null;

  return (
    <div className="h-screen flex flex-col bg-background safe-top">
      {/* Header */}
      <header className="flex-none bg-card border-b border-white/10">
        <div className="max-w-2xl mx-auto px-4 py-3 flex items-center gap-3">
          <Link href="/dashboard" className="p-2 -ml-2 text-gray-400 hover:text-white">
            <ArrowLeft size={20} />
          </Link>
          <div className="flex-1 min-w-0">
            {loading ? (
              <div className="h-5 bg-white/10 rounded animate-pulse w-24" />
            ) : (
              <>
                <h1 className="font-bold truncate">{agent?.name}</h1>
                <p className="text-xs text-gray-400 capitalize">{agent?.personality}</p>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Messages */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-2xl mx-auto px-4 py-4">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-4xl mb-3">💬</div>
              <p className="text-gray-400">
                Start chatting with {agent?.name || 'your agent'}
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((msg, i) => (
                <div
                  key={i}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[85%] px-4 py-3 rounded-2xl ${
                      msg.role === 'user'
                        ? 'bg-accent text-white rounded-br-md'
                        : 'bg-card border border-white/10 rounded-bl-md'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  </div>
                </div>
              ))}
              {sending && (
                <div className="flex justify-start">
                  <div className="px-4 py-3 bg-card border border-white/10 rounded-2xl rounded-bl-md">
                    <Loader2 size={16} className="animate-spin text-gray-400" />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </main>

      {/* Input */}
      <footer className="flex-none bg-card border-t border-white/10 safe-bottom">
        <div className="max-w-2xl mx-auto px-4 py-3">
          <div className="flex items-end gap-2">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={`Message ${agent?.name || 'agent'}...`}
              rows={1}
              className="flex-1 px-4 py-3 bg-background border border-white/20 rounded-xl resize-none focus:border-accent focus:outline-none max-h-32"
              style={{ minHeight: '48px' }}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || sending}
              className="p-3 btn-gradient rounded-xl disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
}
