import { Loader2 } from "lucide-react";
import type { CalendarAgentResponse } from "../../../types/api";
import { PANEL_CLASS } from "../constants";
import { ActionRow } from "../components/ActionRow";
import type { ChatMessage } from "../types";

export function CalendarPanels({
  busyAction,
  lastResult,
  messages,
  onPlan14,
  onBalance,
  onFindGaps,
}: {
  busyAction: string | null;
  lastResult: CalendarAgentResponse | null;
  messages: ChatMessage[];
  onPlan14: () => void;
  onBalance: () => void;
  onFindGaps: () => void;
}) {
  const isGenerating =
    busyAction === "cal14" ||
    busyAction === "calbalance" ||
    busyAction === "calgaps" ||
    busyAction === "calchat";
  const hasChatHistory = messages.length > 1;
  const visibleMessages = hasChatHistory ? messages.slice(1) : messages;

  return (
    <div className="grid gap-5 2xl:grid-cols-[minmax(0,1fr)_320px]">
      <section className={`${PANEL_CLASS} p-5`}>
        <h2 className="text-2xl font-semibold">Market Calendar</h2>
        <p className="mt-2 text-sm text-white/50">
          Powered by POST /api/v1/agents/calendar/generate
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
                  <p className="whitespace-pre-wrap break-words">{message.text}</p>
                </div>
              ))}
              {isGenerating ? (
                <p className="flex items-center gap-2 text-sm text-white/60">
                  <Loader2 className="size-4 animate-spin" />
                  Calendar agent working…
                </p>
              ) : null}
            </div>
          </div>
        ) : isGenerating ? (
          <p className="mt-4 flex items-center gap-2 text-sm text-white/60">
            <Loader2 className="size-4 animate-spin" />
            Calendar agent working…
          </p>
        ) : lastResult?.response ? (
          <div className="mt-4 rounded-md border border-white/10 bg-[#0D1018] p-4 text-sm leading-6 text-white/80">
            <p className="whitespace-pre-wrap">{lastResult.response}</p>
          </div>
        ) : (
          <p className="mt-4 text-sm text-white/70">
            Ask the calendar agent to plan cadence, balance channels, or find
            gaps using your campaign and schedule context.
          </p>
        )}
      </section>

      <section className={`${PANEL_CLASS} p-5`}>
        <p className="text-xs uppercase tracking-[0.16em] text-white/40">
          Quick tasks
        </p>
        <div className="mt-4 grid gap-2">
          <ActionRow
            label="Plan next 14 days"
            loading={busyAction === "cal14"}
            onClick={onPlan14}
          />
          <ActionRow
            label="Balance channels"
            loading={busyAction === "calbalance"}
            onClick={onBalance}
          />
          <ActionRow
            label="Find calendar gaps"
            loading={busyAction === "calgaps"}
            onClick={onFindGaps}
          />
        </div>
      </section>
    </div>
  );
}
