'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Sparkles } from 'lucide-react';
import { getPresets, birthAgent } from '@/lib/api';
import { useAuthStore, useAgentStore } from '@/lib/store';

const PERSONALITY_EMOJIS: Record<string, string> = {
  alfred: '🎩',
  scholar: '📚',
  creative: '🎨',
  coder: '💻',
  coach: '🏆',
  custom: '✨',
};

export default function BirthPage() {
  const router = useRouter();
  const token = useAuthStore((s) => s.token);
  const addAgent = useAgentStore((s) => s.addAgent);

  const [presets, setPresets] = useState<any>(null);
  const [name, setName] = useState('');
  const [personality, setPersonality] = useState('alfred');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token) {
      router.push('/login');
      return;
    }
    loadPresets();
  }, [token]);

  const loadPresets = async () => {
    try {
      const data = await getPresets();
      setPresets(data);
    } catch (err) {
      console.error('Failed to load presets:', err);
    }
  };

  const handleBirth = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token || !name.trim()) return;

    setLoading(true);
    setError('');

    try {
      const agent = await birthAgent(token, {
        name: name.trim(),
        personality,
      });
      addAgent(agent);
      router.push(`/chat/${agent.id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to birth agent');
    } finally {
      setLoading(false);
    }
  };

  if (!token) return null;

  return (
    <div className="min-h-screen safe-top safe-bottom">
      {/* Header */}
      <header className="sticky top-0 bg-background/80 backdrop-blur-lg border-b border-white/10 z-10">
        <div className="max-w-lg mx-auto px-4 py-3 flex items-center gap-3">
          <Link href="/dashboard" className="p-2 -ml-2 text-gray-400 hover:text-white">
            <ArrowLeft size={20} />
          </Link>
          <h1 className="font-bold">Birth New Agent</h1>
        </div>
      </header>

      <main className="max-w-lg mx-auto px-4 py-6">
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">🧬</div>
          <h2 className="text-xl font-bold mb-2">Give Life to Your AI</h2>
          <p className="text-gray-400 text-sm">
            Choose a personality and name for your new agent
          </p>
        </div>

        <form onSubmit={handleBirth} className="space-y-6">
          {/* Name */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Agent Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              maxLength={50}
              className="w-full px-4 py-3 bg-card border border-white/20 rounded-lg focus:border-accent focus:outline-none text-lg"
              placeholder="e.g., Jarvis, Friday, Max..."
            />
          </div>

          {/* Personality */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Personality</label>
            <div className="grid grid-cols-2 gap-3">
              {presets?.personalities &&
                Object.entries(presets.personalities).map(([key, preset]: [string, any]) => (
                  <button
                    key={key}
                    type="button"
                    onClick={() => setPersonality(key)}
                    className={`p-4 rounded-xl border text-left transition ${
                      personality === key
                        ? 'border-accent bg-accent/10'
                        : 'border-white/10 bg-card hover:border-white/20'
                    }`}
                  >
                    <div className="text-2xl mb-2">{PERSONALITY_EMOJIS[key] || '🤖'}</div>
                    <div className="font-medium text-sm">{preset.name}</div>
                    <div className="text-xs text-gray-400 mt-1 line-clamp-2">
                      {preset.description}
                    </div>
                  </button>
                ))}
            </div>
          </div>

          {error && (
            <div className="text-red-400 text-sm bg-red-400/10 p-3 rounded-lg">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !name.trim()}
            className="w-full btn-gradient py-4 rounded-xl font-medium flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <Sparkles size={20} />
            {loading ? 'Birthing...' : 'Birth Agent'}
          </button>
        </form>
      </main>
    </div>
  );
}
