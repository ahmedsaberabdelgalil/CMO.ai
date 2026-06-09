import { Loader2, Send } from "lucide-react";
import { Button } from "../../../components/ui/button";
import { Input } from "../../../components/ui/input";
import { SuggestionList } from "../components/SuggestionList";
import type { Agent, AgentSuggestion, ChatMessage } from "../types";

export function CalendarRightAside({
  activeAgent,
  campaignName,
  messages,
  draft,
  onDraftChange,
  onSend,
  suggestions,
  onPlan14,
  onBalance,
  onFindGaps,
  busyAction,
}: {
  activeAgent: Agent;
  campaignName: string;
  messages: ChatMessage[];
  draft: string;
  onDraftChange: (v: string) => void;
  onSend: (message?: string) => void;
  suggestions: AgentSuggestion[];
  onPlan14: () => void;
  onBalance: () => void;
  onFindGaps: () => void;
  busyAction: string | null;
}) {
  const Icon = activeAgent.icon;
  const isBusy =
    busyAction === "cal14" ||
    busyAction === "calbalance" ||
    busyAction === "calgaps" ||
    busyAction === "calchat";

  const runQuick = (label: string) => {
    if (label === "Plan next 14 days" || label === "Generate next 14 days") {
      onPlan14();
      return;
    }
    if (label === "Balance channels") onBalance();
    if (label === "Find calendar gaps") onFindGaps();
  };

  return (
    <aside className="border-t border-white/10 bg-[#0D1018] xl:border-l xl:border-t-0">
      <div className="flex h-full min-h-[560px] flex-col">
        <div className="border-b border-white/10 px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-md bg-white/10">
              <Icon className={`size-5 ${activeAgent.accent}`} />
            </div>
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold">{activeAgent.name}</p>
              <p className="truncate text-xs text-white/45">{campaignName}</p>
            </div>
          </div>
        </div>

        <div className="flex-1 space-y-3 overflow-y-auto px-4 py-4">
          <SuggestionList suggestions={suggestions} onSelect={runQuick} />
          {messages.map((message, index) => (
            <div
              key={`${message.role}-${index}`}
              className={`rounded-md px-3 py-2 text-sm leading-6 ${
                message.role === "user"
                  ? "ml-8 bg-neonBlue text-cosmic"
                  : "mr-8 bg-white/[0.07] text-white/80"
              }`}
            >
              <p className="whitespace-pre-wrap break-words">{message.text}</p>
            </div>
          ))}
          {isBusy ? (
            <p className="flex items-center gap-2 text-xs text-white/50">
              <Loader2 className="size-3 animate-spin" />
              Calendar agent working…
            </p>
          ) : null}
        </div>

        <div className="border-t border-white/10 p-4">
          <div className="mb-3 grid gap-2">
            {["Plan next 14 days", "Balance channels", "Find calendar gaps"].map(
              (action) => (
                <button
                  key={action}
                  type="button"
                  disabled={isBusy}
                  onClick={() => runQuick(action)}
                  className="rounded-md border border-white/10 px-3 py-2 text-left text-xs text-white/70 transition hover:border-neonBlue/60 hover:text-white disabled:opacity-50"
                >
                  {action}
                </button>
              ),
            )}
          </div>

          <form
            className="flex gap-2"
            onSubmit={(e) => {
              e.preventDefault();
              onSend();
            }}
          >
            <Input
              value={draft}
              onChange={(e) => onDraftChange(e.target.value)}
              disabled={isBusy}
              placeholder="Ask Calendar agent"
              className="h-11 border-white/10 bg-white text-cosmic placeholder:text-slate-500"
            />
            <Button
              type="submit"
              size="icon"
              disabled={isBusy || !draft.trim()}
              className="h-11 w-11 bg-neonPink text-white hover:bg-neonPink/90"
            >
              <Send className="size-4" />
            </Button>
          </form>
        </div>
      </div>
    </aside>
  );
}
