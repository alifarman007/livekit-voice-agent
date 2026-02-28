import { useState } from "react";

export type NavItem =
  | "dashboard"
  | "agents"
  | "tools"
  | "number"
  | "campaigns"
  | "history"
  | "settings";

const navItems: { id: NavItem; label: string; icon: string }[] = [
  { id: "dashboard", label: "Dashboard", icon: "📊" },
  { id: "agents", label: "Agent Playground", icon: "🤖" },
  { id: "tools", label: "Tools Integration", icon: "🔧" },
  { id: "number", label: "Number", icon: "📞" },
  { id: "campaigns", label: "Campaigns", icon: "📢" },
  { id: "history", label: "Call History", icon: "📋" },
  { id: "settings", label: "Settings", icon: "⚙️" },
];

interface SidebarProps {
  activeTab: NavItem;
  onTabChange: (tab: NavItem) => void;
}

export function Sidebar({ activeTab, onTabChange }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false);

  const activeIndex = navItems.findIndex((n) => n.id === activeTab);

  return (
    <aside
      className="flex flex-col h-full shrink-0 transition-all duration-300 ease-in-out relative"
      style={{
        width: collapsed ? 56 : 224,
        background: "var(--depth-1)",
        borderRight: "1px solid var(--border-subtle)",
      }}
    >
      {/* Logo area */}
      <div
        className="flex items-center gap-3 px-4 shrink-0"
        style={{ height: 56 }}
      >
        {/* Waveform logo */}
        <div className="flex items-end gap-[2px] h-6 cursor-pointer group">
          {[0.4, 0.7, 1].map((scale, i) => (
            <div
              key={i}
              className="w-[3px] rounded-full transition-transform duration-300 group-hover:animate-pulse"
              style={{
                height: `${scale * 20}px`,
                background: "var(--accent-purple)",
                animationDelay: `${i * 0.1}s`,
              }}
            />
          ))}
        </div>
        {!collapsed && (
          <span className="text-sm font-semibold text-white whitespace-nowrap">
            LandPhone AI
          </span>
        )}
      </div>

      {/* Nav items */}
      <nav className="flex-1 px-2 py-3 relative">
        {/* Animated pill indicator */}
        <div
          className="absolute left-2 right-2 h-9 rounded-lg transition-all duration-300 ease-in-out z-0"
          style={{
            top: `${12 + activeIndex * 44}px`,
            background: "var(--accent-purple)",
            opacity: 0.12,
          }}
        />

        {navItems.map((item) => {
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className="relative z-10 flex items-center gap-3 w-full px-3 h-9 mb-[8px] rounded-lg text-sm transition-colors duration-200"
              style={{
                color: isActive
                  ? "var(--accent-purple)"
                  : "var(--text-secondary)",
              }}
              title={collapsed ? item.label : undefined}
            >
              <span className="text-base shrink-0">{item.icon}</span>
              {!collapsed && (
                <span
                  className="whitespace-nowrap transition-opacity duration-200"
                  style={{ fontWeight: isActive ? 600 : 400 }}
                >
                  {item.label}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="flex items-center justify-center h-10 mx-2 mb-2 rounded-lg transition-colors duration-200 hover:bg-white/5"
        style={{ color: "var(--text-muted)" }}
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          className={`transition-transform duration-300 ${collapsed ? "rotate-180" : ""}`}
        >
          <path
            d="M10 12L6 8L10 4"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>

      {/* User footer */}
      <div
        className="flex items-center gap-3 px-4 shrink-0 border-t"
        style={{
          height: 56,
          borderColor: "var(--border-subtle)",
        }}
      >
        {/* Avatar */}
        <div
          className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold shrink-0"
          style={{ background: "var(--accent-purple)", color: "white" }}
        >
          A
        </div>
        {!collapsed && (
          <div className="flex flex-col min-w-0">
            <span className="text-xs font-medium text-white truncate">
              Alif
            </span>
            <div className="flex items-center gap-1">
              <div
                className="w-1.5 h-1.5 rounded-full animate-pulse-dot"
                style={{ background: "var(--accent-green)" }}
              />
              <span
                className="text-[10px]"
                style={{ color: "var(--text-muted)" }}
              >
                Pro Plan
              </span>
            </div>
          </div>
        )}
      </div>
    </aside>
  );
}
