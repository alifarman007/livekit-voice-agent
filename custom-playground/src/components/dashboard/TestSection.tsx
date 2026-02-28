import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  BarVisualizer,
  SessionProvider,
  StartAudio,
  RoomAudioRenderer,
  useSession,
  useAgent,
  useSessionMessages,
} from "@livekit/components-react";
import {
  ConnectionState,
  TokenSourceConfigurable,
} from "livekit-client";
import type { AgentConfig } from "./agentTypes";

type CallState = "idle" | "connecting" | "active";

interface TestSectionProps {
  agentName?: string;
  agentConfig?: AgentConfig | null;
}

export function TestSection({ agentName, agentConfig }: TestSectionProps) {
  const [callState, setCallState] = useState<CallState>("idle");

  // Use a ref so the token source always reads the LATEST config
  // without re-creating the token source (which would break useSession)
  const agentConfigRef = useRef(agentConfig);
  agentConfigRef.current = agentConfig;

  // Custom token source that injects agent_config into the POST body
  // so token.ts can set it as room metadata for agent.py to read.
  //
  // LiveKit SDK calls tokenSource.fetch(payload) internally —
  // we intercept this to add our agent_config field.
  const tokenSource = useMemo<TokenSourceConfigurable | undefined>(() => {
    if (!process.env.NEXT_PUBLIC_LIVEKIT_URL) return undefined;

    const source = {
      fetch: async (payload: Record<string, unknown>) => {
        const body: Record<string, unknown> = { ...payload };

        // ═══════ METADATA BRIDGE ═══════
        // Inject agent config from the dashboard AgentBuilder.
        // token.ts will set this as room metadata.
        // agent.py will read ctx.room.metadata and use dynamic config.
        const cfg = agentConfigRef.current;
        if (cfg) {
          body.agent_config = {
            system_prompt: cfg.systemPrompt,
            first_message: cfg.firstMessage,
            end_message: cfg.endMessage,
            stt_provider: cfg.transcriber,
            llm_provider: cfg.llmProvider,
            llm_model: cfg.llmModel,
            tts_provider: cfg.voiceProvider,
            tts_voice: cfg.voice,
            actions: cfg.actions,
          };
        }

        const res = await window.fetch("/api/token", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });

        if (!res.ok) throw new Error(`Token request failed: ${res.status}`);
        const data = await res.json();

        return {
          serverUrl: data.server_url as string,
          participantToken: data.participant_token as string,
        };
      },
    };

    return source as unknown as TokenSourceConfigurable;
  }, []); // No deps — uses ref for latest config

  if (!tokenSource) {
    return (
      <div className="text-center py-8" style={{ color: "var(--text-muted)" }}>
        <p className="text-sm">LiveKit URL not configured.</p>
        <p className="text-xs mt-1">Set NEXT_PUBLIC_LIVEKIT_URL in .env.local</p>
      </div>
    );
  }

  return (
    <TestSectionInner
      tokenSource={tokenSource}
      callState={callState}
      setCallState={setCallState}
      agentName={agentName}
    />
  );
}

function TestSectionInner({
  tokenSource,
  callState,
  setCallState,
  agentName,
}: {
  tokenSource: TokenSourceConfigurable;
  callState: CallState;
  setCallState: (s: CallState) => void;
  agentName?: string;
}) {
  const session = useSession(tokenSource, agentName ? { agentName } : undefined);
  const { connectionState } = session;
  const agent = useAgent(session);
  const messages = useSessionMessages(session);

  // Sync connection state to our callState
  useEffect(() => {
    if (connectionState === ConnectionState.Connected) {
      setCallState("active");
    } else if (connectionState === ConnectionState.Connecting) {
      setCallState("connecting");
    } else if (connectionState === ConnectionState.Disconnected) {
      setCallState("idle");
    }
  }, [connectionState, setCallState]);

  // Enable mic when connected
  useEffect(() => {
    if (connectionState === ConnectionState.Connected) {
      session.room.localParticipant.setMicrophoneEnabled(true);
    }
  }, [connectionState, session.room.localParticipant]);

  const handleStartCall = useCallback(() => {
    if (session.isConnected) return;
    session.start();
    setCallState("connecting");
  }, [session, setCallState]);

  const handleEndCall = useCallback(() => {
    session.end();
    setCallState("idle");
  }, [session, setCallState]);

  return (
    <SessionProvider session={session}>
      <div className="space-y-4">
        {/* Call Button Area */}
        <div className="flex flex-col items-center py-6">
          {callState === "idle" && (
            <button
              onClick={handleStartCall}
              className="relative group"
            >
              {/* Pulse ring behind button */}
              <div
                className="absolute inset-0 rounded-full animate-pulse-ring"
                style={{
                  background: "var(--accent-cyan)",
                  opacity: 0.2,
                  transform: "scale(1)",
                }}
              />
              <div
                className="relative w-[88px] h-[88px] rounded-full flex items-center justify-center transition-all duration-300 group-hover:scale-105"
                style={{
                  background: "linear-gradient(135deg, var(--accent-cyan), #2BA8C7)",
                  boxShadow: "0 0 30px rgba(56,217,245,0.2)",
                }}
              >
                {/* Phone icon */}
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z"
                    fill="white"
                  />
                </svg>
              </div>
              <p className="text-xs mt-3 text-center" style={{ color: "var(--text-secondary)" }}>
                Start Test Call
              </p>
            </button>
          )}

          {callState === "connecting" && (
            <div className="flex flex-col items-center">
              <div
                className="w-[88px] h-[88px] rounded-full flex items-center justify-center animate-connecting-pulse"
                style={{
                  background: "var(--depth-3)",
                  border: "2px solid var(--accent-cyan)",
                }}
              >
                {/* Bouncing dots */}
                <div className="flex gap-1.5">
                  <div className="w-2 h-2 rounded-full animate-bounce-dot-1" style={{ background: "var(--accent-cyan)" }} />
                  <div className="w-2 h-2 rounded-full animate-bounce-dot-2" style={{ background: "var(--accent-cyan)" }} />
                  <div className="w-2 h-2 rounded-full animate-bounce-dot-3" style={{ background: "var(--accent-cyan)" }} />
                </div>
              </div>
              <p className="text-xs mt-3 animate-connecting-pulse" style={{ color: "var(--accent-cyan)" }}>
                Connecting to Nusrat...
              </p>
            </div>
          )}

          {callState === "active" && (
            <div className="flex flex-col items-center w-full">
              {/* Audio Visualizer — uses REAL LiveKit agent audio */}
              <div
                className="w-full rounded-xl p-6 mb-4 glow-cyan"
                style={{ background: "var(--depth-3)" }}
              >
                <div className="flex items-center justify-center h-20 [--lk-va-bar-width:20px] [--lk-va-bar-gap:12px] [--lk-fg:var(--accent-cyan)]">
                  {agent.microphoneTrack ? (
                    <BarVisualizer
                      state={agent.state}
                      track={agent.microphoneTrack}
                      barCount={5}
                      options={{ minHeight: 12 }}
                    />
                  ) : (
                    /* Fallback bars while waiting for agent audio track */
                    <div className="flex items-center gap-[12px]">
                      {[1,2,3,4,5].map(n => (
                        <div
                          key={n}
                          className={`w-[20px] rounded-sm animate-bar-${n}`}
                          style={{ background: "var(--accent-cyan)" }}
                        />
                      ))}
                    </div>
                  )}
                </div>

                <div className="flex items-center justify-center gap-2 mt-2">
                  <div className="w-2 h-2 rounded-full animate-pulse-dot" style={{ background: "var(--accent-cyan)" }} />
                  <span className="text-xs font-mono" style={{ color: "var(--accent-cyan)" }}>
                    {agent.isConnected ? "Agent Connected" : "Waiting for agent..."}
                  </span>
                </div>
              </div>

              {/* End Call button */}
              <button
                onClick={handleEndCall}
                className="px-6 py-2 rounded-full text-sm font-medium transition-all duration-200 hover:opacity-90"
                style={{ background: "#F43F5E", color: "white" }}
              >
                End Call
              </button>
            </div>
          )}
        </div>

        {/* Live Transcript */}
        {callState === "active" && (
          <div
            className="rounded-xl p-4 max-h-[240px] overflow-y-auto"
            style={{ background: "var(--depth-3)" }}
          >
            <h4 className="text-xs font-semibold mb-3" style={{ color: "var(--text-secondary)" }}>
              LIVE TRANSCRIPT
            </h4>
            <div className="space-y-2">
              {messages.messages.length === 0 ? (
                <p className="text-xs italic" style={{ color: "var(--text-muted)" }}>
                  Listening... Start speaking in Bengali.
                </p>
              ) : (
                messages.messages.map((msg, i) => {
                  const isAgent = msg.type === "agentTranscript";
                  const text = "message" in msg ? (msg as { message: string }).message : "";
                  if (!text) return null;
                  return (
                    <div
                      key={i}
                      className={`flex gap-2 animate-fade-in-up ${
                        isAgent ? "justify-start" : "justify-end"
                      }`}
                    >
                      <div
                        className="max-w-[80%] px-3 py-2 rounded-lg text-xs"
                        style={{
                          background: isAgent
                            ? "rgba(56,217,245,0.1)"
                            : "rgba(115,100,226,0.1)",
                          color: isAgent
                            ? "var(--accent-cyan)"
                            : "var(--accent-purple)",
                        }}
                      >
                        <span className="font-medium text-[10px] block mb-0.5 opacity-60">
                          {isAgent ? "Nusrat" : "You"}
                        </span>
                        {text}
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        )}
      </div>

      <RoomAudioRenderer />
      <StartAudio label="Click to enable audio playback" />
    </SessionProvider>
  );
}
