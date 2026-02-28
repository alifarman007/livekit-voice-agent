// Agent configuration type
export interface AgentConfig {
  id: string;
  name: string;
  templateId: string | null;
  status: "live" | "draft";
  callCount: number;
  // Prompt section
  systemPrompt: string;
  firstMessage: string;
  endMessage: string;
  // Voice
  voiceProvider: string;
  voice: string;
  // LLM
  llmProvider: string;
  llmModel: string;
  // Transcriber
  transcriber: string;
  // Actions
  actions: {
    bookAppointment: boolean;
    updateSheet: boolean;
    transferCall: boolean;
    endCall: boolean;
  };
  // Phone
  phoneNumber: string;
  callMode: string;
}

// Template definition
export interface AgentTemplate {
  id: string;
  name: string;
  emoji: string;
  description: string;
  accentColor: string;
  washBg: string;
  borderColor: string;
  defaults: Partial<AgentConfig>;
}

export const TEMPLATES: AgentTemplate[] = [
  {
    id: "receptionist",
    name: "Receptionist",
    emoji: "🏢",
    description: "Front desk — greeting, routing, registration. Handles inbound calls professionally.",
    accentColor: "#3B82F6",
    washBg: "rgba(59,130,246,0.08)",
    borderColor: "rgba(59,130,246,0.2)",
    defaults: {
      systemPrompt: "You are Nusrat, a professional Bangladeshi receptionist...",
      firstMessage: "আসসালামু আলাইকুম, আমাদের কোম্পানি-এ স্বাগতম। আমি নুসরাত।",
      voiceProvider: "google", voice: "bn-BD-Chirp3-HD-Achol",
      llmProvider: "gemini", llmModel: "gemini-2.0-flash-exp",
      transcriber: "google",
    },
  },
  {
    id: "sales",
    name: "Sales Agent",
    emoji: "💰",
    description: "Outbound sales — lead qualification, product pitching, deal closing.",
    accentColor: "#F59E0B",
    washBg: "rgba(245,158,11,0.08)",
    borderColor: "rgba(245,158,11,0.2)",
    defaults: {
      systemPrompt: "You are Nusrat, a friendly Bangladeshi sales representative...",
      firstMessage: "আসসালামু আলাইকুম! আমি নুসরাত, আমাদের নতুন অফার সম্পর্কে জানাতে কল করেছি।",
      voiceProvider: "google", voice: "bn-BD-Chirp3-HD-Achol",
      llmProvider: "gemini", llmModel: "gemini-2.0-flash-exp",
      transcriber: "google",
    },
  },
  {
    id: "survey",
    name: "Survey Agent",
    emoji: "📋",
    description: "Customer satisfaction — NPS scoring, feedback collection.",
    accentColor: "#38D9F5",
    washBg: "rgba(56,217,245,0.08)",
    borderColor: "rgba(56,217,245,0.2)",
    defaults: {
      systemPrompt: "You are Nusrat, conducting customer satisfaction surveys...",
      firstMessage: "আসসালামু আলাইকুম! আমি নুসরাত। আপনার সেবা সম্পর্কে কিছু প্রশ্ন করতে চাই।",
      voiceProvider: "google", voice: "bn-BD-Chirp3-HD-Achol",
      llmProvider: "gemini", llmModel: "gemini-2.0-flash-exp",
      transcriber: "google",
    },
  },
  {
    id: "collections",
    name: "Collections",
    emoji: "💳",
    description: "Payment reminders — billing inquiries, installment plans.",
    accentColor: "#F43F5E",
    washBg: "rgba(244,63,94,0.08)",
    borderColor: "rgba(244,63,94,0.2)",
    defaults: {
      systemPrompt: "You are Nusrat, a polite collections agent...",
      firstMessage: "আসসালামু আলাইকুম! আমি নুসরাত, আপনার বিল সম্পর্কে কল করেছি।",
      voiceProvider: "google", voice: "bn-BD-Chirp3-HD-Achol",
      llmProvider: "gemini", llmModel: "gemini-2.0-flash-exp",
      transcriber: "google",
    },
  },
  {
    id: "appointment",
    name: "Appointment",
    emoji: "📅",
    description: "Focused on scheduling — slot checking, booking, cancellation.",
    accentColor: "#2DD4A8",
    washBg: "rgba(45,212,168,0.08)",
    borderColor: "rgba(45,212,168,0.2)",
    defaults: {
      systemPrompt: "You are Nusrat, an appointment scheduling specialist...",
      firstMessage: "আসসালামু আলাইকুম! আমি নুসরাত। অ্যাপয়েন্টমেন্ট বুক করতে চান?",
      voiceProvider: "google", voice: "bn-BD-Chirp3-HD-Achol",
      llmProvider: "gemini", llmModel: "gemini-2.0-flash-exp",
      transcriber: "google",
    },
  },
  {
    id: "support",
    name: "Tech Support",
    emoji: "🛠️",
    description: "Focused on tickets — troubleshooting, issue tracking.",
    accentColor: "#7364E2",
    washBg: "rgba(115,100,226,0.08)",
    borderColor: "rgba(115,100,226,0.2)",
    defaults: {
      systemPrompt: "You are Nusrat, a technical support specialist...",
      firstMessage: "আসসালামু আলাইকুম! আমি নুসরাত, টেকনিক্যাল সাপোর্ট থেকে বলছি।",
      voiceProvider: "google", voice: "bn-BD-Chirp3-HD-Achol",
      llmProvider: "gemini", llmModel: "gemini-2.0-flash-exp",
      transcriber: "google",
    },
  },
];

export function createDefaultAgent(templateId?: string): AgentConfig {
  const template = TEMPLATES.find((t) => t.id === templateId);
  return {
    id: `agent-${Date.now()}`,
    name: template ? `${template.name} Agent` : "New Agent",
    templateId: templateId || null,
    status: "draft",
    callCount: 0,
    systemPrompt: template?.defaults.systemPrompt || "",
    firstMessage: template?.defaults.firstMessage || "",
    endMessage: "",
    voiceProvider: template?.defaults.voiceProvider || "google",
    voice: template?.defaults.voice || "bn-BD-Chirp3-HD-Achol",
    llmProvider: template?.defaults.llmProvider || "gemini",
    llmModel: template?.defaults.llmModel || "gemini-2.0-flash-exp",
    transcriber: template?.defaults.transcriber || "google",
    actions: {
      bookAppointment: true,
      updateSheet: true,
      transferCall: true,
      endCall: true,
    },
    phoneNumber: "",
    callMode: "inbound",
  };
}

// Sample agents for demo
export const SAMPLE_AGENTS: AgentConfig[] = [
  {
    ...createDefaultAgent("sales"),
    id: "sample-1",
    name: "Nusrat — Sales",
    status: "live",
    callCount: 142,
  },
  {
    ...createDefaultAgent("support"),
    id: "sample-2",
    name: "Nusrat — Support",
    status: "live",
    callCount: 89,
  },
  {
    ...createDefaultAgent("survey"),
    id: "sample-3",
    name: "Nusrat — Survey",
    status: "draft",
    callCount: 0,
  },
];
