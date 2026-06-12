import { Loader2 } from "lucide-react";
import type { ContentAgentStatus, TextAgentResponse } from "../../../types/api";
import { PANEL_CLASS } from "../constants";
import { ActionRow } from "../components/ActionRow";
import { TextAgentResultBody } from "../components/TextAgentResultBody";
import type { ChatMessage } from "../types";

export function TextPanels({
  agentStatus,
  busyAction,
  lastResult,
  messages,
  onLinkedIn,
  onEmail,
  onHooks,
}: {
  agentStatus: ContentAgentStatus | null;
  busyAction: string | null;
  lastResult: TextAgentResponse | null;
  messages: ChatMessage[];
  onLinkedIn: () => void;
  onEmail: () => void;
  onHooks: () => void;
}) {
  const isGenerating =
    busyAction === "li" ||
    busyAction === "email" ||
    busyAction === "hooks" ||
    busyAction === "textchat";
  const hasChatHistory = messages.length > 1;
  const visibleMessages = hasChatHistory ? messages.slice(1) : messages;

  return (
    <div className="grid gap-5 2xl:grid-cols-[minmax(0,1fr)_320px]">
      <section className={`${PANEL_CLASS} p-5`}>
        <div className="flex flex-wrap items-center gap-3">
          <h2 className="text-2xl font-semibold">Text Generation</h2>
          {agentStatus ? (
            <div
              className={`rounded-full border px-3 py-1 text-xs font-medium ${
                agentStatus.mode === "live"
                  ? "border-emerald-400/30 bg-emerald-400/10 text-emerald-200"
                  : "border-amber-400/30 bg-amber-400/10 text-amber-200"
              }`}
            >
              {agentStatus.mode === "live"
                ? `Live: ${agentStatus.provider} / ${agentStatus.model}`
                : "Fallback writing mode"}
            </div>
          ) : null}
        </div>
        <p className="mt-2 text-sm text-white/50">
          Write posts, ads, emails, and landing copy on brand.
        </p>
        {hasChatHistory ? (
          <div className="mt-4 max-h-96 overflow-y-auto rounded-md border border-white/10 bg-[#0D1018] p-3 text-sm leading-6 text-white/80">
            <div className="space-y-3">
              {visibleMessages.map((message, index) => (
                <div
                  key={`${message.role}-${index}`}
                  className={`rounded-md px-3 py-2 ${
                    message.role === "user"
                      ? "ml-auto max-w-[88%] bg-neonBlue text-cosmic"
                      : "mr-auto max-w-full bg-white/[0.06] text-white/85"
                  }`}
                >
                  <p className="whitespace-pre-wrap break-words">
                    {message.text}
                  </p>
                </div>
              ))}
              {isGenerating ? (
                <p className="flex items-center gap-2 text-sm text-white/60">
                  <Loader2 className="size-4 animate-spin" /> Generating...
                </p>
              ) : null}
            </div>
          </div>
        ) : isGenerating ? (
          <p className="flex items-center gap-2 mt-4 text-sm text-white/60">
            <Loader2 className="size-4 animate-spin" /> Generating...
          </p>
        ) : lastResult ? (
          <div className="mt-4 max-h-96 overflow-y-auto rounded-md border border-white/10 bg-[#0D1018] p-3 text-sm leading-6 text-white/80">
            <TextAgentResultBody result={lastResult} />
          </div>
        ) : (
          <p className="mt-3 text-sm text-white/70">
            Use quick actions or Ask Text to generate copy for this campaign.
          </p>
        )}
      </section>

      <section className={`${PANEL_CLASS} p-5`}>
        <p className="text-xs uppercase tracking-[0.16em] text-white/40">
          Current focus
        </p>
        <div className="grid gap-2 mt-4">
          <ActionRow
            label="Write LinkedIn posts"
            loading={busyAction === "li"}
            onClick={onLinkedIn}
          />
          <ActionRow
            label="Draft email sequence"
            loading={busyAction === "email"}
            onClick={onEmail}
          />
          <ActionRow
            label="Create ad hooks"
            loading={busyAction === "hooks"}
            onClick={onHooks}
          />
        </div>
      </section>
    </div>
  );
}
