import Head from "next/head";
import { useState } from "react";
import { Sidebar, NavItem } from "@/components/dashboard/Sidebar";
import { AgentPlayground } from "@/components/dashboard/AgentPlayground";
import { PlaceholderPage } from "@/components/dashboard/PlaceholderPage";

export default function Home() {
  const [activeTab, setActiveTab] = useState<NavItem>("agents");

  return (
    <>
      <Head>
        <title>LandPhone AI — Voice Agent Dashboard</title>
        <meta name="description" content="Bengali voice AI agent management dashboard" />
        <meta
          name="viewport"
          content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no"
        />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="flex h-full w-full" style={{ background: "var(--depth-0)" }}>
        {/* Sidebar */}
        <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />

        {/* Main content area */}
        <main className="flex-1 overflow-y-auto" style={{ background: "var(--depth-0)" }}>
          {activeTab === "agents" ? (
            <AgentPlayground />
          ) : (
            <PlaceholderPage tab={activeTab} />
          )}
        </main>
      </div>
    </>
  );
}
