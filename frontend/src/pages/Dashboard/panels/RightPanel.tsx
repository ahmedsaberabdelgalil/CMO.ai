import { useMemo, useState } from "react";
import { Send } from "lucide-react";
import { Button } from "../../../components/ui/button";
import { Input } from "../../../components/ui/input";
import type { BrandOut, CampaignOut } from "../../../types/api";
import type { Agent, AgentId, ChatMessage } from "../types";
import { buildAgentSuggestions, getAgentDemoIntro } from "../utils";
import { SuggestionList } from "../components/SuggestionList";
import { TextRightAside } from "./TextRightAside";
import { ImageRightAside } from "./ImageRightAside";
import { VideoRightAside } from "./VideoRightAside";
import { CalendarRightAside } from "./CalendarRightAside";
import { AnalyticsRightAside } from "./AnalyticsRightAside";
import type { ImageAgentResponse, VideoAgentResponse } from "../../../types/api";

export function RightPanel({
  activeAgent,
  campaign,
  brand,
  brandAudience,
  nextActions,
  onDemoAction,
  onCalendar14,
  onCalendarBalance,
  onCalendarFindGaps,
  calendarChatMessages,
  calendarDraft,
  onCalendarDraftChange,
  onCalendarChatSend,
  onMarketQuickAction,
  onTextLi,
  onTextEmail,
  onTextHooks,
  textChatMessages,
  textDraft,
  onTextDraftChange,
  onTextChatSend,
  imageChatMessages,
  imageLastResult,
  imageDraft,
  onImageDraftChange,
  onImageChatSend,
  onImgGenerateVisual,
  onImgAssets,
  videoChatMessages,
  videoLastResult,
  videoDraft,
  onVideoDraftChange,
  onVideoChatSend,
  onVideoScript,
  onVideoStoryboard,
  onVideoBrief,
  busyAction,
}: {
  activeAgent: Agent;
  campaign: CampaignOut | null;
  brand: BrandOut | null;
  brandAudience: string | null;
  nextActions: string[];
  onDemoAction: (agentId: AgentId, action: string) => void;
  onCalendar14: () => void;
  onCalendarBalance: () => void;
  onCalendarFindGaps: () => void;
  calendarChatMessages: ChatMessage[];
  calendarDraft: string;
  onCalendarDraftChange: (v: string) => void;
  onCalendarChatSend: (message?: string) => void;
  onMarketQuickAction: (message: string) => void;
  onTextLi: () => void;
  onTextEmail: () => void;
  onTextHooks: () => void;
  textChatMessages: ChatMessage[];
  textDraft: string;
  onTextDraftChange: (v: string) => void;
  onTextChatSend: (message?: string) => void;
  imageChatMessages: ChatMessage[];
  imageLastResult: ImageAgentResponse | null;
  imageDraft: string;
  onImageDraftChange: (v: string) => void;
  onImageChatSend: (message?: string) => void;
  onImgGenerateVisual: () => void;
  onImgAssets: () => void;
  videoChatMessages: ChatMessage[];
  videoLastResult: VideoAgentResponse | null;
  videoDraft: string;
  onVideoDraftChange: (v: string) => void;
  onVideoChatSend: (message?: string) => void;
  onVideoScript: () => void;
  onVideoStoryboard: () => void;
  onVideoBrief: () => void;
  busyAction: string | null;
}) {
  const Icon = activeAgent.icon;
  const [demoDraft, setDemoDraft] = useState("");
  const suggestions = useMemo(
    () => buildAgentSuggestions(activeAgent.id, campaign, brand),
    [activeAgent.id, brand, campaign],
  );

  const sendDemoRequest = (fallbackAction: string) => {
    const action = demoDraft.trim() || fallbackAction;
    onDemoAction(activeAgent.id, action);
    setDemoDraft("");
  };

  const runSuggestion = (action: string) => {
    if (activeAgent.id === "text") {
      onTextChatSend(action);
      return;
    }
    if (activeAgent.id === "calendar") {
      if (action === "Generate next 14 days") {
        void onCalendar14();
        return;
      }
      if (action === "Balance channels") {
        void onCalendarBalance();
        return;
      }
      if (action === "Find calendar gaps") {
        onCalendarFindGaps();
        return;
      }
      return;
    }
    if (activeAgent.id === "image") {
      if (action === "Create image prompts") {
        void onImgGenerateVisual();
        return;
      }
      if (action === "Draft asset briefs") {
        void onImgAssets();
        return;
      }
      onImageChatSend(action);
      return;
    }
    if (activeAgent.id === "video") {
      if (action === "Write short video script") {
        onVideoScript();
        return;
      }
      if (action === "Create storyboard") {
        onVideoStoryboard();
        return;
      }
      if (action === "Plan creator brief") {
        onVideoBrief();
        return;
      }
      onVideoChatSend(action);
      return;
    }
    if (activeAgent.id === "analytics") {
      onDemoAction("analytics", action);
      return;
    }
    if (activeAgent.id === "market") {
      onMarketQuickAction(action);
      return;
    }
    if (activeAgent.id === "brand") {
      onDemoAction("brand", action);
      return;
    }
    onDemoAction("orchestrator", action);
  };

  if (activeAgent.id === "orchestrator") {
    return (
      <aside className="border-t border-white/10 bg-[#0D1018] xl:border-l xl:border-t-0">
        <div className="flex h-full min-h-[560px] flex-col">
          <div className="px-4 py-4 border-b border-white/10">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center rounded-md size-10 bg-white/10">
                <Icon className={`size-5 ${activeAgent.accent}`} />
              </div>
              <div className="min-w-0">
                <p className="text-sm font-semibold truncate">Orchestrator</p>
                <p className="text-xs truncate text-white/45">
                  {campaign?.name ?? "-"}
                </p>
              </div>
            </div>
          </div>
          <div className="flex-1 px-4 py-4 space-y-3 overflow-y-auto">
            <div className="rounded-md bg-white/[0.07] px-3 py-2 text-sm leading-6 text-white/80">
              {getAgentDemoIntro("orchestrator", campaign, brandAudience)}
            </div>
            <SuggestionList
              suggestions={suggestions}
              onSelect={runSuggestion}
            />
            {nextActions.map((action) => (
              <button
                key={action}
                type="button"
                onClick={() => onDemoAction("orchestrator", action)}
                className="w-full px-3 py-2 text-xs text-left transition border rounded-md border-white/10 text-white/70 hover:border-neonBlue/60 hover:text-white"
              >
                {action}
              </button>
            ))}
          </div>
          <form
            className="flex gap-2 p-4 border-t border-white/10"
            onSubmit={(e) => {
              e.preventDefault();
              sendDemoRequest("Summarize campaign readiness");
            }}
          >
            <Input
              value={demoDraft}
              onChange={(e) => setDemoDraft(e.target.value)}
              placeholder="Ask Orchestrator"
              className="bg-white h-11 border-white/10 text-cosmic placeholder:text-slate-500"
            />
            <Button
              type="submit"
              size="icon"
              disabled={!demoDraft.trim()}
              className="text-white h-11 w-11 bg-neonPink hover:bg-neonPink/90"
            >
              <Send className="size-4" />
            </Button>
          </form>
        </div>
      </aside>
    );
  }

  if (activeAgent.id === "brand") {
    return (
      <aside className="border-t border-white/10 bg-[#0D1018] xl:border-l xl:border-t-0">
        <div className="flex h-full min-h-[560px] flex-col">
          <div className="px-4 py-4 border-b border-white/10">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center rounded-md size-10 bg-white/10">
                <Icon className={`size-5 ${activeAgent.accent}`} />
              </div>
              <div className="min-w-0">
                <p className="text-sm font-semibold truncate">
                  {activeAgent.name}
                </p>
                <p className="text-xs truncate text-white/45">
                  {campaign?.name ?? "-"}
                </p>
              </div>
            </div>
          </div>
          <div className="flex-1 px-4 py-4 space-y-3 overflow-y-auto">
            <p className="text-sm text-white/70">
              {getAgentDemoIntro("brand", campaign, brandAudience)}
            </p>
            <SuggestionList
              suggestions={suggestions}
              onSelect={runSuggestion}
            />
            {nextActions.map((action) => (
              <button
                key={action}
                type="button"
                onClick={() => onDemoAction("brand", action)}
                className="w-full px-3 py-2 text-xs text-left transition border rounded-md border-white/10 text-white/70 hover:border-neonBlue/60 hover:text-white"
              >
                {action}
              </button>
            ))}
          </div>
          <form
            className="flex gap-2 p-4 border-t border-white/10"
            onSubmit={(e) => {
              e.preventDefault();
              sendDemoRequest("Refine positioning");
            }}
          >
            <Input
              value={demoDraft}
              onChange={(e) => setDemoDraft(e.target.value)}
              placeholder="Ask Brand"
              className="bg-white h-11 border-white/10 text-cosmic placeholder:text-slate-500"
            />
            <Button
              type="submit"
              size="icon"
              disabled={!demoDraft.trim()}
              className="text-white h-11 w-11 bg-neonPink hover:bg-neonPink/90"
            >
              <Send className="size-4" />
            </Button>
          </form>
        </div>
      </aside>
    );
  }

  if (activeAgent.id === "analytics") {
    return (
      <AnalyticsRightAside
        activeAgent={activeAgent}
        campaignName={campaign?.name ?? "-"}
        suggestions={suggestions}
        onDemoAction={onDemoAction}
      />
    );
  }

  if (activeAgent.id === "image") {
    return (
      <ImageRightAside
        activeAgent={activeAgent}
        campaignName={campaign?.name ?? "-"}
        messages={imageChatMessages}
        lastResult={imageLastResult}
        draft={imageDraft}
        onDraftChange={onImageDraftChange}
        onSend={onImageChatSend}
        suggestions={suggestions}
        onGenerateVisual={onImgGenerateVisual}
        onListAssets={onImgAssets}
        busyAction={busyAction}
      />
    );
  }

  if (activeAgent.id === "calendar") {
    return (
      <CalendarRightAside
        activeAgent={activeAgent}
        campaignName={campaign?.name ?? "-"}
        messages={calendarChatMessages}
        draft={calendarDraft}
        onDraftChange={onCalendarDraftChange}
        onSend={onCalendarChatSend}
        suggestions={suggestions}
        onGenerate14={onCalendar14}
        onBalance={onCalendarBalance}
        onFindGaps={onCalendarFindGaps}
        busyAction={busyAction}
      />
    );
  }

  if (activeAgent.id === "video") {
    return (
      <VideoRightAside
        activeAgent={activeAgent}
        campaignName={campaign?.name ?? "-"}
        messages={videoChatMessages}
        lastResult={videoLastResult}
        draft={videoDraft}
        onDraftChange={onVideoDraftChange}
        onSend={onVideoChatSend}
        suggestions={suggestions}
        onScript={onVideoScript}
        onStoryboard={onVideoStoryboard}
        onCreatorBrief={onVideoBrief}
        busyAction={busyAction}
      />
    );
  }

  if (activeAgent.id === "text") {
    return (
      <TextRightAside
        activeAgent={activeAgent}
        campaignName={campaign?.name ?? "-"}
        messages={textChatMessages}
        draft={textDraft}
        onDraftChange={onTextDraftChange}
        onSend={onTextChatSend}
        nextActions={nextActions}
        suggestions={suggestions}
        onTextLi={onTextLi}
        onTextEmail={onTextEmail}
        onTextHooks={onTextHooks}
        busyAction={busyAction}
      />
    );
  }

  const assistantIntro = getAgentDemoIntro(
    activeAgent.id,
    campaign,
    brandAudience,
  );

  const runQuick = (label: string) => {
    if (activeAgent.id === "video") {
      if (label === "Write short video script") onVideoScript();
      if (label === "Create storyboard") onVideoStoryboard();
      if (label === "Plan creator brief") onVideoBrief();
    }
  };

  const isBusy = (label: string) => {
    if (label === "Generate marketing strategy") {
      return busyAction === "marketgen" || busyAction === "marketchat";
    }
    if (label === "Generate next 14 days") return busyAction === "cal14";
    if (label === "Balance channels") return busyAction === "calbalance";
    if (label === "Find calendar gaps") return busyAction === "calgaps";
    if (label === "Write LinkedIn posts") return busyAction === "li";
    if (label === "Draft email sequence") return busyAction === "email";
    if (label === "Create ad hooks") return busyAction === "hooks";
    if (label === "Create image prompts") return busyAction === "imggen";
    if (label === "Draft asset briefs") return busyAction === "assets";
    if (label === "Write short video script") return busyAction === "vscript";
    if (label === "Create storyboard") return busyAction === "vstoryboard";
    if (label === "Plan creator brief") return busyAction === "vbrief";
    return false;
  };

  return (
    <aside className="border-t border-white/10 bg-[#0D1018] xl:border-l xl:border-t-0">
      <div className="flex h-full min-h-[560px] flex-col">
        <div className="px-4 py-4 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center rounded-md size-10 bg-white/10">
              <Icon className={`size-5 ${activeAgent.accent}`} />
            </div>
            <div className="min-w-0">
              <p className="text-sm font-semibold truncate">
                {activeAgent.name}
              </p>
              <p className="text-xs truncate text-white/45">
                {campaign?.name ?? "-"}
              </p>
            </div>
          </div>
        </div>

        <div className="flex-1 px-4 py-4 space-y-3 overflow-y-auto">
          <div className="rounded-md bg-white/[0.07] px-3 py-2 text-sm leading-6 text-white/80">
            {assistantIntro}
          </div>
          <SuggestionList suggestions={suggestions} onSelect={runSuggestion} />
        </div>

        <div className="p-4 border-t border-white/10">
          <div className="grid gap-2 mb-3">
            {nextActions.map((action) => {
              if (
                activeAgent.id === "image" &&
                action === "Review visual consistency"
              ) {
                return (
                  <button
                    key={action}
                    type="button"
                    onClick={() => runQuick(action)}
                    className="px-3 py-2 text-xs text-left transition border rounded-md border-white/10 text-white/70 hover:border-neonBlue/60 hover:text-white"
                  >
                    {action}
                  </button>
                );
              }
              if (
                activeAgent.id === "video" &&
                action === "Create storyboard"
              ) {
                return (
                  <button
                    key={action}
                    type="button"
                    onClick={() => runQuick(action)}
                    className="px-3 py-2 text-xs text-left transition border rounded-md border-white/10 text-white/70 hover:border-neonBlue/60 hover:text-white"
                  >
                    {action}
                  </button>
                );
              }
              return (
                <button
                  key={action}
                  type="button"
                  disabled={isBusy(action)}
                  onClick={() => runQuick(action)}
                  className="px-3 py-2 text-xs text-left transition border rounded-md border-white/10 text-white/70 hover:border-neonBlue/60 hover:text-white disabled:opacity-50"
                >
                  {isBusy(action) ? "Loading..." : action}
                </button>
              );
            })}
          </div>

          <form
            className="flex gap-2"
            onSubmit={(e) => {
              e.preventDefault();
              sendDemoRequest(nextActions[0] ?? `Ask ${activeAgent.shortName}`);
            }}
          >
            <Input
              value={demoDraft}
              onChange={(e) => setDemoDraft(e.target.value)}
              placeholder={`Ask ${activeAgent.shortName}`}
              className="bg-white h-11 border-white/10 text-cosmic placeholder:text-slate-500"
            />
            <Button
              type="submit"
              size="icon"
              disabled={!demoDraft.trim()}
              className="text-white h-11 w-11 bg-neonPink hover:bg-neonPink/90"
            >
              <Send className="size-4" />
            </Button>
          </form>
        </div>
      </div>
    </aside>
  );
}
