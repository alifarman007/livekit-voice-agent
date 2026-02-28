import type { NavItem } from "./Sidebar";

const tabMeta: Record<string, { title: string; desc: string; icon: string }> = {
  dashboard: {
    title: "Dashboard",
    desc: "Overview of calls, agent performance, and real-time metrics.",
    icon: "📊",
  },
  tools: {
    title: "Tools Integration",
    desc: "Connect Google Calendar, Sheets, CRM, and other external services.",
    icon: "🔧",
  },
  number: {
    title: "Phone Numbers",
    desc: "Manage SIP trunks, Twilio numbers, and Bangladesh +880 lines.",
    icon: "📞",
  },
  campaigns: {
    title: "Campaigns",
    desc: "Create and manage outbound calling campaigns.",
    icon: "📢",
  },
  history: {
    title: "Call History",
    desc: "Browse call recordings, transcripts, and analytics.",
    icon: "📋",
  },
  settings: {
    title: "Settings",
    desc: "Account, API keys, billing, and system configuration.",
    icon: "⚙️",
  },
};

interface PlaceholderPageProps {
  tab: NavItem;
}

export function PlaceholderPage({ tab }: PlaceholderPageProps) {
  const meta = tabMeta[tab] || { title: tab, desc: "Coming soon.", icon: "📄" };

  return (
    <div className="flex items-center justify-center h-full">
      <div className="text-center max-w-md animate-fade-in-up">
        <div
          className="w-16 h-16 rounded-2xl flex items-center justify-center text-3xl mx-auto mb-4"
          style={{ background: "var(--depth-2)" }}
        >
          {meta.icon}
        </div>
        <h2 className="text-lg font-semibold mb-2" style={{ color: "var(--text-primary)" }}>
          {meta.title}
        </h2>
        <p className="text-sm mb-4" style={{ color: "var(--text-secondary)" }}>
          {meta.desc}
        </p>
        <div
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs"
          style={{
            background: "rgba(115,100,226,0.1)",
            color: "var(--accent-purple)",
          }}
        >
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
            <circle cx="8" cy="8" r="6" stroke="currentColor" strokeWidth="1.5" />
            <path d="M8 5V8.5L10 10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
          Coming in Phase 2
        </div>
      </div>
    </div>
  );
}
