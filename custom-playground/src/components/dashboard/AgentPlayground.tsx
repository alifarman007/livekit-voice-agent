import { useState, useCallback } from "react";
import { AgentConfig, createDefaultAgent, SAMPLE_AGENTS } from "./agentTypes";
import { AgentList } from "./AgentList";
import { TemplatePicker } from "./TemplatePicker";
import { AgentBuilder } from "./AgentBuilder";

type View = "list" | "templates" | "builder";

export function AgentPlayground() {
  const [view, setView] = useState<View>("list");
  const [agents, setAgents] = useState<AgentConfig[]>(SAMPLE_AGENTS);
  const [currentAgent, setCurrentAgent] = useState<AgentConfig | null>(null);

  // Create new agent flow: list → templates → builder
  const handleCreateNew = useCallback(() => {
    setView("templates");
  }, []);

  // Template selected → create agent and open builder
  const handleSelectTemplate = useCallback((templateId: string | null) => {
    const newAgent = createDefaultAgent(templateId || undefined);
    setCurrentAgent(newAgent);
    setView("builder");
  }, []);

  // Edit existing agent → open builder directly
  const handleEdit = useCallback((agent: AgentConfig) => {
    setCurrentAgent({ ...agent });
    setView("builder");
  }, []);

  // Test existing agent → open builder with test section visible
  const handleTest = useCallback((agent: AgentConfig) => {
    setCurrentAgent({ ...agent });
    setView("builder");
  }, []);

  // Save agent
  const handleSave = useCallback(() => {
    if (!currentAgent) return;
    setAgents((prev) => {
      const existing = prev.findIndex((a) => a.id === currentAgent.id);
      if (existing >= 0) {
        const next = [...prev];
        next[existing] = currentAgent;
        return next;
      }
      return [...prev, currentAgent];
    });
    setView("list");
    setCurrentAgent(null);
  }, [currentAgent]);

  // Back navigation
  const handleBackToList = useCallback(() => {
    setView("list");
    setCurrentAgent(null);
  }, []);

  switch (view) {
    case "list":
      return (
        <AgentList
          agents={agents}
          onCreateNew={handleCreateNew}
          onEdit={handleEdit}
          onTest={handleTest}
        />
      );
    case "templates":
      return (
        <TemplatePicker
          onSelectTemplate={handleSelectTemplate}
          onBack={handleBackToList}
        />
      );
    case "builder":
      return currentAgent ? (
        <AgentBuilder
          agent={currentAgent}
          onChange={setCurrentAgent}
          onBack={handleBackToList}
          onSave={handleSave}
        />
      ) : null;
    default:
      return null;
  }
}
