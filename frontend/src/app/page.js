"use client";

import { useState, useRef, useEffect } from "react";

const AGENTS = [
  { key: "billing", label: "Billing", color: "#F59E0B", grad: "from-amber-400 to-orange-500" },
  { key: "technical", label: "Technical", color: "#8B5CF6", grad: "from-violet-400 to-purple-600" },
  { key: "product", label: "Product", color: "#10B981", grad: "from-emerald-400 to-teal-500" },
  { key: "complaint", label: "Complaint", color: "#F43F5E", grad: "from-rose-400 to-pink-600" },
  { key: "faq", label: "FAQ", color: "#64748B", grad: "from-slate-400 to-slate-600" },
];

const agentMap = Object.fromEntries(AGENTS.map((a) => [a.key, a]));

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeAgents, setActiveAgents] = useState([]);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 120) + "px";
    }
  }, [input]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage, session_id: sessionId }),
      });
      const data = await res.json();
      setSessionId(data.session_id);
      setActiveAgents(data.agents_used || []);

      setMessages((prev) => [
        ...prev,
        { role: "system-log", agents: data.agents_used, reasoning: data.reasoning },
        ...Object.entries(data.responses).map(([agent, reply]) => ({
          role: "assistant",
          agent,
          content: reply,
          time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        })),
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", agent: "faq", content: "Connection failed. Check that the backend server is running." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const resetConversation = () => {
    setMessages([]);
    setSessionId(null);
    setActiveAgents([]);
  };

  return (
    <div className="relative flex flex-col h-screen overflow-hidden bg-gradient-to-br from-indigo-50 via-white to-pink-50">
      {/* Animated background blobs */}
      <div className="blob w-96 h-96 bg-indigo-300 top-[-100px] left-[-80px]"></div>
      <div className="blob w-80 h-80 bg-pink-300 bottom-[-60px] right-[-60px]" style={{ animationDelay: "3s" }}></div>
      <div className="blob w-72 h-72 bg-purple-200 top-1/3 right-1/4" style={{ animationDelay: "6s" }}></div>

      {/* Header */}
      <header className="relative z-10 backdrop-blur-xl bg-white/60 border-b border-white/40 px-4 sm:px-6 py-4 flex items-center justify-between shrink-0 shadow-sm">
        <div className="flex items-center gap-3">
          <span className="text-2xl sparkle">✨</span>
          <div>
            <h1 className="text-lg sm:text-xl font-bold gradient-text">TechMart Support</h1>
            <p className="text-[11px] text-slate-500">AI multi-agent assistant</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={resetConversation}
            className="text-xs font-medium text-slate-500 hover:text-indigo-600 transition hidden sm:block"
          >
            New session
          </button>
          <span className="flex items-center gap-1.5 text-xs font-medium text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 led-active"></span>
            Online
          </span>
        </div>
      </header>

      {/* Agent chips row */}
      <div className="relative z-10 flex gap-2 overflow-x-auto px-4 sm:px-6 py-3 shrink-0">
        {AGENTS.map((agent) => {
          const isActive = activeAgents.includes(agent.key);
          return (
            <div
              key={agent.key}
              className={`flex items-center gap-1.5 shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                isActive
                  ? `bg-gradient-to-r ${agent.grad} text-white shadow-md scale-105`
                  : "bg-white/70 text-slate-500 border border-slate-200"
              }`}
            >
              <span className={`w-1.5 h-1.5 rounded-full ${isActive ? "bg-white" : ""}`} style={{ backgroundColor: isActive ? "white" : agent.color }}></span>
              {agent.label}
            </div>
          );
        })}
      </div>

      {/* Chat area */}
      <div className="relative z-10 flex-1 overflow-y-auto px-4 sm:px-8 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="max-w-md mx-auto mt-16 text-center">
            <div className="text-4xl mb-3">💬✨</div>
            <p className="text-slate-800 text-xl font-semibold mb-1">How can we help?</p>
            <p className="text-slate-500 text-sm">Ask about orders, refunds, warranty, or anything else.</p>
          </div>
        )}

        {messages.map((msg, i) => {
          if (msg.role === "system-log") {
            return (
              <div key={i} className="text-[11px] text-slate-400 pl-1 msg-enter">
                → Routed to <span className="font-semibold text-indigo-500">{msg.agents?.join(" + ")}</span>
                <span className="text-slate-400"> — {msg.reasoning}</span>
              </div>
            );
          }

          if (msg.role === "user") {
            return (
              <div key={i} className="flex justify-end msg-enter">
                <div className="max-w-lg rounded-2xl rounded-br-md px-4 py-3 bg-gradient-to-br from-indigo-500 to-purple-600 text-white shadow-lg shadow-indigo-200">
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            );
          }

          const agent = agentMap[msg.agent] || agentMap.faq;
          return (
            <div key={i} className="flex justify-start msg-enter">
              <div className="max-w-lg rounded-2xl rounded-bl-md px-4 py-3 bg-white/80 backdrop-blur-md border border-white shadow-lg hover:shadow-xl transition-shadow">
                <div className="flex items-center gap-1.5 mb-1.5">
                  <span className={`text-[10px] font-bold uppercase tracking-wide px-2 py-0.5 rounded-full bg-gradient-to-r ${agent.grad} text-white`}>
                    {agent.label}
                  </span>
                  {msg.time && <span className="text-[10px] text-slate-400">{msg.time}</span>}
                </div>
                <p className="text-sm text-slate-700 whitespace-pre-wrap">{msg.content}</p>
              </div>
            </div>
          );
        })}

        {loading && (
          <div className="flex items-center gap-1.5 pl-1">
            <span className="w-2 h-2 rounded-full bg-gradient-to-r from-indigo-400 to-purple-500 dot-bounce" style={{ animationDelay: "0s" }}></span>
            <span className="w-2 h-2 rounded-full bg-gradient-to-r from-purple-400 to-pink-500 dot-bounce" style={{ animationDelay: "0.15s" }}></span>
            <span className="w-2 h-2 rounded-full bg-gradient-to-r from-pink-400 to-rose-500 dot-bounce" style={{ animationDelay: "0.3s" }}></span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="relative z-10 px-4 sm:px-8 py-4 shrink-0">
        <div className="flex items-end gap-2 bg-white/80 backdrop-blur-xl rounded-2xl px-4 border-2 border-transparent focus-within:border-indigo-300 shadow-lg transition-all">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            rows={1}
            className="flex-1 resize-none bg-transparent py-3.5 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none max-h-[120px]"
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="relative overflow-hidden shimmer bg-gradient-to-r from-indigo-500 to-purple-600 text-white px-5 py-2.5 my-2 rounded-xl text-sm font-medium disabled:opacity-30 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-indigo-300 hover:scale-105 transition-all shrink-0"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}