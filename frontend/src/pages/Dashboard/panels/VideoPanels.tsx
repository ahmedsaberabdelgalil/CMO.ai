import { Loader2 } from "lucide-react";
import type { VideoAgentResponse } from "../../../types/api";
import { PANEL_CLASS } from "../constants";
import { ActionRow } from "../components/ActionRow";
import { VideoAgentResultBody } from "../components/VideoAgentResultBody";

export function VideoPanels({
  busyAction,
  lastResult,
  onScript,
  onStoryboard,
  onCreatorBrief,
}: {
  busyAction: string | null;
  lastResult: VideoAgentResponse | null;
  onScript: () => void;
  onStoryboard: () => void;
  onCreatorBrief: () => void;
}) {
  const isGenerating =
    busyAction === "vscript" ||
    busyAction === "vstoryboard" ||
    busyAction === "vbrief" ||
    busyAction === "videochat";

  return (
    <div className="grid gap-5 2xl:grid-cols-[minmax(0,1fr)_320px]">
      <section className={`${PANEL_CLASS} p-5`}>
        <h2 className="text-2xl font-semibold">Video Generation</h2>
        <p className="mt-2 text-sm text-white/50">
          Create scripts, storyboards, and creator-ready briefs.
        </p>

        {isGenerating ? (
          <p className="mt-4 flex items-center gap-2 text-sm text-white/60">
            <Loader2 className="size-4 animate-spin" />
            Generating video plan and optional Runway render…
          </p>
        ) : lastResult ? (
          <div className="mt-4 max-h-[32rem] overflow-y-auto">
            <VideoAgentResultBody result={lastResult} />
          </div>
        ) : (
          <p className="mt-3 text-sm text-white/70">
            Build short-form scripts, storyboards, and creator briefs for this
            campaign using the video agent.
          </p>
        )}
      </section>

      <section className={`${PANEL_CLASS} p-5`}>
        <p className="text-xs uppercase tracking-[0.16em] text-white/40">
          Current focus
        </p>
        <div className="mt-4 grid gap-2">
          <ActionRow
            label="Write short video script"
            loading={busyAction === "vscript"}
            onClick={onScript}
          />
          <ActionRow
            label="Create storyboard"
            loading={busyAction === "vstoryboard"}
            onClick={onStoryboard}
          />
          <ActionRow
            label="Plan creator brief"
            loading={busyAction === "vbrief"}
            onClick={onCreatorBrief}
          />
        </div>
      </section>
    </div>
  );
}
