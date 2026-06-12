import { Loader2 } from "lucide-react";
import type { CampaignOut } from "../../../types/api";
import { nextActions, PANEL_CLASS } from "../constants";
import { getAgentDemoIntro } from "../utils";
import { ActionRow } from "../components/ActionRow";
import type { ChatMessage } from "../types";

export function BrandPanels({
  campaign,
  brandAudience,
  messages,
  busyAction,
  onQuickAction,
  onReport,
  onSaveProfile,
}: {
  campaign: CampaignOut;
  brandAudience: string | null;
  messages: ChatMessage[];
  busyAction: string | null;
  onQuickAction: (action: string) => void;
  onReport: () => void;
  onSaveProfile: () => void;
}) {
  const isGenerating =
    busyAction === "brandchat" ||
    busyAction === "brandreport" ||
    busyAction === "brandsave";
  const hasChatHistory = messages.length > 1;
  const visibleMessages = hasChatHistory ? messages.slice(1) : messages;

  return (
    <div className="grid gap-5 2xl:grid-cols-[minmax(0,1fr)_320px]">
      <section className={`${PANEL_CLASS} p-5`}>
        <h2 className="text-2xl font-semibold">Brand Coaching</h2>
        <p className="mt-2 text-sm text-white/50">
          Answer a few questions and I'll build and save your brand profile.
        </p>

        {hasChatHistory ? (
          <div className="mt-4 max-h-96 overflow-y-auto rounded-md border border-white/10 bg-[#0D1018] p-3 text-sm leading-6 text-white/80">
            <div className="space-y-3">
              {visibleMessages.map((message, index) => (
                <div
                  key={`${message.role}-${index}`}
                  className={`rounded-md px-3 py-2 ${
                    message.role === "user"
                      ? "ml-auto max-w-[88%] bg-neonPurple text-white"
                      : "mr-auto max-w-full bg-white/[0.06] text-white/85"
                  }`}
                >
                  <p className="whitespace-pre-wrap break-words">{message.text}</p>
                </div>
              ))}
              {isGenerating ? (
                <p className="flex items-center gap-2 text-sm text-white/60">
                  <Loader2 className="size-4 animate-spin" />
                  Brand coach working…
                </p>
              ) : null}
            </div>
          </div>
        ) : isGenerating ? (
          <p className="mt-4 flex items-center gap-2 text-sm text-white/60">
            <Loader2 className="size-4 animate-spin" />
            Brand coach working…
          </p>
        ) : (
          <p className="mt-4 text-sm leading-6 text-white/70">
            {getAgentDemoIntro("brand", campaign, brandAudience)}
          </p>
        )}
      </section>

      <section className={`${PANEL_CLASS} p-5`}>
        <p className="text-xs uppercase tracking-[0.16em] text-white/40">
          Coaching prompts
        </p>
        <div className="grid gap-2 mt-4">
          {nextActions.brand.map((action) => (
            <ActionRow
              key={action}
              label={action}
              loading={false}
              onClick={() => onQuickAction(action)}
            />
          ))}
          <ActionRow
            label="Save brand profile"
            loading={busyAction === "brandsave"}
            onClick={onSaveProfile}
          />
          <ActionRow
            label="Generate brand report"
            loading={busyAction === "brandreport"}
            onClick={onReport}
          />
        </div>
      </section>
    </div>
  );
}
