import { AgentConfig, TEMPLATES } from "./agentTypes";

interface AgentListProps {
  agents: AgentConfig[];
  onCreateNew: () => void;
  onEdit: (agent: AgentConfig) => void;
  onTest: (agent: AgentConfig) => void;
}

export function AgentList({ agents, onCreateNew, onEdit, onTest }: AgentListProps) {
  return (
    <div className="p-6 max-w-[1200px] mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-semibold" style={{ color: "var(--text-primary)" }}>
            Agent Playground
          </h1>
          <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>
            {agents.length} agent{agents.length !== 1 ? "s" : ""} configured
          </p>
        </div>
        <button
          onClick={onCreateNew}
          className="px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 hover:opacity-90"
          style={{ background: "var(--accent-purple)", color: "white" }}
        >
          + New Agent
        </button>
      </div>

      {/* Agent Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {agents.map((agent, i) => {
          const template = TEMPLATES.find((t) => t.id === agent.templateId);
          const accent = template?.accentColor || "#7364E2";
          const wash = template?.washBg || "rgba(115,100,226,0.08)";

          return (
            <div
              key={agent.id}
              className={`animate-fade-in-up stagger-${Math.min(i + 1, 6)} group relative rounded-xl border transition-all duration-200 hover:border-opacity-40`}
              style={{
                background: "var(--depth-2)",
                borderColor: "var(--border-subtle)",
              }}
            >
              {/* Card header with icon */}
              <div className="p-4 pb-3">
                <div className="flex items-start gap-3">
                  {/* Template icon with wash background */}
                  <div
                    className="w-10 h-10 rounded-lg flex items-center justify-center text-lg shrink-0"
                    style={{ background: wash }}
                  >
                    {template?.emoji || "🤖"}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="text-sm font-semibold truncate" style={{ color: "var(--text-primary)" }}>
                        {agent.name}
                      </h3>
                      {/* Status pill */}
                      <span
                        className="shrink-0 inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium"
                        style={{
                          background: agent.status === "live"
                            ? "rgba(45,212,168,0.12)"
                            : "rgba(136,136,160,0.12)",
                          color: agent.status === "live"
                            ? "var(--accent-green)"
                            : "var(--text-secondary)",
                        }}
                      >
                        {agent.status === "live" && (
                          <span className="w-1.5 h-1.5 rounded-full animate-pulse-dot" style={{ background: "var(--accent-green)" }} />
                        )}
                        {agent.status === "live" ? "Live" : "Draft"}
                      </span>
                    </div>
                    <p className="text-xs mt-0.5" style={{ color: "var(--text-muted)" }}>
                      {agent.voiceProvider} / {agent.llmProvider}
                    </p>
                  </div>
                </div>
              </div>

              {/* Card footer */}
              <div
                className="flex items-center justify-between px-4 py-3 border-t"
                style={{ borderColor: "var(--border-subtle)" }}
              >
                <span className="font-mono text-xs" style={{ color: "var(--text-muted)" }}>
                  {agent.callCount} calls
                </span>
                <div className="flex gap-2">
                  <button
                    onClick={() => onEdit(agent)}
                    className="px-3 py-1.5 rounded-md text-xs font-medium transition-colors duration-200 hover:bg-white/5"
                    style={{ color: "var(--text-secondary)", border: "1px solid var(--border-default)" }}
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => onTest(agent)}
                    className="px-3 py-1.5 rounded-md text-xs font-medium transition-colors duration-200"
                    style={{ background: accent, color: "white", opacity: 0.9 }}
                  >
                    Test
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
