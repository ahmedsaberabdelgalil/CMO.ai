import { Loader2 } from "lucide-react";
import type { ImageAgentResponse, ImageAgentStatus } from "../../../types/api";
import { PANEL_CLASS } from "../constants";
import { ActionRow } from "../components/ActionRow";
import { ImageAgentResultBody } from "../components/ImageAgentResultBody";

export function ImagePanels({
  agentStatus,
  busyAction,
  lastResult,
  onGenerateVisual,
  onGenerateVariations,
  onAssets,
  onReview,
}: {
  agentStatus: ImageAgentStatus | null;
  busyAction: string | null;
  lastResult: ImageAgentResponse | null;
  onGenerateVisual: () => void;
  onGenerateVariations: () => void;
  onAssets: () => void;
  onReview: () => void;
}) {
  const isGenerating =
    busyAction === "imggen" ||
    busyAction === "imgchat" ||
    busyAction === "imgvar";

  return (
    <div className="grid gap-5 2xl:grid-cols-[minmax(0,1fr)_320px]">
      <section className={`${PANEL_CLASS} p-5`}>
        <div className="flex flex-wrap items-center gap-3">
          <h2 className="text-2xl font-semibold">Image Generation</h2>
          {agentStatus ? (
            <div className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs text-white/60">
              Groq prompts · {agentStatus.image_backend} images
              {!agentStatus.image_backend_configured ? " · backend key missing" : ""}
            </div>
          ) : null}
        </div>
        <p className="mt-2 text-sm text-white/50">
          Generate campaign visuals and creative asset briefs.
        </p>

        {isGenerating ? (
          <p className="mt-4 flex items-center gap-2 text-sm text-white/60">
            <Loader2 className="size-4 animate-spin" />
            Generating images… this may take up to a minute.
          </p>
        ) : lastResult ? (
          <div className="mt-4 max-h-[32rem] overflow-y-auto">
            <ImageAgentResultBody result={lastResult} />
          </div>
        ) : (
          <p className="mt-3 text-sm text-white/70">
            Generate campaign visuals with the image agent, or list existing
            assets from your library.
          </p>
        )}
      </section>

      <section className={`${PANEL_CLASS} p-5`}>
        <p className="text-xs uppercase tracking-[0.16em] text-white/40">
          Current focus
        </p>
        <div className="mt-4 grid gap-2">
          <ActionRow
            label="Create image prompts"
            loading={busyAction === "imggen"}
            onClick={onGenerateVisual}
          />
          <ActionRow
            label="Generate 2 variations"
            loading={busyAction === "imgvar"}
            onClick={onGenerateVariations}
          />
          <ActionRow
            label="Draft asset briefs"
            loading={busyAction === "assets"}
            onClick={onAssets}
          />
          <button
            type="button"
            onClick={onReview}
            className="rounded-md border border-white/10 bg-[#0D1018] px-3 py-2 text-left text-sm text-white/80 transition hover:border-neonBlue/60"
          >
            Review visual consistency
          </button>
        </div>
      </section>
    </div>
  );
}
