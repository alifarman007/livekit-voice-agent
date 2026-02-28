import { useState, useCallback } from "react";
import { AgentConfig, TEMPLATES } from "./agentTypes";
import { TestSection } from "./TestSection";

interface AgentBuilderProps {
  agent: AgentConfig;
  onChange: (agent: AgentConfig) => void;
  onBack: () => void;
  onSave: () => void;
}

// Section collapse state type
type SectionKey = "prompt" | "voice" | "llm" | "transcriber" | "actions" | "phone" | "test";

export function AgentBuilder({ agent, onChange, onBack, onSave }: AgentBuilderProps) {
  const [openSections, setOpenSections] = useState<Set<SectionKey>>(
    () => new Set<SectionKey>(["prompt", "test"])
  );

  const template = TEMPLATES.find((t) => t.id === agent.templateId);
  const accent = template?.accentColor || "#7364E2";

  const toggleSection = useCallback((key: SectionKey) => {
    setOpenSections((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  }, []);

  const update = useCallback(
    (partial: Partial<AgentConfig>) => {
      onChange({ ...agent, ...partial });
    },
    [agent, onChange]
  );

  return (
    <div className="flex h-full overflow-hidden">
      {/* Left: Config Panel */}
      <div className="flex-1 overflow-y-auto p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <button
              onClick={onBack}
              className="flex items-center gap-2 text-sm mb-2 transition-colors"
              style={{ color: "var(--text-secondary)" }}
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M10 12L6 8L10 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Back
            </button>
            <div className="flex items-center gap-3">
              {template && (
                <div
                  className="w-8 h-8 rounded-lg flex items-center justify-center text-base"
                  style={{ background: template.washBg }}
                >
                  {template.emoji}
                </div>
              )}
              <input
                type="text"
                value={agent.name}
                onChange={(e) => update({ name: e.target.value })}
                className="text-lg font-semibold bg-transparent outline-none"
                style={{ color: "var(--text-primary)" }}
              />
            </div>
          </div>
          <button
            onClick={onSave}
            className="px-4 py-2 rounded-lg text-sm font-medium transition-all"
            style={{ background: accent, color: "white" }}
          >
            Save Agent
          </button>
        </div>

        <div className="space-y-3 max-w-[640px]">
          {/* 1. PROMPT */}
          <Section
            title="Prompt"
            icon="📝"
            sectionKey="prompt"
            open={openSections.has("prompt")}
            onToggle={toggleSection}
            accent={accent}
          >
            <div className="space-y-4">
              <Field label="System Prompt">
                <textarea
                  rows={5}
                  value={agent.systemPrompt}
                  onChange={(e) => update({ systemPrompt: e.target.value })}
                  placeholder="You are Nusrat, a professional Bangladeshi receptionist..."
                  className="w-full rounded-lg px-3 py-2 text-sm outline-none resize-none transition-colors"
                  style={{
                    background: "var(--depth-3)",
                    color: "var(--text-primary)",
                    border: "1px solid var(--border-subtle)",
                  }}
                />
              </Field>
              <Field label="First Message (Greeting)">
                <input
                  type="text"
                  value={agent.firstMessage}
                  onChange={(e) => update({ firstMessage: e.target.value })}
                  placeholder="আসসালামু আলাইকুম..."
                  className="w-full rounded-lg px-3 py-2 text-sm outline-none"
                  style={{
                    background: "var(--depth-3)",
                    color: "var(--text-primary)",
                    border: "1px solid var(--border-subtle)",
                  }}
                />
              </Field>
              <Field label="End Message (Goodbye)">
                <input
                  type="text"
                  value={agent.endMessage}
                  onChange={(e) => update({ endMessage: e.target.value })}
                  placeholder="আস্সালামু আলাইকুম, আবার কল দিবেন।"
                  className="w-full rounded-lg px-3 py-2 text-sm outline-none"
                  style={{
                    background: "var(--depth-3)",
                    color: "var(--text-primary)",
                    border: "1px solid var(--border-subtle)",
                  }}
                />
              </Field>
            </div>
          </Section>

          {/* 2. VOICE */}
          <Section
            title="Voice"
            icon="🔊"
            sectionKey="voice"
            open={openSections.has("voice")}
            onToggle={toggleSection}
            accent={accent}
          >
            <div className="space-y-3">
              <Field label="TTS Provider">
                <Select
                  value={agent.voiceProvider}
                  onChange={(v) => update({ voiceProvider: v })}
                  options={[
                    { value: "google", label: "Google Chirp3-HD (★★★★)" },
                    { value: "gemini", label: "Gemini TTS (★★★)" },
                    { value: "azure", label: "Azure Neural (★★★★)" },
                    { value: "elevenlabs", label: "ElevenLabs (★★★★★)" },
                    { value: "openai", label: "OpenAI TTS (★★)" },
                    { value: "cartesia", label: "Cartesia Sonic-3 (★★)" },
                    { value: "custom", label: "Custom" },
                  ]}
                />
              </Field>
              <Field label="Voice Name">
                <input
                  type="text"
                  value={agent.voice}
                  onChange={(e) => update({ voice: e.target.value })}
                  className="w-full rounded-lg px-3 py-2 text-sm outline-none"
                  style={{
                    background: "var(--depth-3)",
                    color: "var(--text-primary)",
                    border: "1px solid var(--border-subtle)",
                  }}
                />
              </Field>
            </div>
          </Section>

          {/* 3. AI MODEL */}
          <Section
            title="AI Model"
            icon="🧠"
            sectionKey="llm"
            open={openSections.has("llm")}
            onToggle={toggleSection}
            accent={accent}
          >
            <div className="space-y-3">
              <Field label="LLM Provider">
                <Select
                  value={agent.llmProvider}
                  onChange={(v) => update({ llmProvider: v })}
                  options={[
                    { value: "gemini", label: "Google Gemini (★★★★★)" },
                    { value: "openai", label: "OpenAI GPT (★★★★)" },
                    { value: "anthropic", label: "Anthropic Claude (★★★★)" },
                    { value: "groq", label: "Groq (★★★)" },
                    { value: "deepseek", label: "DeepSeek (★★★★)" },
                    { value: "custom", label: "Custom (OpenAI-compatible)" },
                  ]}
                />
              </Field>
              <Field label="Model">
                <input
                  type="text"
                  value={agent.llmModel}
                  onChange={(e) => update({ llmModel: e.target.value })}
                  className="w-full rounded-lg px-3 py-2 text-sm outline-none font-mono"
                  style={{
                    background: "var(--depth-3)",
                    color: "var(--text-primary)",
                    border: "1px solid var(--border-subtle)",
                  }}
                />
              </Field>
            </div>
          </Section>

          {/* 4. TRANSCRIBER */}
          <Section
            title="Transcriber"
            icon="🎙️"
            sectionKey="transcriber"
            open={openSections.has("transcriber")}
            onToggle={toggleSection}
            accent={accent}
          >
            <Field label="STT Provider">
              <Select
                value={agent.transcriber}
                onChange={(v) => update({ transcriber: v })}
                options={[
                  { value: "google", label: "Google Cloud STT (★★★★★)" },
                  { value: "azure", label: "Azure Speech (★★★★)" },
                  { value: "deepgram", label: "Deepgram Nova-3 (★★)" },
                  { value: "elevenlabs", label: "ElevenLabs Scribe (★★★)" },
                  { value: "assemblyai", label: "AssemblyAI (★★★)" },
                ]}
              />
            </Field>
          </Section>

          {/* 5. ACTIONS */}
          <Section
            title="Actions"
            icon="⚡"
            sectionKey="actions"
            open={openSections.has("actions")}
            onToggle={toggleSection}
            accent={accent}
          >
            <div className="space-y-2">
              {(
                [
                  { key: "bookAppointment", label: "Book Appointment", desc: "Google Calendar" },
                  { key: "updateSheet", label: "Update CRM / Sheet", desc: "Google Sheets" },
                  { key: "transferCall", label: "Transfer Call", desc: "Route to department" },
                  { key: "endCall", label: "End Call", desc: "Goodbye + summary" },
                ] as const
              ).map((action) => (
                <label
                  key={action.key}
                  className="flex items-center justify-between p-3 rounded-lg cursor-pointer transition-colors hover:bg-white/[0.02]"
                  style={{ border: "1px solid var(--border-subtle)" }}
                >
                  <div>
                    <span className="text-sm" style={{ color: "var(--text-primary)" }}>
                      {action.label}
                    </span>
                    <p className="text-xs" style={{ color: "var(--text-muted)" }}>
                      {action.desc}
                    </p>
                  </div>
                  <div className="relative">
                    <input
                      type="checkbox"
                      className="sr-only"
                      checked={agent.actions[action.key]}
                      onChange={(e) =>
                        update({
                          actions: { ...agent.actions, [action.key]: e.target.checked },
                        })
                      }
                    />
                    <div
                      className="w-9 h-5 rounded-full transition-colors duration-200"
                      style={{
                        background: agent.actions[action.key] ? accent : "var(--depth-4)",
                      }}
                    >
                      <div
                        className="w-4 h-4 rounded-full bg-white transition-transform duration-200 mt-0.5"
                        style={{
                          transform: agent.actions[action.key]
                            ? "translateX(18px)"
                            : "translateX(2px)",
                        }}
                      />
                    </div>
                  </div>
                </label>
              ))}
            </div>
          </Section>

          {/* 6. PHONE NUMBER */}
          <Section
            title="Phone Number"
            icon="📞"
            sectionKey="phone"
            open={openSections.has("phone")}
            onToggle={toggleSection}
            accent={accent}
          >
            <div className="space-y-3">
              <Field label="Assigned Number">
                <input
                  type="text"
                  value={agent.phoneNumber}
                  onChange={(e) => update({ phoneNumber: e.target.value })}
                  placeholder="+1 (774) 500-7904"
                  className="w-full rounded-lg px-3 py-2 text-sm outline-none font-mono"
                  style={{
                    background: "var(--depth-3)",
                    color: "var(--text-primary)",
                    border: "1px solid var(--border-subtle)",
                  }}
                />
              </Field>
              <Field label="Call Mode">
                <Select
                  value={agent.callMode}
                  onChange={(v) => update({ callMode: v })}
                  options={[
                    { value: "inbound", label: "Inbound Only" },
                    { value: "outbound", label: "Outbound Only" },
                    { value: "both", label: "Both" },
                  ]}
                />
              </Field>
            </div>
          </Section>

          {/* 7. TEST YOUR AGENT */}
          <Section
            title="Test Your Agent"
            icon="🧪"
            sectionKey="test"
            open={openSections.has("test")}
            onToggle={toggleSection}
            accent={accent}
          >
            <TestSection />
          </Section>
        </div>
      </div>
    </div>
  );
}

// === Sub-components ===

function Section({
  title,
  icon,
  sectionKey,
  open,
  onToggle,
  accent,
  children,
}: {
  title: string;
  icon: string;
  sectionKey: SectionKey;
  open: boolean;
  onToggle: (key: SectionKey) => void;
  accent: string;
  children: React.ReactNode;
}) {
  return (
    <div
      className="rounded-xl border transition-colors duration-200"
      style={{
        background: "var(--depth-2)",
        borderColor: open ? accent + "30" : "var(--border-subtle)",
      }}
    >
      <button
        onClick={() => onToggle(sectionKey)}
        className="flex items-center justify-between w-full px-4 py-3 text-left"
      >
        <div className="flex items-center gap-2.5">
          <span className="text-base">{icon}</span>
          <span className="text-sm font-medium" style={{ color: "var(--text-primary)" }}>
            {title}
          </span>
        </div>
        <svg
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          className={`transition-transform duration-200 ${open ? "rotate-180" : ""}`}
          style={{ color: "var(--text-muted)" }}
        >
          <path
            d="M4 6L8 10L12 6"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>
      {open && (
        <div className="px-4 pb-4 animate-fade-in-up">
          {children}
        </div>
      )}
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--text-secondary)" }}>
        {label}
      </label>
      {children}
    </div>
  );
}

function Select({
  value,
  onChange,
  options,
}: {
  value: string;
  onChange: (v: string) => void;
  options: { value: string; label: string }[];
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="w-full rounded-lg px-3 py-2 text-sm outline-none appearance-none cursor-pointer"
      style={{
        background: "var(--depth-3)",
        color: "var(--text-primary)",
        border: "1px solid var(--border-subtle)",
      }}
    >
      {options.map((o) => (
        <option key={o.value} value={o.value}>
          {o.label}
        </option>
      ))}
    </select>
  );
}
