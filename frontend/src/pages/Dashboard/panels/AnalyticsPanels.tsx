import { Loader2 } from "lucide-react";
import type { AnalyticsAgentResponse } from "../../../types/api";
import { PANEL_CLASS } from "../constants";
import { ActionRow } from "../components/ActionRow";
import type { ChatMessage } from "../types";

export function AnalyticsPanels({
  busyAction,
  lastResult,
  messages,
  onSummarize,
  onWeakFunnel,
  onBudgetShift,
}: {
  busyAction: string | null;
  lastResult: AnalyticsAgentResponse | null;
  messages: ChatMessage[];
  onSummarize: () => void;
  onWeakFunnel: () => void;
  onBudgetShift: () => void;
}) {
  const isGenerating =
    busyAction === "asum" ||
    busyAction === "afunnel" ||
    busyAction === "abudget" ||
    busyAction === "analychat";
  const hasChatHistory = messages.length > 1;
  const visibleMessages = hasChatHistory ? messages.slice(1) : messages;

  return (
    <div className="grid gap-5 2xl:grid-cols-[minmax(0,1fr)_320px]">
      <section className={`${PANEL_CLASS} p-5`}>
        <h2 className="text-2xl font-semibold">Performance Analytics</h2>
        <p className="mt-2 text-sm text-white/50">
          Data-driven insights from your campaign performance.
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
                  Analytics agent working…
                </p>
              ) : null}
            </div>
          </div>
        ) : isGenerating ? (
          <p className="mt-4 flex items-center gap-2 text-sm text-white/60">
            <Loader2 className="size-4 animate-spin" />
            Analytics agent working…
          </p>
        ) : lastResult?.response ? (
          <div className="mt-4 rounded-md border border-white/10 bg-[#0D1018] p-4 text-sm leading-6 text-white/80">
            <p className="whitespace-pre-wrap">{lastResult.response}</p>
          </div>
        ) : (
          <p className="mt-4 text-sm text-white/70">
            Ask the analytics agent to summarize performance, find weak funnel
            steps, or suggest budget shifts using your metrics context.
          </p>
        )}
      </section>

      <section className={`${PANEL_CLASS} p-5`}>
        <p className="text-xs uppercase tracking-[0.16em] text-white/40">
          Quick tasks
        </p>
        <div className="mt-4 grid gap-2">
          <ActionRow
            label="Summarize performance"
            loading={busyAction === "asum"}
            onClick={onSummarize}
          />
          <ActionRow
            label="Find weak funnel step"
            loading={busyAction === "afunnel"}
            onClick={onWeakFunnel}
          />
          <ActionRow
            label="Suggest budget shift"
            loading={busyAction === "abudget"}
            onClick={onBudgetShift}
          />
        </div>
      </section>
    </div>
  );
}
