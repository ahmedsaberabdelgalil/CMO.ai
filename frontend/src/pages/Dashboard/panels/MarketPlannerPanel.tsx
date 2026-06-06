import { useEffect, useMemo, useState } from "react";
import { CheckCircle2, Loader2, Sparkles } from "lucide-react";
import { Button } from "../../../components/ui/button";
import { Input } from "../../../components/ui/input";
import { Textarea } from "../../../components/ui/textarea";
import type { BrandOut, CampaignOut, MarketingAgentResponse } from "../../../types/api";
import { PANEL_CLASS, SUBPANEL_CLASS } from "../constants";
import { BriefStat } from "../components/CampaignBrief";
import { MarketingAgentResultBody } from "../components/MarketingAgentResultBody";

export type PlannerFormState = {
  brandName: string;
  targetAudience: string;
  industry: string;
  budget: number;
  productService: string;
  mainGoal: string;
  platforms: string[];
};

const PLATFORM_OPTIONS = [
  "Instagram",
  "TikTok",
  "Facebook",
  "LinkedIn",
  "YouTube",
];

const GOAL_OPTIONS = [
  "Brand Awareness",
  "Increase Sales",
  "Lead Generation",
  "Grow Awareness",
  "Build Community",
];

export function MarketPlannerPanel({
  campaign,
  brand,
  brandAudience,
  busyAction,
  lastResult,
  onGenerate,
  onOpenCalendar,
}: {
  campaign: CampaignOut;
  brand: BrandOut | null;
  brandAudience: string | null;
  busyAction: string | null;
  lastResult: MarketingAgentResponse | null;
  onGenerate: (form: PlannerFormState, message: string) => void;
  onOpenCalendar: () => void;
}) {
  const initialForm = useMemo<PlannerFormState>(
    () => ({
      brandName: brand?.brand_name?.trim() || "Brand",
      targetAudience: brandAudience?.trim() || "General audience",
      industry: brand?.industry?.trim() || "General",
      budget: 1000,
      productService:
        campaign.description?.trim() || campaign.name,
      mainGoal: "Brand Awareness",
      platforms: ["Instagram", "TikTok"],
    }),
    [brand, brandAudience, campaign.description, campaign.name],
  );

  const [form, setForm] = useState<PlannerFormState>(initialForm);
  const isGenerating = busyAction === "marketgen" || busyAction === "marketchat";

  useEffect(() => {
    setForm(initialForm);
  }, [initialForm]);

  const togglePlatform = (platform: string) => {
    setForm((current) => {
      const exists = current.platforms.includes(platform);
      const platforms = exists
        ? current.platforms.filter((item) => item !== platform)
        : [...current.platforms, platform];

      return {
        ...current,
        platforms: platforms.length ? platforms : [platform],
      };
    });
  };

  const primaryPlatform = form.platforms[0] ?? "Instagram";
  const secondaryPlatform = form.platforms[1] ?? form.platforms[0] ?? "TikTok";

  return (
    <div className="space-y-5">
      <section className="grid gap-5 2xl:grid-cols-[minmax(0,1.2fr)_320px]">
        <div className={`${PANEL_CLASS} p-5`}>
          <div className="flex items-center gap-2 text-neonBlue">
            <Sparkles className="size-5" />
            <h2 className="text-2xl font-semibold">Market Planner</h2>
          </div>
          <p className="mt-3 text-sm leading-6 text-white/70">
            Generate a data-driven marketing strategy with budget allocation,
            financial projections, and a full CMO plan via the marketing agent.
          </p>
          <p className="mt-1 text-xs text-white/45">
            Powered by POST /api/v1/agents/marketing/generate
          </p>

          <div className="mt-5 grid gap-4 lg:grid-cols-2">
            <label className="space-y-2">
              <span className="text-sm text-white/70">Brand Name</span>
              <Input
                value={form.brandName}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    brandName: event.target.value,
                  }))
                }
                className="border-white/10 bg-white text-cosmic"
              />
            </label>

            <label className="space-y-2">
              <span className="text-sm text-white/70">Target Audience</span>
              <Input
                value={form.targetAudience}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    targetAudience: event.target.value,
                  }))
                }
                className="border-white/10 bg-white text-cosmic"
              />
            </label>

            <label className="space-y-2">
              <span className="text-sm text-white/70">Industry</span>
              <Input
                value={form.industry}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    industry: event.target.value,
                  }))
                }
                className="border-white/10 bg-white text-cosmic"
              />
            </label>

            <label className="space-y-2">
              <span className="text-sm text-white/70">Marketing Budget ($)</span>
              <div className="flex items-center gap-2">
                <Button
                  type="button"
                  variant="outline"
                  className="h-11 border-white/20 bg-white/5 px-3 text-white hover:bg-white/10"
                  onClick={() =>
                    setForm((current) => ({
                      ...current,
                      budget: Math.max(0, current.budget - 100),
                    }))
                  }
                >
                  -
                </Button>
                <Input
                  type="number"
                  min={0}
                  step={100}
                  value={form.budget}
                  onChange={(event) =>
                    setForm((current) => ({
                      ...current,
                      budget: Number(event.target.value) || 0,
                    }))
                  }
                  className="border-white/10 bg-white text-cosmic"
                />
                <Button
                  type="button"
                  variant="outline"
                  className="h-11 border-white/20 bg-white/5 px-3 text-white hover:bg-white/10"
                  onClick={() =>
                    setForm((current) => ({
                      ...current,
                      budget: current.budget + 100,
                    }))
                  }
                >
                  +
                </Button>
              </div>
            </label>

            <label className="space-y-2 lg:col-span-2">
              <span className="text-sm text-white/70">Product / Service</span>
              <Textarea
                rows={3}
                value={form.productService}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    productService: event.target.value,
                  }))
                }
                className="resize-none border-white/10 bg-white text-cosmic"
              />
            </label>

            <label className="space-y-2">
              <span className="text-sm text-white/70">Main Goal</span>
              <select
                value={form.mainGoal}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    mainGoal: event.target.value,
                  }))
                }
                className="h-11 w-full rounded-md border border-white/10 bg-white px-3 text-sm text-cosmic outline-none"
              >
                {GOAL_OPTIONS.map((goal) => (
                  <option key={goal} value={goal}>
                    {goal}
                  </option>
                ))}
              </select>
            </label>

            <div className="space-y-2">
              <span className="text-sm text-white/70">Marketing Platforms</span>
              <div className="flex flex-wrap gap-2">
                {PLATFORM_OPTIONS.map((platform) => {
                  const isActive = form.platforms.includes(platform);

                  return (
                    <button
                      key={platform}
                      type="button"
                      onClick={() => togglePlatform(platform)}
                      className={`rounded-full border px-3 py-2 text-sm transition ${
                        isActive
                          ? "border-neonPink/40 bg-neonPink/20 text-white"
                          : "border-white/15 bg-white/5 text-white/65 hover:bg-white/10 hover:text-white"
                      }`}
                    >
                      {platform}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          <div className="mt-5 flex flex-wrap items-center gap-3">
            <Button
              type="button"
              disabled={isGenerating}
              className="bg-neonBlue text-cosmic hover:bg-neonBlue/90"
              onClick={() =>
                onGenerate(
                  form,
                  `Generate marketing strategy for ${form.productService}`,
                )
              }
            >
              {isGenerating ? (
                <span className="flex items-center gap-2">
                  <Loader2 className="size-4 animate-spin" />
                  Generating…
                </span>
              ) : (
                "Generate Marketing Strategy"
              )}
            </Button>
            {lastResult && !isGenerating ? (
              <span className="inline-flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-xs font-medium text-emerald-200">
                <CheckCircle2 className="size-4" />
                {lastResult.calendar_ready
                  ? "Plan linked to calendar"
                  : "Live strategy from marketing agent"}
              </span>
            ) : null}
            {lastResult?.calendar_ready ? (
              <Button
                type="button"
                variant="outline"
                className="border-neonBlue/30 bg-neonBlue/10 text-white hover:bg-neonBlue/20"
                onClick={onOpenCalendar}
              >
                Open Calendar
              </Button>
            ) : null}
          </div>
          {lastResult?.calendar_ready ? (
            <p className="mt-3 text-sm text-emerald-200/90">
              {lastResult.calendar_items_created ?? 14} posts were scheduled for
              the next two weeks. Switch to Market Calendar to review them.
            </p>
          ) : campaign.strategy_id ? (
            <p className="mt-3 text-sm text-white/60">
              This campaign already has a linked strategy. Regenerating will
              refresh the plan and calendar schedule.
            </p>
          ) : null}
        </div>

        <section className={`${PANEL_CLASS} p-5`}>
          <p className="text-xs uppercase tracking-[0.16em] text-white/40">
            Planner snapshot
          </p>
          <div className="mt-4 grid gap-3">
            <BriefStat label="Primary platform" value={primaryPlatform} />
            <BriefStat label="Secondary platform" value={secondaryPlatform} />
            <BriefStat
              label="Budget"
              value={`$${form.budget.toLocaleString("en-US")}`}
            />
            <BriefStat label="Main goal" value={form.mainGoal} />
          </div>
          <div className={`mt-4 p-4 ${SUBPANEL_CLASS}`}>
            <p className="text-xs uppercase tracking-[0.16em] text-white/40">
              Planner angle
            </p>
            <p className="mt-2 text-sm leading-6 text-white/75">
              Uses Groq + rule-based budget, financial, and platform models,
              then synthesizes a full CMO strategy for your campaign.
            </p>
          </div>
        </section>
      </section>

      {isGenerating ? (
        <p className="flex items-center gap-2 text-sm text-white/60">
          <Loader2 className="size-4 animate-spin" />
          Calling marketing agent… this may take 15–30 seconds.
        </p>
      ) : null}

      {lastResult ? (
        <MarketingAgentResultBody result={lastResult} />
      ) : null}
    </div>
  );
}
