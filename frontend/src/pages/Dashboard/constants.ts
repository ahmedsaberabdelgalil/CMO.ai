import {
  BarChart3,
  CalendarDays,
  Clapperboard,
  Image,
  LayoutDashboard,
  Megaphone,
  PenLine,
  Sparkles,
} from "lucide-react";
import type { Agent, AgentId } from "./types";

export const agents: Agent[] = [
  {
    id: "orchestrator",
    name: "Orchestrator",
    shortName: "Dashboard",
    description: "Campaign command center",
    icon: LayoutDashboard,
    accent: "text-neonBlue",
    navSubtitle: "Campaign workspace",
  },
  {
    id: "market",
    name: "Market Planner",
    shortName: "Planner",
    description: "Business inputs, content pillars, posting cadence",
    icon: Megaphone,
    accent: "text-neonGreen",
    navSubtitle: "Strategy output",
  },
  {
    id: "brand",
    name: "Brand Coaching",
    shortName: "Brand",
    description: "Positioning, voice, audience fit",
    icon: Sparkles,
    accent: "text-neonPurple",
    navSubtitle: "Brand identity",
  },
  {
    id: "calendar",
    name: "Market Calendar",
    shortName: "Calendar",
    description: "Campaign timing and content cadence",
    icon: CalendarDays,
    accent: "text-neonBlue",
    navSubtitle: "Content planning",
  },
  {
    id: "text",
    name: "Text Generation",
    shortName: "Text",
    description: "Posts, ads, emails, landing copy",
    icon: PenLine,
    accent: "text-neonPink",
    navSubtitle: "Copy generation",
  },
  {
    id: "image",
    name: "Image Generation",
    shortName: "Image",
    description: "Visual briefs and campaign assets",
    icon: Image,
    accent: "text-neonYellow",
    navSubtitle: "Visual assets",
  },
  {
    id: "video",
    name: "Video Generation",
    shortName: "Video",
    description: "Scripts, storyboards, shorts",
    icon: Clapperboard,
    accent: "text-neonGreen",
    navSubtitle: "Video production",
  },
  {
    id: "analytics",
    name: "Performance Analytics",
    shortName: "Analytics",
    description: "Signals, learnings, next moves",
    icon: BarChart3,
    accent: "text-neonBlue",
    navSubtitle: "Performance data",
  },
];

export const nextActions: Record<AgentId, string[]> = {
  orchestrator: [
    "Create a 7-day launch plan",
    "Ask every agent for blockers",
    "Summarize campaign readiness",
  ],
  market: [
    "Generate marketing strategy",
    "Review content pillars",
    "Plan posting schedule",
  ],
  brand: [
    "Refine positioning",
    "Create a voice guide",
    "Write audience objections",
  ],
  calendar: ["Plan next 14 days", "Balance channels", "Find calendar gaps"],
  text: ["Write LinkedIn posts", "Draft email sequence", "Create ad hooks"],
  image: [
    "Create image prompts",
    "Draft asset briefs",
    "Review visual consistency",
  ],
  video: [
    "Write short video script",
    "Create storyboard",
    "Plan creator brief",
  ],
  analytics: [
    "Summarize performance",
    "Find weak funnel step",
    "Suggest budget shift",
  ],
};

export const PANEL_CLASS =
  "rounded-2xl border border-white/10 bg-[linear-gradient(180deg,rgba(92,46,190,0.22),rgba(14,18,36,0.96))] shadow-[0_18px_50px_rgba(10,10,30,0.35)] backdrop-blur-xl";

export const SUBPANEL_CLASS =
  "rounded-2xl border border-white/10 bg-[linear-gradient(180deg,rgba(120,70,220,0.16),rgba(13,16,30,0.92))] shadow-[0_12px_36px_rgba(7,9,20,0.3)]";
