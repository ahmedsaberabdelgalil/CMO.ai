import type { LucideIcon } from "lucide-react";
import type { ContentAgentType, BrandOut, CampaignOut } from "../../types/api";

export type ChatMessage = {
  role: "user" | "assistant";
  text: string;
  images?: string[];
  videoUrl?: string;
};

export type AgentSuggestion = {
  title: string;
  description: string;
  action: string;
};

export type DashboardNotification = {
  id: string;
  title: string;
  detail: string;
  tone: "info" | "warn" | "success";
  showInBadge?: boolean;
  actionLabel?: string;
  actionType?:
    | "new-campaign"
    | "brand"
    | "calendar"
    | "text"
    | "market"
    | "image";
};

export type AgentId =
  | "orchestrator"
  | "market"
  | "brand"
  | "calendar"
  | "text"
  | "image"
  | "video"
  | "analytics";

export type Agent = {
  id: AgentId;
  name: string;
  shortName: string;
  description: string;
  icon: LucideIcon;
  accent: string;
  navSubtitle: string;
};

export type TextContentType = ContentAgentType;

export type DemoContext = {
  campaign: CampaignOut | null;
  brand: BrandOut | null;
};
