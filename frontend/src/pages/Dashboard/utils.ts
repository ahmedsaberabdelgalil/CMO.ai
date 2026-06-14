import type {
  BrandOut,
  CampaignOut,
  CampaignStatusApi,
  ImageAgentResponse,
  TextAgentResponse,
} from "../../types/api";
import type { AgentId, AgentSuggestion } from "./types";

export function buildBrandPrompts(
  campaign: CampaignOut | null,
  brand: BrandOut | null,
): string[] {
  const brandName = brand?.brand_name?.trim() || "this brand";
  const audience = brand?.target_audience?.trim() || "the core audience";
  const industry = brand?.industry?.trim() || "the market";
  const campaignName = campaign?.name?.trim() || "this campaign";
  const hasProfile = Boolean(
    brand?.value_proposition?.trim() || brand?.positioning?.trim(),
  );

  if (!hasProfile) {
    return [
      `What does ${brandName} do and who is it for?`,
      `Help me define the value proposition for ${brandName}.`,
      `What tone of voice fits ${brandName} in ${industry}?`,
      `Who exactly is the target audience for ${brandName}?`,
    ];
  }

  return [
    `Refine the positioning for ${brandName} into one sentence.`,
    `Create a brand voice guide for ${audience}.`,
    `Write 3 key brand messages for ${brandName} in ${industry}.`,
    `List the objections ${audience} have before buying.`,
    `Align ${brandName}'s message with ${campaignName}.`,
  ];
}

export function buildAgentSuggestions(
  agentId: AgentId,
  campaign: CampaignOut | null,
  brand: BrandOut | null,
): AgentSuggestion[] {
  const campaignName = campaign?.name?.trim() || "this campaign";
  const brandName = brand?.brand_name?.trim() || "this brand";
  const audience = brand?.target_audience?.trim() || "the core audience";
  const industry = brand?.industry?.trim() || "the market";
  const tone = brand?.tone_of_voice?.trim() || "clear and proof-led";
  const value =
    brand?.value_proposition?.trim() || "a concrete business outcome";
  const positioning =
    brand?.positioning?.trim() || "a practical, differentiated promise";

  if (agentId === "orchestrator") {
    return [
      {
        title: "Launch angle",
        description: `Align ${campaignName} around ${value}.`,
        action: "Create a 7-day launch plan",
      },
      {
        title: "Message fit",
        description: `Check whether ${brandName} is speaking clearly to ${audience}.`,
        action: "Summarize campaign readiness",
      },
      {
        title: "Agent sync",
        description: `Surface blockers before creative work spreads across ${industry}.`,
        action: "Ask every agent for blockers",
      },
    ];
  }

  if (agentId === "brand") {
    return [
      {
        title: "Promise",
        description: `Sharpen ${positioning} into one sentence the team can reuse.`,
        action: "Refine positioning",
      },
      {
        title: "Tone guide",
        description: `Turn "${tone}" into a repeatable voice for ${audience}.`,
        action: "Create a voice guide",
      },
      {
        title: "Objections",
        description: `List the real hesitations ${audience} may have before buying.`,
        action: "Write audience objections",
      },
    ];
  }

  if (agentId === "market") {
    return [
      {
        title: "Planner draft",
        description: `Turn ${brandName} into a weekly plan for ${audience}.`,
        action: "Generate marketing strategy",
      },
      {
        title: "Content pillars",
        description: `Review whether the content mix matches ${industry} and ${value}.`,
        action: "Review content pillars",
      },
      {
        title: "Posting cadence",
        description: `Map the weekly schedule before creative production starts.`,
        action: "Plan posting schedule",
      },
    ];
  }

  if (agentId === "calendar") {
    return [
      {
        title: "Cadence",
        description: `Spread ${campaignName} across awareness, proof, and CTA moments.`,
        action: "Generate next 14 days",
      },
      {
        title: "Channel mix",
        description: `Balance the content plan for ${industry} without repeating one angle.`,
        action: "Balance channels",
      },
      {
        title: "Gap check",
        description: `Find missing trust-building beats before the hardest ask.`,
        action: "Find calendar gaps",
      },
    ];
  }

  if (agentId === "text") {
    return [
      {
        title: "LinkedIn angle",
        description: `Write a LinkedIn post for ${brandName} that speaks to ${audience} using a ${tone} tone.`,
        action: `Write a LinkedIn post for ${campaignName} focused on ${value}.`,
      },
      {
        title: "Email sequence",
        description: `Turn ${campaignName} into a short nurture sequence with one strong CTA.`,
        action: `Draft a 3-email sequence for ${campaignName} that proves ${value}.`,
      },
      {
        title: "Ad hooks",
        description: `Create sharper first-line hooks based on ${positioning}.`,
        action: `Create ad hooks for ${campaignName} aimed at ${audience}.`,
      },
    ];
  }

  if (agentId === "image") {
    return [
      {
        title: "Hero visual",
        description: `Build a prompt that makes ${brandName} recognizable in one frame.`,
        action: "Create image prompts",
      },
      {
        title: "Asset brief",
        description: `Prepare reusable asset directions around ${value}.`,
        action: "Draft asset briefs",
      },
      {
        title: "Consistency",
        description: `Keep every visual anchored to ${tone} and ${positioning}.`,
        action: "Review visual consistency",
      },
    ];
  }

  if (agentId === "video") {
    return [
      {
        title: "Opening hook",
        description: `Script a short that turns ${value} into a strong first three seconds.`,
        action: "Write short video script",
      },
      {
        title: "Storyboard",
        description: `Map the proof arc for ${campaignName} in a quick sequence.`,
        action: "Create storyboard",
      },
      {
        title: "Creator brief",
        description: `Explain the audience, promise, and CTA in a way a creator can shoot fast.`,
        action: "Plan creator brief",
      },
    ];
  }

  return [
    {
      title: "Performance summary",
      description: `Check whether ${campaignName} is turning attention into clicks.`,
      action: "Summarize performance",
    },
    {
      title: "Funnel weakness",
      description: `Spot where buyers in ${audience} lose confidence before converting.`,
      action: "Find weak funnel step",
    },
    {
      title: "Budget move",
      description: `Recommend where to reallocate spend for ${brandName}.`,
      action: "Suggest budget shift",
    },
  ];
}

export function mapCampaignStatusToStage(status: CampaignStatusApi): string {
  if (status === "Draft") return "Planning";
  if (status === "In Progress") return "Launch planning";
  if (status === "Completed") return "Completed";
  return status;
}

export function formatLaunchDate(iso: string | null | undefined): string {
  if (!iso) return "Not set";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "Not set";
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

export function launchWindowDaysFromStart(
  startDate: string | null | undefined,
): string {
  if (!startDate) return "--";
  const end = new Date(startDate);
  const start = new Date();
  const ms = end.getTime() - start.getTime();
  const days = Math.ceil(ms / (1000 * 60 * 60 * 24));
  return `${days}d`;
}

export function buildAgentDemoResponse(
  agentId: AgentId,
  action: string,
  campaign: CampaignOut | null,
  brandAudience: string | null,
): string {
  const name = campaign?.name?.trim() || "the selected campaign";
  const launch = formatLaunchDate(campaign?.start_date);
  const description =
    campaign?.description?.trim() ||
    "No campaign description has been added yet.";
  const audience = brandAudience?.trim() || "the campaign audience";

  if (agentId === "orchestrator") {
    if (action.toLowerCase().includes("blocker")) {
      return [
        `Campaign: ${name}`,
        "",
        "Agent check-in:",
        "- Brand Coaching: lock one clear promise before copy and visuals branch out.",
        "- Market Calendar: reserve launch week for one theme instead of scattered topics.",
        "- Text Generation: create the first ad hooks, email opener, and LinkedIn post.",
        "- Image Generation: approve one visual rule set before making more assets.",
        "- Video Generation: turn the main promise into one 30-second proof script.",
        "- Performance Analytics: choose the primary KPI before launch.",
        "",
        "Next move: run Brand Coaching, then send the output to Text Generation.",
      ].join("\n");
    }

    if (action.toLowerCase().includes("readiness")) {
      return [
        `Campaign readiness demo for ${name}: 72%`,
        "",
        "Ready:",
        "- Campaign is selected and has a working brief.",
        `- Launch date: ${launch}.`,
        `- Audience context: ${audience}.`,
        "",
        "Needs attention:",
        "- Pick one primary KPI.",
        "- Approve the core message angle.",
        "- Create a first visual direction before scheduling all content.",
      ].join("\n");
    }

    return [
      `7-day launch plan for ${name}`,
      "",
      "Day 1: sharpen positioning and audience objections.",
      "Day 2: generate three copy angles and choose the strongest.",
      "Day 3: build image prompts and asset briefs from the winning angle.",
      "Day 4: write one short video script and storyboard.",
      "Day 5: schedule launch-week content across the strongest channels.",
      "Day 6: QA creative consistency and landing-page message match.",
      "Day 7: launch, then check reach, clicks, and conversion signal.",
    ].join("\n");
  }

  if (agentId === "brand") {
    if (action.toLowerCase().includes("voice")) {
      return [
        `Voice guide for ${name}`,
        "",
        "Tone: confident, practical, direct, and slightly aspirational.",
        "Use: proof, simple language, specific outcomes, and customer language.",
        "Avoid: vague hype, generic AI claims, and feature lists without a business result.",
        "",
        `Audience anchor: speak to ${audience}.`,
      ].join("\n");
    }

    if (action.toLowerCase().includes("objection")) {
      return [
        `Audience objections for ${name}`,
        "",
        "- Is this worth changing our current workflow?",
        "- Will this save time without lowering quality?",
        "- Can I trust the output enough to show it to customers?",
        "- How quickly can the team see proof?",
        "",
        "Response angle: show one concrete before/after result and one low-risk first step.",
      ].join("\n");
    }

    return [
      `Positioning demo for ${name}`,
      "",
      `For ${audience}, ${name} should feel like the campaign that makes the next action obvious.`,
      "",
      `Brief note: ${description}`,
      "",
      "Core promise: clearer marketing decisions, faster creative production, and a measurable launch path.",
    ].join("\n");
  }

  if (agentId === "market") {
    if (action.toLowerCase().includes("pillar")) {
      return [
        `Market planner review for ${name}`,
        "",
        "- Keep 4-5 content pillars so the team can repeat strong ideas without sounding repetitive.",
        "- Mix aspiration, education, proof, and CTA moments each week.",
        "- Use the audience language directly in hooks and headlines.",
        "",
        "Next move: approve the pillar mix, then pass the winning angles to Text and Image.",
      ].join("\n");
    }

    if (action.toLowerCase().includes("schedule")) {
      return [
        `Posting schedule guidance for ${name}`,
        "",
        "- Start the week with education or inspiration.",
        "- Put proof in the middle of the week before the strongest ask.",
        "- Reserve Friday or Saturday for offer-led content.",
        "- Keep one lighter engagement slot to learn what the audience responds to.",
      ].join("\n");
    }

    return [
      `Marketing strategy draft for ${name}`,
      "",
      `Goal: translate the campaign into a channel plan that feels specific to ${audience}.`,
      "",
      "Output:",
      "- Business information summary",
      "- Content pillars with formats and weekly frequency",
      "- Recommended posting schedule across the selected platforms",
      "- Closing note with next operational steps",
    ].join("\n");
  }

  if (agentId === "calendar") {
    return [
      `Calendar gap review for ${name}`,
      "",
      "- Add one proof post before asking for conversion.",
      "- Split launch week into awareness, education, proof, and CTA days.",
      "- Keep one flexible slot for reacting to early performance data.",
      "- Repeat the strongest message twice in different formats.",
      "",
      "Suggested next slot: a comparison post 48 hours before launch.",
    ].join("\n");
  }

  if (agentId === "image") {
    return [
      `Visual consistency review for ${name}`,
      "",
      "- Use one hero color accent across every asset.",
      "- Keep the product or offer visible in the first visual frame.",
      "- Pair one human/context image with one clean product/system image.",
      "- Reuse the same headline hierarchy on ads, posts, and thumbnails.",
      "",
      "Demo output: approve one campaign moodboard before generating variants.",
    ].join("\n");
  }

  if (agentId === "video") {
    return [
      `Storyboard demo for ${name}`,
      "",
      "0-3s: show the painful before state.",
      "4-10s: introduce the campaign promise in one sentence.",
      "11-20s: show proof, workflow, or result.",
      "21-27s: handle the biggest objection.",
      "28-30s: direct CTA tied to the launch goal.",
      "",
      "Format: vertical short, caption-first, one idea only.",
    ].join("\n");
  }

  if (agentId === "analytics") {
    if (action.toLowerCase().includes("budget")) {
      return [
        `Budget shift demo for ${name}`,
        "",
        "- Move 15% from the lowest-click channel into the strongest engagement channel.",
        "- Keep 10% unassigned for the first 48 hours after launch.",
        "- Use conversion rate, not reach, as the final scaling signal.",
        "",
        "Decision rule: scale only after clicks and conversions improve together.",
      ].join("\n");
    }

    return [
      `Weak funnel step demo for ${name}`,
      "",
      "Likely weak point: mid-funnel proof.",
      "Why: campaigns often jump from awareness to CTA before trust is built.",
      "Fix: add a case-study post, objection-handling email, and proof-led short video.",
      "",
      "Metric to watch: click-through rate into conversion rate.",
    ].join("\n");
  }

  return `Demo response for ${name}: ${action}`;
}

export function getAgentDemoIntro(
  agentId: AgentId,
  campaign: CampaignOut | null,
  brandAudience: string | null,
): string {
  const name = campaign?.name?.trim() || "this campaign";
  const audience = brandAudience?.trim() || "the selected audience";

  if (agentId === "orchestrator") {
    return `I can coordinate the six agents around ${name}, summarize readiness, and turn agent outputs into the next campaign move.`;
  }
  if (agentId === "brand") {
    return `I can shape positioning, voice, and objections for ${name}, grounded in ${audience}.`;
  }
  if (agentId === "market") {
    return `I can turn ${name} into a structured marketing plan with business inputs, content pillars, and a weekly posting cadence for ${audience}.`;
  }
  if (agentId === "calendar") {
    return `I can plan launch cadence, spot calendar gaps, and balance content timing for ${name}.`;
  }
  if (agentId === "image") {
    return `I can create visual prompts, asset briefs, and consistency checks for ${name}.`;
  }
  if (agentId === "video") {
    return `I can turn ${name} into scripts, storyboards, and creator-ready briefs.`;
  }
  if (agentId === "analytics") {
    return `I can read performance signals for ${name}, explain weak funnel points, and suggest budget moves.`;
  }
  return `I can help with ${name}.`;
}

export function formatTextAgentResponse(res: TextAgentResponse): string {
  const parts: string[] = [];
  if (res.subject_line) {
    parts.push(`Subject: ${res.subject_line}`);
  }
  parts.push(res.generated_content);
  if (res.hashtags?.length) {
    parts.push(`\nHashtags: ${res.hashtags.join(" ")}`);
  }
  if (res.variations?.length) {
    parts.push("\nVariations:");
    for (const v of res.variations) {
      parts.push(`\nVariation ${v.variation_id}:\n${v.content}`);
    }
  }
  if (res.seo) {
    parts.push(
      `\nSEO title: ${res.seo.suggested_title}\nMeta: ${res.seo.meta_description}\nKeywords: ${res.seo.keywords.join(", ")}`,
    );
  }
  if (res.char_count != null) {
    parts.push(
      `\n${res.char_count} characters${res.within_limit === false ? " (over limit)" : ""}`,
    );
  }
  return parts.join("\n");
}

/** Served by FastAPI StaticFiles; proxied in Vite dev via /uploads. */
export function resolveUploadUrl(imageUrl: string): string {
  if (imageUrl.startsWith("http://") || imageUrl.startsWith("https://")) {
    return imageUrl;
  }
  return imageUrl.startsWith("/") ? imageUrl : `/${imageUrl}`;
}

export function formatImageAgentResponse(res: ImageAgentResponse): string {
  const lines = [
    `Generated ${res.images.length} image(s) in ${res.generation_time_sec}s.`,
  ];
  if (res.images[0]?.ad_copy) {
    lines.push(`Ad copy: ${res.images[0].ad_copy}`);
  }
  for (const img of res.images) {
    lines.push(
      `\n[${img.image_id}] ${img.platform} ${img.size} (${img.model_used})`,
      img.prompt_used,
      `View: ${resolveUploadUrl(img.image_url)}`,
    );
  }
  if (res.knowledge_context) {
    lines.push(`\nContext: ${res.knowledge_context.slice(0, 200)}…`);
  }
  return lines.filter(Boolean).join("\n");
}
