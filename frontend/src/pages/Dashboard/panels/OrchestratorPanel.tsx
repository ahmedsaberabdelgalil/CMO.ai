import { ChevronRight, Loader2, Megaphone } from "lucide-react";
import type { CampaignOut } from "../../../types/api";
import { agents, nextActions, PANEL_CLASS, SUBPANEL_CLASS } from "../constants";
import type { AgentId, ChatMessage } from "../types";
import { formatLaunchDate, getAgentDemoIntro } from "../utils";

export function OrchestratorPanel({
  campaign,
  brandAudience,
  messages,
  busyAction,
  onPickAgent,
  onQuickAction,
}: {
  campaign: CampaignOut;
  brandAudience: string | null;
  messages: ChatMessage[];
  busyAction: string | null;
  onPickAgent: (agentId: AgentId) => void;
  onQuickAction: (action: string) => void;
}) {
  const launch = formatLaunchDate(campaign.start_date);
  const isGenerating = busyAction === "orchchat";
  const hasChatHistory = messages.length > 1;
  const visibleMessages = hasChatHistory ? messages.slice(1) : messages;

  return (
    <div className="space-y-5">
      <section className="grid gap-4 lg:grid-cols-3">
        <div className={`${PANEL_CLASS} p-5 lg:col-span-2`}>
          <div className="flex items-center gap-2 text-neonBlue">
            <Megaphone className="size-5" />
            <h2 className="text-lg font-semibold">Orchestrator</h2>
          </div>
          <p className="mt-3 text-sm leading-6 text-white/70">
            {getAgentDemoIntro("orchestrator", campaign, brandAudience)}
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
                    {message.images?.length ? (
                      <div className="grid grid-cols-2 gap-2 mt-3">
                        {message.images.map((src, i) => (
                          <a
                            key={`img-${i}`}
                            href={src}
                            target="_blank"
                            rel="noreferrer"
                          >
                            <img
                              src={src}
                              alt="Generated asset"
                              className="w-full border rounded-md border-white/10"
                            />
                          </a>
                        ))}
                      </div>
                    ) : null}
                    {message.videoUrl ? (
                      <video
                        src={message.videoUrl}
                        controls
                        className="w-full mt-3 border rounded-md border-white/10"
                      />
                    ) : null}
                  </div>
                ))}
                {isGenerating ? (
                  <p className="flex items-center gap-2 text-sm text-white/60">
                    <Loader2 className="size-4 animate-spin" />
                    Orchestrator routing…
                  </p>
                ) : null}
              </div>
            </div>
          ) : isGenerating ? (
            <p className="mt-4 flex items-center gap-2 text-sm text-white/60">
              <Loader2 className="size-4 animate-spin" />
              Orchestrator routing…
            </p>
          ) : null}

          <div className="grid gap-2 mt-4 md:grid-cols-3">
            {nextActions.orchestrator.map((action) => (
              <button
                key={action}
                type="button"
                disabled={isGenerating}
                onClick={() => onQuickAction(action)}
                className={`${SUBPANEL_CLASS} px-3 py-2 text-left text-xs text-white/85 transition hover:border-neonBlue/60 hover:text-white disabled:opacity-50`}
              >
                {action}
              </button>
            ))}
          </div>
        </div>

        <div className={`${PANEL_CLASS} p-5`}>
          <p className="text-xs uppercase tracking-[0.16em] text-white/40">
            Audience
          </p>
          <p className="mt-2 text-sm leading-6 text-white/75">
            {brandAudience?.trim() ||
              "Audience details will load from the linked brand."}
          </p>
          <div className={`mt-4 ${SUBPANEL_CLASS} px-3 py-2 text-sm`}>
            <p className="text-white/45">Launch</p>
            <p className="mt-1 font-medium text-white/80">{launch}</p>
          </div>
        </div>
      </section>

      <section className="grid gap-3 md:grid-cols-2 2xl:grid-cols-3">
        {agents
          .filter((agent) => agent.id !== "orchestrator")
          .map((agent) => {
            const Icon = agent.icon;

            return (
              <button
                key={agent.id}
                type="button"
                onClick={() => onPickAgent(agent.id)}
                className={`${PANEL_CLASS} p-4 text-left transition hover:border-neonBlue/60 hover:bg-white/[0.07]`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center min-w-0 gap-3">
                    <Icon className={`size-5 shrink-0 ${agent.accent}`} />
                    <div className="min-w-0">
                      <p className="font-medium truncate">{agent.name}</p>
                      <p className="mt-1 text-xs truncate text-white/45">
                        {agent.description}
                      </p>
                    </div>
                  </div>
                  <ChevronRight className="size-4 shrink-0 text-white/35" />
                </div>
                <p className="mt-4 text-xs font-medium text-white/55">
                  Open agent
                </p>
              </button>
            );
          })}
      </section>
    </div>
  );
}
