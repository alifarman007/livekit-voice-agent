import { TEMPLATES } from "./agentTypes";

interface TemplatePickerProps {
  onSelectTemplate: (templateId: string | null) => void;
  onBack: () => void;
}

export function TemplatePicker({ onSelectTemplate, onBack }: TemplatePickerProps) {
  return (
    <div className="p-6 max-w-[900px] mx-auto">
      {/* Back button + Header */}
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-sm mb-4 transition-colors duration-200"
        style={{ color: "var(--text-secondary)" }}
      >
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M10 12L6 8L10 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
        Back to Agents
      </button>

      <h1 className="text-xl font-semibold mb-2" style={{ color: "var(--text-primary)" }}>
        Choose a Template
      </h1>
      <p className="text-sm mb-6" style={{ color: "var(--text-secondary)" }}>
        Start with a pre-configured agent or build from scratch.
      </p>

      {/* Template Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {TEMPLATES.map((template, i) => (
          <button
            key={template.id}
            onClick={() => onSelectTemplate(template.id)}
            className={`animate-fade-in-up stagger-${Math.min(i + 1, 6)} group relative text-left rounded-xl border overflow-hidden transition-all duration-200 hover:shadow-lg`}
            style={{
              background: "var(--depth-2)",
              borderColor: "var(--border-subtle)",
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLElement).style.borderColor = template.accentColor + "40";
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLElement).style.borderColor = "var(--border-subtle)";
            }}
          >
            {/* Top color bar */}
            <div className="h-[3px] w-full relative overflow-hidden">
              <div
                className="absolute inset-0 origin-left transition-transform duration-300 scale-x-0 group-hover:scale-x-100"
                style={{ background: template.accentColor }}
              />
            </div>

            <div className="p-4">
              {/* Emoji on wash bg */}
              <div
                className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl mb-3 transition-transform duration-200 group-hover:scale-105"
                style={{ background: template.washBg }}
              >
                {template.emoji}
              </div>

              <h3 className="text-sm font-semibold mb-1" style={{ color: "var(--text-primary)" }}>
                {template.name}
              </h3>
              <p className="text-xs leading-relaxed" style={{ color: "var(--text-secondary)" }}>
                {template.description}
              </p>

              {/* Use This button */}
              <div className="flex items-center gap-1 mt-3 text-xs font-medium transition-all duration-200 group-hover:gap-2"
                style={{ color: template.accentColor }}
              >
                Use This
                <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
                  <path d="M6 4L10 8L6 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
            </div>
          </button>
        ))}

        {/* Build from Scratch */}
        <button
          onClick={() => onSelectTemplate(null)}
          className="animate-fade-in-up stagger-6 group text-left rounded-xl border border-dashed transition-all duration-200 hover:border-white/20"
          style={{
            background: "transparent",
            borderColor: "var(--border-default)",
          }}
        >
          <div className="h-[3px]" />
          <div className="p-4">
            <div
              className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl mb-3 transition-transform duration-200 group-hover:scale-105"
              style={{ background: "rgba(255,255,255,0.04)" }}
            >
              ✨
            </div>
            <h3 className="text-sm font-semibold mb-1" style={{ color: "var(--text-primary)" }}>
              Build from Scratch
            </h3>
            <p className="text-xs leading-relaxed" style={{ color: "var(--text-secondary)" }}>
              Start with a blank canvas and configure everything yourself.
            </p>
            <div className="flex items-center gap-1 mt-3 text-xs font-medium transition-all duration-200 group-hover:gap-2"
              style={{ color: "var(--text-secondary)" }}
            >
              Start Building
              <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
                <path d="M6 4L10 8L6 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
          </div>
        </button>
      </div>
    </div>
  );
}
