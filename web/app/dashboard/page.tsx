'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Plus, MessageCircle, LogOut, User } from 'lucide-react';
import { getAgents } from '@/lib/api';
import { useAuthStore, useAgentStore } from '@/lib/store';

export default function DashboardPage() {
  const router = useRouter();
  const { token, user, logout } = useAuthStore();
  const { agents, setAgents } = useAgentStore();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) {
      router.push('/login');
      return;
    }

    loadAgents();
  }, [token]);

  const loadAgents = async () => {
    if (!token) return;
    try {
      const data = await getAgents(token);
      setAgents(data);
    } catch (err) {
      console.error('Failed to load agents:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  if (!token) return null;

  return (
    <div className="min-h-screen safe-top safe-bottom">
      {/* Header */}
      <header className="sticky top-0 bg-background/80 backdrop-blur-lg border-b border-white/10 z-10">
        <div className="max-w-2xl mx-auto px-4 py-3 flex justify-between items-center">
          <div className="text-lg font-bold gradient-text">ALFRED</div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 text-sm text-gray-400">
              <User size={16} />
              <span className="hidden sm:inline">{user?.email}</span>
            </div>
            <button
              onClick={handleLogout}
              className="p-2 text-gray-400 hover:text-white transition"
            >
              <LogOut size={18} />
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-6">
        {/* Tier badge */}
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-xl font-bold">Your AI Agents</h1>
          <span className="text-xs px-2 py-1 bg-accent/20 text-accent rounded-full">
            {user?.subscription_tier?.toUpperCase() || 'FREE'} {user?.beta_access && '- BETA'}
          </span>
        </div>

        {loading ? (
          <div className="text-center py-12 text-gray-400">Loading...</div>
        ) : agents.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-4xl mb-4">🤖</div>
            <h2 className="text-lg font-medium mb-2">No agents yet</h2>
            <p className="text-gray-400 text-sm mb-6">
              Birth your first AI agent to get started
            </p>
            <Link
              href="/birth"
              className="inline-flex items-center gap-2 btn-gradient px-6 py-3 rounded-lg font-medium"
            >
              <Plus size={18} /> Birth New Agent
            </Link>
          </div>
        ) : (
          <>
            {/* Agent list */}
            <div className="space-y-3 mb-6">
              {agents.filter(a => a.status === 'active').map((agent) => (
                <Link
                  key={agent.id}
                  href={`/chat/${agent.id}`}
                  className="block p-4 bg-card border border-white/10 rounded-xl card-hover"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium">{agent.name}</h3>
                      <p className="text-sm text-gray-400 capitalize">
                        {agent.personality} • {agent.total_conversations} chats
                      </p>
                    </div>
                    <div className="flex items-center gap-2 text-accent">
                      <MessageCircle size={18} />
                    </div>
                  </div>
                </Link>
              ))}
            </div>

            {/* Birth button */}
            <Link
              href="/birth"
              className="fixed bottom-6 right-6 btn-gradient p-4 rounded-full shadow-lg shadow-accent/20"
            >
              <Plus size={24} />
            </Link>
          </>
        )}
      </main>
    </div>
  );
}
