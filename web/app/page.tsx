'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Sparkles, Brain, Shield, Link2, ChevronRight } from 'lucide-react';
import { betaSignup } from '@/lib/api';

export default function LandingPage() {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  const handleBetaSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus('loading');

    try {
      const res = await betaSignup(email);
      setStatus('success');
      setMessage(res.message);
      setEmail('');
    } catch (err: any) {
      setStatus('error');
      setMessage(err.message || 'Something went wrong');
    }
  };

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-white/10">
        <div className="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="text-xl font-bold gradient-text">ALFRED SYSTEMS</div>
          <div className="flex gap-4">
            <Link href="/login" className="px-4 py-2 text-gray-400 hover:text-white transition">
              Login
            </Link>
            <Link
              href="/signup"
              className="px-4 py-2 bg-accent rounded-lg hover:bg-accent/80 transition"
            >
              Sign Up
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="px-4 py-16 md:py-24 text-center">
        <div className="max-w-3xl mx-auto">
          <div className="inline-block px-4 py-1.5 border border-accent text-accent rounded-full text-sm mb-6">
            Patent-Pending AI Technology
          </div>
          <h1 className="text-4xl md:text-6xl font-bold mb-6 gradient-text">
            Birth Your Own AI
          </h1>
          <p className="text-lg md:text-xl text-gray-400 mb-8 max-w-xl mx-auto">
            Create personalized AI agents that learn, remember, and evolve with you.
            Your AI, your rules.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/signup"
              className="btn-gradient px-8 py-3 rounded-lg font-medium text-white flex items-center justify-center gap-2"
            >
              Get Started Free <ChevronRight size={18} />
            </Link>
            <a
              href="#features"
              className="px-8 py-3 rounded-lg border border-accent text-accent hover:bg-accent/10 transition"
            >
              Learn More
            </a>
          </div>
          <p className="text-gray-500 text-sm mt-6">
            Open Beta - Pro features free for early adopters
          </p>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="px-4 py-16 bg-card">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">What Makes MaiAI Different</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <FeatureCard
              icon={<Sparkles className="text-accent" size={32} />}
              title="Personality DNA"
              description="Each agent has unique traits, voice, and behavior. Create a British butler, coding mentor, or something entirely new."
            />
            <FeatureCard
              icon={<Brain className="text-accent" size={32} />}
              title="Persistent Memory"
              description="Powered by our patent-pending 11-table brain. Your agent remembers and gets better over time."
            />
            <FeatureCard
              icon={<Shield className="text-accent" size={32} />}
              title="Privacy First"
              description="Local AI by default. Your data never leaves your device unless you say so."
            />
            <FeatureCard
              icon={<Link2 className="text-accent" size={32} />}
              title="NEXUS Protocol"
              description="Let your AI agents talk to each other. Share knowledge and coordinate tasks."
            />
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="px-4 py-16">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4">Simple Pricing</h2>
          <p className="text-gray-400 text-center mb-12">Start free, upgrade when ready</p>
          <div className="grid md:grid-cols-3 gap-6">
            <PriceCard
              title="Free"
              price="$0"
              features={['1 AI Agent', '100 msgs/day', 'Basic memory', 'Community support']}
              cta="Get Started"
              href="/signup"
            />
            <PriceCard
              title="Pro"
              price="$9.99"
              features={['5 AI Agents', '1,000 msgs/day', 'Unlimited memory', 'Priority support', 'Voice customization']}
              cta="Start Pro"
              href="/signup"
              featured
            />
            <PriceCard
              title="Enterprise"
              price="$49.99"
              features={['Unlimited Agents', 'Unlimited messages', 'Full API access', 'NEXUS protocol', 'White-label']}
              cta="Contact Sales"
              href="mailto:danieljrita@hotmail.com"
            />
          </div>
        </div>
      </section>

      {/* Beta CTA */}
      <section className="px-4 py-16 bg-card">
        <div className="max-w-lg mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">Join the Beta</h2>
          <p className="text-gray-400 mb-8">
            Get <span className="text-accent font-medium">Pro features free</span> during beta
          </p>
          <form onSubmit={handleBetaSignup} className="flex flex-col sm:flex-row gap-3">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              required
              className="flex-1 px-4 py-3 bg-background border border-white/20 rounded-lg focus:border-accent focus:outline-none"
            />
            <button
              type="submit"
              disabled={status === 'loading'}
              className="btn-gradient px-6 py-3 rounded-lg font-medium disabled:opacity-50"
            >
              {status === 'loading' ? 'Joining...' : 'Join Beta'}
            </button>
          </form>
          {message && (
            <p className={`mt-4 text-sm ${status === 'success' ? 'text-green-400' : 'text-red-400'}`}>
              {message}
            </p>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="px-4 py-8 border-t border-white/10 text-center text-gray-500 text-sm">
        <p>Patent-Pending Technology by Daniel J Rita (BATDAN)</p>
        <p>CAMDAN Enterprises LLC 2025-2026</p>
      </footer>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="p-6 bg-background border border-white/10 rounded-xl card-hover">
      <div className="mb-4">{icon}</div>
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-gray-400 text-sm">{description}</p>
    </div>
  );
}

function PriceCard({
  title,
  price,
  features,
  cta,
  href,
  featured,
}: {
  title: string;
  price: string;
  features: string[];
  cta: string;
  href: string;
  featured?: boolean;
}) {
  return (
    <div
      className={`p-6 rounded-xl border ${
        featured ? 'border-accent bg-accent/5 scale-105' : 'border-white/10 bg-card'
      }`}
    >
      {featured && (
        <div className="text-xs text-accent font-medium mb-2">MOST POPULAR</div>
      )}
      <h3 className="text-xl font-bold mb-2">{title}</h3>
      <div className="text-3xl font-bold mb-4">
        {price}
        <span className="text-sm text-gray-400 font-normal">/mo</span>
      </div>
      <ul className="space-y-2 mb-6">
        {features.map((f) => (
          <li key={f} className="text-sm text-gray-400 flex items-center gap-2">
            <span className="text-accent">✓</span> {f}
          </li>
        ))}
      </ul>
      <Link
        href={href}
        className={`block text-center py-2.5 rounded-lg font-medium ${
          featured ? 'btn-gradient text-white' : 'border border-accent text-accent hover:bg-accent/10'
        }`}
      >
        {cta}
      </Link>
    </div>
  );
}
