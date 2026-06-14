import { useEffect, useMemo, useState } from "react";
import { CheckCircle2, Loader2, Sparkles } from "lucide-react";
import { Button } from "../../../components/ui/button";
import { Input } from "../../../components/ui/input";
import { Textarea } from "../../../components/ui/textarea";
import type { BrandOut, CampaignOut } from "../../../types/api";
import { PANEL_CLASS, SUBPANEL_CLASS } from "../constants";

export type BrandProfileForm = {
  brandName: string;
  industry: string;
  targetAudience: string;
  valueProposition: string;
  toneOfVoice: string;
  positioning: string;
};

const TONE_OPTIONS = [
  "Professional",
  "Friendly",
  "Bold",
  "Playful",
  "Luxury",
  "Inspirational",
];

export function BrandPanels({
  campaign,
  brand,
  brandAudience,
  busyAction,
  suggestions,
  onSaveProfile,
  onPromptSelect,
}: {
  campaign: CampaignOut;
  brand: BrandOut | null;
  brandAudience: string | null;
  busyAction: string | null;
  suggestions: string[];
  onSaveProfile: (form: BrandProfileForm) => void;
  onPromptSelect: (prompt: string) => void;
}) {
  const initialForm = useMemo<BrandProfileForm>(
    () => ({
      brandName: brand?.brand_name?.trim() || "",
      industry: brand?.industry?.trim() || "",
      targetAudience: brandAudience?.trim() || brand?.target_audience?.trim() || "",
      valueProposition: brand?.value_proposition?.trim() || "",
      toneOfVoice: brand?.tone_of_voice?.trim() || "Professional",
      positioning: brand?.positioning?.trim() || "",
    }),
    [brand, brandAudience],
  );

  const [form, setForm] = useState<BrandProfileForm>(initialForm);
  const isSaving = busyAction === "brandprofile";

  useEffect(() => {
    setForm(initialForm);
  }, [initialForm]);

  const set = (key: keyof BrandProfileForm, value: string) =>
    setForm((current) => ({ ...current, [key]: value }));

  return (
    <div className="space-y-5">
      <section className="grid gap-5 2xl:grid-cols-[minmax(0,1.2fr)_320px]">
        <div className={`${PANEL_CLASS} p-5`}>
          <div className="flex items-center gap-2 text-neonPurple">
            <Sparkles className="size-5" />
            <h2 className="text-2xl font-semibold">Brand Coaching</h2>
          </div>
          <p className="mt-3 text-sm leading-6 text-white/70">
            Answer these questions about your business. Save them so every other
            agent knows your brand — then pick a prompt option to go deeper.
          </p>

          <div className="grid gap-4 mt-5 lg:grid-cols-2">
            <label className="space-y-2">
              <span className="text-sm text-white/70">Brand name</span>
              <Input
                value={form.brandName}
                onChange={(e) => set("brandName", e.target.value)}
                placeholder="e.g. Veltrix"
                className="bg-white border-white/10 text-cosmic"
              />
            </label>

            <label className="space-y-2">
              <span className="text-sm text-white/70">Industry</span>
              <Input
                value={form.industry}
                onChange={(e) => set("industry", e.target.value)}
                placeholder="e.g. SaaS analytics"
                className="bg-white border-white/10 text-cosmic"
              />
            </label>

            <label className="space-y-2 lg:col-span-2">
              <span className="text-sm text-white/70">
                Who is your target audience?
              </span>
              <Input
                value={form.targetAudience}
                onChange={(e) => set("targetAudience", e.target.value)}
                placeholder="e.g. startup founders and creators"
                className="bg-white border-white/10 text-cosmic"
              />
            </label>

            <label className="space-y-2 lg:col-span-2">
              <span className="text-sm text-white/70">
                What is your unique value proposition?
              </span>
              <Textarea
                rows={2}
                value={form.valueProposition}
                onChange={(e) => set("valueProposition", e.target.value)}
                placeholder="What makes you different / the outcome you deliver"
                className="bg-white resize-none border-white/10 text-cosmic"
              />
            </label>

            <label className="space-y-2">
              <span className="text-sm text-white/70">Brand voice / tone</span>
              <select
                value={form.toneOfVoice}
                onChange={(e) => set("toneOfVoice", e.target.value)}
                className="w-full px-3 text-sm border rounded-md outline-none h-11 border-white/10 bg-white text-cosmic"
              >
                {TONE_OPTIONS.map((tone) => (
                  <option key={tone} value={tone}>
                    {tone}
                  </option>
                ))}
              </select>
            </label>

            <label className="space-y-2">
              <span className="text-sm text-white/70">
                Positioning (one sentence)
              </span>
              <Input
                value={form.positioning}
                onChange={(e) => set("positioning", e.target.value)}
                placeholder="The promise in one line"
                className="bg-white border-white/10 text-cosmic"
              />
            </label>
          </div>

          <div className="flex flex-wrap items-center gap-3 mt-5">
            <Button
              type="button"
              disabled={isSaving || !form.brandName.trim()}
              className="text-white bg-neonPurple hover:bg-neonPurple/90"
              onClick={() => onSaveProfile(form)}
            >
              {isSaving ? (
                <span className="flex items-center gap-2">
                  <Loader2 className="size-4 animate-spin" />
                  Saving…
                </span>
              ) : (
                "Save brand profile"
              )}
            </Button>
            {suggestions.length && !isSaving ? (
              <span className="inline-flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-xs font-medium text-emerald-200">
                <CheckCircle2 className="size-4" />
                Profile saved — agents now know your brand
              </span>
            ) : null}
          </div>
        </div>

        <section className={`${PANEL_CLASS} p-5`}>
          <p className="text-xs uppercase tracking-[0.16em] text-white/40">
            Prompt options
          </p>
          {suggestions.length ? (
            <div className="grid gap-2 mt-4">
              {suggestions.map((prompt) => (
                <button
                  key={prompt}
                  type="button"
                  onClick={() => onPromptSelect(prompt)}
                  className={`${SUBPANEL_CLASS} px-3 py-2 text-left text-sm text-white/85 transition hover:border-neonPurple/60 hover:text-white`}
                >
                  {prompt}
                </button>
              ))}
            </div>
          ) : (
            <p className="mt-3 text-sm leading-6 text-white/60">
              Save your brand profile to unlock tailored prompt options. You can
              also chat with the brand coach in the panel on the right anytime.
            </p>
          )}
          <div className={`mt-4 p-4 ${SUBPANEL_CLASS}`}>
            <p className="text-xs uppercase tracking-[0.16em] text-white/40">
              Why this matters
            </p>
            <p className="mt-2 text-sm leading-6 text-white/75">
              The saved brand profile feeds the content, image, video, calendar,
              analytics, and orchestrator agents for {campaign.name}.
            </p>
          </div>
        </section>
      </section>
    </div>
  );
}
