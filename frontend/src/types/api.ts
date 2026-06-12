export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserOut {
  id: number;
  name: string;
  email: string;
  avatar_url: string | null;
  role: string;
  created_at: string;
}

export interface BrandOut {
  id: number;
  brand_name: string;
  logo_url: string | null;
  industry: string | null;
  tone_of_voice: string | null;
  target_audience: string | null;
  value_proposition: string | null;
  positioning: string | null;
  user_id: number;
  created_at: string;
  updated_at: string | null;
}

export interface StrategyOut {
  id: number;
  title: string;
  objectives: string | null;
  messaging_themes: string | null;
  platform_focus: string | null;
  status: string;
  brand_id: number;
  created_at: string;
  updated_at: string | null;
}

export interface MessageResponse {
  message: string;
}

/** Matches backend `CampaignStatus` serialization */
export type CampaignStatusApi = "Draft" | "In Progress" | "Completed";

export interface CampaignOut {
  id: number;
  name: string;
  description: string | null;
  start_date: string | null;
  brand_id: number;
  strategy_id: number | null;
  status: CampaignStatusApi;
  created_at: string;
  updated_at: string | null;
}

export interface CampaignCreatePayload {
  name: string;
  description?: string | null;
  brand_id: number;
  strategy_id?: number | null;
  start_date?: string | null;
}

export interface DashboardSummary {
  active_campaigns: number;
  total_reach: number;
  avg_engagement_rate: number;
  scheduled_posts: number;
}

export interface AIInsight {
  tip: string;
  action: string;
}

export interface PlanUsage {
  plan_name: string;
  ai_generations_used: number;
  ai_generation_limit: number;
}

export interface AnalyticsOverview {
  total_impressions: number;
  total_engagement: number;
  total_clicks: number;
  total_conversions: number;
  total_reach: number;
  avg_engagement_rate: number;
}

export interface ChannelBreakdown {
  platform: string;
  total_reach: number;
  total_engagement: number;
  total_clicks: number;
}

export interface TimeSeriesPoint {
  date: string;
  reach: number;
  engagement: number;
}

export type ContentCalendarMap = Record<string, ContentItemOut[]>;

export interface ContentItemOut {
  id: number;
  title: string;
  content_type: string;
  platform: string;
  objective: string | null;
  body_text: string | null;
  scheduled_date: string;
  scheduled_time: string | null;
  status: string;
  schedule_id: number;
  created_at: string;
}

export interface QuickActionResponse {
  result: string;
}

export interface BlogPostRequest {
  topic: string;
  brand_id: number;
}

export interface GenerateImageRequest {
  prompt: string;
  brand_id: number;
}

export type ContentAgentType =
  | "social_media_post"
  | "email_campaign"
  | "promotional_message";

export type ContentAgentPlatform =
  | "instagram"
  | "twitter"
  | "linkedin"
  | "facebook"
  | "email";

export interface TextAgentRequest {
  message: string;
  campaign_id: number;
  content_type: ContentAgentType;
  platform?: ContentAgentPlatform | null;
}

export interface ContentVariationOut {
  variation_id: number;
  content: string;
  platform_note: string;
}

export interface SEODataOut {
  keywords: string[];
  meta_description: string;
  suggested_title: string;
}

export interface TextAgentResponse {
  content_type: string;
  platform: string | null;
  generated_content: string;
  variations?: ContentVariationOut[] | null;
  hashtags?: string[] | null;
  subject_line?: string | null;
  seo?: SEODataOut | null;
  platform_rules?: Record<string, unknown> | null;
  char_count?: number | null;
  within_limit?: boolean | null;
}

export interface ContentAgentStatus {
  provider: string;
  model: string;
  mode: "live" | "fallback";
  configured: boolean;
}

export type ImageAgentPlatform =
  | "instagram"
  | "facebook"
  | "tiktok"
  | "linkedin"
  | "general";

export type ImageAgentSize = "512x512" | "768x768" | "1024x1024";

export interface ImageAgentRequest {
  message: string;
  campaign_id: number;
  platform?: ImageAgentPlatform;
  image_size?: ImageAgentSize;
  num_variations?: number;
  logo_enabled?: boolean;
  ad_copy?: string | null;
}

export interface GeneratedImageOut {
  image_id: string;
  request_id: string;
  local_path: string;
  image_url: string;
  prompt_used: string;
  ad_copy: string;
  platform: string;
  size: string;
  model_used: string;
  logo_applied: boolean;
  metadata: Record<string, unknown>;
}

export interface ImageAgentResponse {
  request_id: string;
  brand_name: string;
  campaign_goal: string;
  images: GeneratedImageOut[];
  ab_test_ready: boolean;
  generation_time_sec: number;
  knowledge_context: string;
}

export interface ImageAgentStatus {
  provider: string;
  model: string;
  image_backend: string;
  groq_configured: boolean;
  image_backend_configured: boolean;
  output_dir: string;
}

export interface VideoAgentRequest {
  message: string;
  campaign_id: number;
  platforms?: string[];
  budget?: string;
}

export interface ScriptOut {
  hook?: string | null;
  body?: string | null;
  cta?: string | null;
}

export interface VideoPlanOut {
  concept?: string | null;
  script?: ScriptOut | null;
  scenes?: string[];
  visual_style?: string | null;
  audio_style?: string | null;
}

export interface ReasoningOut {
  psychological_trigger?: string | null;
  content_angle?: string | null;
  hook_rationale?: string | null;
  why_this_works?: string | null;
}

export interface VideoAgentResponse {
  status: string;
  video_plan?: VideoPlanOut | null;
  reasoning?: ReasoningOut | null;
  video_prompt?: string | null;
  video_url?: string | null;
  error_message?: string | null;
}

export interface MarketingAgentRequest {
  message: string;
  campaign_id: number;
  budget?: number;
  platforms?: string[];
  goal?: string;
  brand_name?: string | null;
  industry?: string | null;
  audience?: string | null;
  product?: string | null;
}

export interface MarketingAgentResponse {
  status: string;
  strategy?: string | null;
  financial_model?: Record<string, unknown> | null;
  budget_allocation?: Record<string, unknown> | null;
  platform_insight?: string | null;
  decision?: string | null;
  competitor_insight?: string | null;
  error_message?: string | null;
  strategy_id?: number | null;
  calendar_items_created?: number | null;
  calendar_ready?: boolean;
}

export interface CalendarAgentRequest {
  message: string;
  campaign_id: number;
}

export interface CalendarAgentResponse {
  status: string;
  response?: string | null;
  error_message?: string | null;
}

export interface AnalyticsAgentRequest {
  message: string;
  campaign_id: number;
}

export interface AnalyticsAgentResponse {
  status: string;
  response?: string | null;
  error_message?: string | null;
}

export interface AgentChatTurn {
  role: "user" | "assistant";
  content: string;
}

export interface BrandAgentRequest {
  campaign_id: number;
  messages: AgentChatTurn[];
}

export interface BrandAgentResponse {
  status: string;
  response?: string | null;
  error_message?: string | null;
}

export interface BrandSaveResponse {
  status: string;
  response?: string | null;
  saved_fields: Record<string, string>;
  error_message?: string | null;
}

export interface OrchestratorAgentRequest {
  campaign_id: number;
  message: string;
  messages?: AgentChatTurn[];
}

export interface OrchestratorAgentResponse {
  status: string;
  agent?: string | null;
  agent_label?: string | null;
  reason?: string | null;
  response?: string | null;
  error_message?: string | null;
  image_result?: ImageAgentResponse | null;
  video_result?: VideoAgentResponse | null;
}
