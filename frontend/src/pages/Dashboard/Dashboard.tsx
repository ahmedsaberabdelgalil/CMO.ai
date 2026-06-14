import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useRef } from "react";
import {
  Bell,
  CheckCircle2,
  ChevronRight,
  MessageSquareText,
  Plus,
  Target,
  TrendingUp,
} from "lucide-react";
import logo from "@/assets/cmo-logo.png";

import { Button } from "../../components/ui/button";
import { Skeleton } from "../../components/ui/skeleton";
import { NewCampaignModal } from "../../components/NewCampaignModal";
import { deleteCampaign } from "../../services/campaignService";
import { deleteBrand, getBrands} from "../../services/brandService";
import { useCampaign } from "../../hooks/useCampaign";
import { listAssets } from "../../services/assetsService";
import {
  applyCalendarPlan,
  generateCalendarInsight,
} from "../../services/calendarAgentService";
import { exportDocx, exportMarketingPlan } from "../../services/exportService";
import { generateAnalyticsInsight } from "../../services/analyticsAgentService";
import {
  generateBrandCoaching,
  generateBrandReport,
  saveBrandProfile,
  saveStructuredBrandProfile,
} from "../../services/brandAgentService";
import { orchestrate } from "../../services/orchestratorAgentService";
import {
  generateContent,
  getContentAgentStatus,
} from "../../services/contentAgentService";
import {
  generateImageAsync,
  getImageAgentStatus,
} from "../../services/imageAgentService";
import { generateVideoAsync } from "../../services/videoAgentService";
import { generateMarketingStrategy } from "../../services/marketingAgentService";
import type {
  BrandOut,
  CampaignOut,
  ContentAgentPlatform,
  ContentAgentStatus,
  ContentAgentType,
  TextAgentResponse,
  CalendarAgentResponse,
  AnalyticsAgentResponse,
  ImageAgentResponse,
  ImageAgentStatus,
  ImageAgentPlatform,
  VideoAgentResponse,
  MarketingAgentResponse,
} from "../../types/api";

import { agents, nextActions } from "./constants";
import type { AgentId, ChatMessage, DashboardNotification } from "./types";
import {
  buildAgentDemoResponse,
  formatImageAgentResponse,
  formatTextAgentResponse,
  launchWindowDaysFromStart,
  resolveUploadUrl,
} from "./utils";
import { ResultDialog } from "./components/ResultDialog";
import { MetricCard } from "./components/MetricCard";
import { CampaignBrief } from "./components/CampaignBrief";
import { OrchestratorPanel } from "./panels/OrchestratorPanel";
import { MarketPlannerPanel } from "./panels/MarketPlannerPanel";
import type { PlannerFormState } from "./panels/MarketPlannerPanel";
import { BrandPanels } from "./panels/BrandPanels";
import type { BrandProfileForm } from "./panels/BrandPanels";
import { CalendarPanels } from "./panels/CalendarPanels";
import { TextPanels } from "./panels/TextPanels";
import { ImagePanels } from "./panels/ImagePanels";
import { VideoPanels } from "./panels/VideoPanels";
import { AnalyticsPanels } from "./panels/AnalyticsPanels";
import { RightPanel } from "./panels/RightPanel";

const getInitialTextChat = (): ChatMessage[] => [
  {
    role: "assistant",
    text: "I can write campaign copy, compare angles, or expand the approved strategy into drafts.",
  },
];

const getChatStorageKey = (id: number | null | undefined) =>
  id ? `cmo-text-chat-${id}` : "cmo-text-chat-empty";

export default function Dashboard() {
  const navigate = useNavigate();

  const {
    campaigns,
    campaign,
    setCampaignId,
    isLoading: campaignLoading,
    error: campaignError,
    brand,
    brandAudience,
    registerNewCampaign,
    refresh: refreshCampaign,
  } = useCampaign();

  const [activeAgentId, setActiveAgentId] = useState<AgentId>("orchestrator");
  const [newCampaignOpen, setNewCampaignOpen] = useState(false);
  const [modalMode, setModalMode] = useState<"campaign" | "brand">("campaign");
  const [selectedBrandId, setSelectedBrandId] = useState<number | "all">("all");
  const [brands, setBrands] = useState<BrandOut[]>([]);

  const [resultOpen, setResultOpen] = useState(false);
  const [resultTitle, setResultTitle] = useState("");
  const [resultBody, setResultBody] = useState("");

  const [busyAction, setBusyAction] = useState<string | null>(null);
  const [agentStatus, setAgentStatus] = useState<ContentAgentStatus | null>(
    null,
  );
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const notificationsRef = useRef<HTMLDivElement | null>(null);

  const [textChatMessages, setTextChatMessages] =
    useState<ChatMessage[]>(getInitialTextChat());
  const [textLastResult, setTextLastResult] =
    useState<TextAgentResponse | null>(null);
  const [textDraft, setTextDraft] = useState("");

  const getInitialImageChat = (): ChatMessage[] => [
    {
      role: "assistant",
      text: "I can generate campaign visuals, ad creatives, and platform-ready images for this campaign.",
    },
  ];
  const [imageChatMessages, setImageChatMessages] = useState<ChatMessage[]>(
    getInitialImageChat(),
  );
  const [imageLastResult, setImageLastResult] =
    useState<ImageAgentResponse | null>(null);
  const [imageDraft, setImageDraft] = useState("");
  const [imageAgentStatus, setImageAgentStatus] =
    useState<ImageAgentStatus | null>(null);

  const getInitialVideoChat = (): ChatMessage[] => [
    {
      role: "assistant",
      text: "I can create scripts, shot lists, storyboards, and creator briefs for this campaign.",
    },
  ];
  const [videoChatMessages, setVideoChatMessages] = useState<ChatMessage[]>(
    getInitialVideoChat(),
  );
  const [videoLastResult, setVideoLastResult] =
    useState<VideoAgentResponse | null>(null);
  const [videoDraft, setVideoDraft] = useState("");

  const [marketingLastResult, setMarketingLastResult] =
    useState<MarketingAgentResponse | null>(null);
  const [calendarLastResult, setCalendarLastResult] =
    useState<CalendarAgentResponse | null>(null);
  const [analyticsLastResult, setAnalyticsLastResult] =
    useState<AnalyticsAgentResponse | null>(null);
  const [calendarChatMessages, setCalendarChatMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      text: "I can plan launch cadence, balance channels, and find calendar gaps for this campaign.",
    },
  ]);
  const [calendarDraft, setCalendarDraft] = useState("");
  const [analyticsChatMessages, setAnalyticsChatMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      text: "I can summarize performance, find weak funnel steps, and suggest budget shifts.",
    },
  ]);
  const [analyticsDraft, setAnalyticsDraft] = useState("");
  const [brandChatMessages, setBrandChatMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      text: "I'm your brand coach. Tell me about your business and I'll help shape positioning, voice, and audience — then I can generate a full brand strategy report.",
    },
  ]);
  const [brandDraft, setBrandDraft] = useState("");
  const [brandPromptOptions, setBrandPromptOptions] = useState<string[]>([]);
  const [orchestratorChatMessages, setOrchestratorChatMessages] = useState<
    ChatMessage[]
  >([
    {
      role: "assistant",
      text: "I'm the orchestrator. Ask me anything about this campaign and I'll route it to the right agent — content, brand, calendar, analytics, and more.",
    },
  ]);
  const [orchestratorDraft, setOrchestratorDraft] = useState("");
  const [orchestratorFollowups, setOrchestratorFollowups] = useState<string[]>(
    [],
  );
  const filteredCampaigns = useMemo(() => {
    if (selectedBrandId === "all") return campaigns;

    return campaigns.filter((item) => item.brand_id === selectedBrandId);
  }, [campaigns, selectedBrandId]);
  const selectedBrand = useMemo(() => {
    if (selectedBrandId === "all") return null;

    return brands.find((item) => item.id === selectedBrandId) ?? null;
  }, [brands, selectedBrandId]);
  const isAllBrandsView = selectedBrandId === "all";
  const dashboardCampaign =
    isAllBrandsView || campaign?.brand_id === selectedBrandId
      ? campaign
      : null;
  const dashboardBrand = isAllBrandsView ? brand : selectedBrand;
  const dashboardBrandAudience =
    isAllBrandsView
      ? brandAudience
      : selectedBrand?.target_audience ?? null;
  const dashboardCampaignId = dashboardCampaign?.id ?? null;
  const workspaceSummary = isAllBrandsView
    ? `${brands.length} brands in workspace`
    : dashboardCampaign?.name ?? "No active campaign";
  const workspaceDetail = isAllBrandsView
    ? `${filteredCampaigns.length} campaigns available`
    : dashboardBrand?.industry?.trim() || "Brand workspace";
  const headerBrandName = isAllBrandsView
    ? "All brands"
    : dashboardBrand?.brand_name ?? "CMO.ai";
  const headerBrandLogo = isAllBrandsView ? logo : dashboardBrand?.logo_url || logo;
  const headerBrandAlt = isAllBrandsView
    ? "All brands"
    : dashboardBrand?.brand_name
      ? `${dashboardBrand.brand_name} logo`
      : "Brand logo";
  const activeAgent = useMemo(
    () => agents.find((a) => a.id === activeAgentId) ?? agents[0],
    [activeAgentId],
  );

  useEffect(() => {
    if (selectedBrandId === "all") return;
    if (campaign?.brand_id === selectedBrandId) return;

    const nextCampaign = filteredCampaigns[0];
    if (nextCampaign) setCampaignId(nextCampaign.id);
  }, [campaign?.brand_id, filteredCampaigns, selectedBrandId, setCampaignId]);

  const handleCampaignCreated = useCallback(
    (createdCampaign: CampaignOut) => {
      registerNewCampaign(createdCampaign);
      setSelectedBrandId(createdCampaign.brand_id);
      void getBrands()
        .then(setBrands)
        .catch((error) => console.error(error));
    },
    [registerNewCampaign],
  );

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("cmo-user");
    navigate("/login");
  };

  const handleDeleteCampaign = async () => {
    if (!dashboardCampaign?.id) return;

    const confirmed = window.confirm(
      `Delete "${dashboardCampaign.name}"? This will also remove its saved chat history.`,
    );

    if (!confirmed) return;

    await deleteCampaign(dashboardCampaign.id);
    localStorage.removeItem(getChatStorageKey(dashboardCampaign.id));
    window.location.reload();
  };

  const handleDeleteBrand = async () => {
    if (!dashboardBrand?.id) return;

    const confirmed = window.confirm(
      `Delete "${dashboardBrand.brand_name}"? Campaigns connected to this brand may be affected.`,
    );

    if (!confirmed) return;

    await deleteBrand(dashboardBrand.id);
    window.location.reload();
  };

  useEffect(() => {
    setTextLastResult(null);

    if (!dashboardCampaignId) {
      setTextChatMessages(getInitialTextChat());
      return;
    }

    const saved = localStorage.getItem(getChatStorageKey(dashboardCampaignId));

    if (!saved) {
      setTextChatMessages(getInitialTextChat());
      return;
    }

    try {
      setTextChatMessages(JSON.parse(saved) as ChatMessage[]);
    } catch {
      setTextChatMessages(getInitialTextChat());
    }
  }, [dashboardCampaignId]);

  useEffect(() => {
    if (!dashboardCampaignId) return;

    localStorage.setItem(
      getChatStorageKey(dashboardCampaignId),
      JSON.stringify(textChatMessages),
    );
  }, [dashboardCampaignId, textChatMessages]);

  useEffect(() => {
    void getBrands()
      .then(setBrands)
      .catch((error) => console.error(error));
  }, []);

  useEffect(() => {
    let cancelled = false;

    void getImageAgentStatus()
      .then((status) => {
        if (!cancelled) setImageAgentStatus(status);
      })
      .catch(() => {
        if (!cancelled) setImageAgentStatus(null);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;

    void getContentAgentStatus()
      .then((status) => {
        if (!cancelled) setAgentStatus(status);
      })
      .catch(() => {
        if (!cancelled) setAgentStatus(null);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const showResult = useCallback((title: string, body: string) => {
    setResultTitle(title);
    setResultBody(body);
    setResultOpen(true);
  }, []);

  const readinessDisplay = dashboardCampaign ? "72%" : "N/A";
  const projectedLiftDisplay =
    dashboardCampaign?.status === "Completed"
      ? "+18%"
      : dashboardCampaign
        ? "+12%"
        : "N/A";

  const campaignStatusDisplay = dashboardCampaign?.status ?? "N/A";

  const launchWindowDisplay = useMemo(() => {
    if (!dashboardCampaign?.start_date) return "--";
    return launchWindowDaysFromStart(dashboardCampaign.start_date);
  }, [dashboardCampaign?.start_date]);

  const notifications = useMemo<DashboardNotification[]>(
    (() => {
      const items: DashboardNotification[] = [];

      if (agentStatus) {
        items.push(
          agentStatus.mode === "live"
            ? {
                id: "ai-live",
                title: "Text agent is live",
                detail: `Connected to ${agentStatus.provider} for real AI copy generation.`,
                tone: "success",
                showInBadge: false,
                actionLabel: "Open Text",
                actionType: "text",
              }
            : {
                id: "ai-fallback",
                title: "AI fallback mode",
                detail:
                  "The text agent is using fallback output. Check your AI key before the demo.",
                tone: "warn",
                showInBadge: true,
                actionLabel: "Open Text",
                actionType: "text",
              },
        );
      }

      if (imageAgentStatus) {
        items.push(
          imageAgentStatus.image_backend_configured
            ? {
                id: "image-live",
                title: "Image agent is ready",
                detail: `Visual generation is configured with ${imageAgentStatus.image_backend}.`,
                tone: "success",
                showInBadge: false,
                actionLabel: "Open Image",
                actionType: "image",
              }
            : {
                id: "image-config-missing",
                title: "Image agent needs setup",
                detail:
                  "Image generation is not fully configured yet. Check backend image credentials before the demo.",
                tone: "warn",
                showInBadge: true,
                actionLabel: "Open Image",
                actionType: "image",
              },
        );
      }

      if (!campaigns.length) {
        items.push({
          id: "campaign-empty",
          title: "No campaign yet",
          detail: "Create your first campaign to unlock the agent workspace.",
          tone: "warn",
          showInBadge: true,
          actionLabel: "New campaign",
          actionType: "new-campaign",
        });
      } else if (dashboardCampaign && !dashboardCampaign.strategy_id) {
        items.push({
          id: "strategy-missing",
          title: "Marketing plan needed",
          detail:
            "Generate a strategy in Market Planner to link your campaign and populate the content calendar.",
          tone: "info",
          showInBadge: true,
          actionLabel: "Open Planner",
          actionType: "market",
        });
      }

      if (!isAllBrandsView && dashboardCampaign && !dashboardBrand) {
        items.push({
          id: "brand-missing",
          title: "Brand details need attention",
          detail:
            "Your campaign exists, but the brand context has not loaded cleanly yet.",
          tone: "warn",
          showInBadge: true,
          actionLabel: "Open Brand",
          actionType: "brand",
        });
      } else if (dashboardBrand) {
        items.push({
          id: "brand-ready",
          title: `${dashboardBrand.brand_name} is active`,
          detail:
            dashboardBrand.target_audience?.trim() ||
            "Add audience details to make the suggestions feel more tailored.",
          tone: "info",
          showInBadge: false,
          actionLabel: "Open Brand",
          actionType: "brand",
        });
      }

      return items;
    }) as () => DashboardNotification[],
    [
      agentStatus,
      brands.length,
      dashboardBrand,
      dashboardCampaign,
      campaigns.length,
      imageAgentStatus,
      isAllBrandsView,
    ],
  );

  const activeNotificationCount = useMemo(
    () => notifications.filter((item) => item.showInBadge !== false).length,
    [notifications],
  );

  const handleNotificationAction = useCallback(
    (actionType?: DashboardNotification["actionType"]) => {
      if (!actionType) return;

      if (actionType === "new-campaign") {
        setModalMode("campaign");
        setNewCampaignOpen(true);
      }

      if (actionType === "brand") setActiveAgentId("brand");
      if (actionType === "market") setActiveAgentId("market");
      if (actionType === "calendar") setActiveAgentId("calendar");
      if (actionType === "text") setActiveAgentId("text");
      if (actionType === "image") setActiveAgentId("image");

      setNotificationsOpen(false);
    },
    [],
  );

  useEffect(() => {
    if (!notificationsOpen) return;

    const handlePointerDown = (event: MouseEvent) => {
      if (
        notificationsRef.current &&
        !notificationsRef.current.contains(event.target as Node)
      ) {
        setNotificationsOpen(false);
      }
    };

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setNotificationsOpen(false);
      }
    };

    document.addEventListener("mousedown", handlePointerDown);
    document.addEventListener("keydown", handleEscape);

    return () => {
      document.removeEventListener("mousedown", handlePointerDown);
      document.removeEventListener("keydown", handleEscape);
    };
  }, [notificationsOpen]);

  const runMarketingGenerate = useCallback(
    async (
      message: string,
      busyKey: string,
      options?: {
        budget?: number;
        platforms?: string[];
        goal?: string;
        brand_name?: string;
        industry?: string;
        audience?: string;
        product?: string;
      },
    ) => {
      if (!dashboardCampaign) {
        showResult(
          "Select a campaign",
          "Choose a brand and campaign in the sidebar before generating a strategy.",
        );
        return;
      }

      setBusyAction(busyKey);

      try {
        const res = await generateMarketingStrategy({
          message,
          campaign_id: dashboardCampaign.id,
          budget: options?.budget ?? 1000,
          platforms: options?.platforms ?? ["Instagram", "TikTok"],
          goal: options?.goal ?? "Brand Awareness",
          brand_name: options?.brand_name,
          industry: options?.industry,
          audience: options?.audience,
          product: options?.product,
        });
        setMarketingLastResult(res);

        if (res.error_message) {
          showResult("Marketing agent error", res.error_message);
        } else if (res.strategy?.startsWith("Strategy generation failed:")) {
          showResult("Marketing agent error", res.strategy!);
        } else if (res.calendar_ready && res.strategy_id) {
          await refreshCampaign();

          const count = res.calendar_items_created ?? 14;
          showResult(
            "Marketing plan ready",
            `Strategy linked to this campaign with ${count} scheduled posts. Open the Calendar agent to plan and review your schedule.`,
          );
        }
      } catch (e) {
        const err =
          e instanceof Error ? e.message : "Something went wrong";
        showResult("Error", err);
      } finally {
        setBusyAction(null);
      }
    },
    [dashboardCampaign, refreshCampaign, showResult],
  );

  const handleMarketGenerate = useCallback(
    (form: PlannerFormState, message: string) => {
      void runMarketingGenerate(message, "marketgen", {
        budget: form.budget,
        platforms: form.platforms,
        goal: form.mainGoal,
        brand_name: form.brandName,
        industry: form.industry,
        audience: form.targetAudience,
        product: form.productService,
      });
    },
    [runMarketingGenerate],
  );

  const handleBrandReportExport = useCallback(async () => {
    const lastAssistant = [...brandChatMessages]
      .reverse()
      .find((m) => m.role === "assistant");
    if (!lastAssistant) {
      showResult("Nothing to export", "Generate a brand report first.");
      return;
    }
    setBusyAction("brandexport");
    try {
      await exportDocx({
        title: `Brand Report — ${dashboardBrand?.brand_name ?? "Brand"}`,
        content: lastAssistant.text,
        subtitle: dashboardCampaign?.name,
        filename: "brand_report",
      });
    } catch (e) {
      const err = e instanceof Error ? e.message : "Export failed";
      showResult("Export failed", err);
    } finally {
      setBusyAction(null);
    }
  }, [brandChatMessages, dashboardBrand, dashboardCampaign, showResult]);

  const handleMarketExport = useCallback(async () => {
    if (!dashboardCampaign) return;
    setBusyAction("marketexport");
    try {
      await exportMarketingPlan(
        dashboardCampaign.id,
        `marketing_plan_${dashboardCampaign.name}`,
      );
    } catch (e) {
      const err = e instanceof Error ? e.message : "Export failed";
      showResult("Export failed", err);
    } finally {
      setBusyAction(null);
    }
  }, [dashboardCampaign, showResult]);

  const handleMarketQuickAction = useCallback(
    (message: string) => {
      void runMarketingGenerate(message, "marketchat", {
        budget: 1000,
        platforms: ["Instagram", "TikTok"],
        goal: "Brand Awareness",
        brand_name: dashboardBrand?.brand_name,
        industry: dashboardBrand?.industry ?? undefined,
        audience: dashboardBrandAudience ?? undefined,
        product:
          dashboardCampaign?.description?.trim() || dashboardCampaign?.name,
      });
    },
    [
      dashboardBrand,
      dashboardBrandAudience,
      dashboardCampaign,
      runMarketingGenerate,
    ],
  );

  const runCalendarAgent = useCallback(
    async (message: string, busyKey: string) => {
      if (!dashboardCampaign) {
        showResult(
          "Select a campaign",
          "Choose a campaign before using the calendar agent.",
        );
        return;
      }

      setBusyAction(busyKey);
      setCalendarChatMessages((prev) => [...prev, { role: "user", text: message }]);

      try {
        const res = await generateCalendarInsight({
          message,
          campaign_id: dashboardCampaign.id,
        });
        setCalendarLastResult(res);

        const text =
          res.error_message ||
          res.response ||
          "Calendar agent did not return a response.";

        setCalendarChatMessages((prev) => [
          ...prev,
          { role: "assistant", text },
        ]);
      } catch (e) {
        const err = e instanceof Error ? e.message : "Something went wrong";
        setCalendarChatMessages((prev) => [
          ...prev,
          { role: "assistant", text: err },
        ]);
        showResult("Error", err);
      } finally {
        setBusyAction(null);
      }
    },
    [dashboardCampaign, showResult],
  );

  const handleCalendarPlan14 = useCallback(() => {
    void runCalendarAgent(
      "Plan the next 14 days of content for this campaign. Include platform mix, post themes, and timing.",
      "cal14",
    );
  }, [runCalendarAgent]);

  const handleCalendarBalance = useCallback(() => {
    void runCalendarAgent(
      "Balance content across channels for this campaign. Recommend how to distribute posts and effort.",
      "calbalance",
    );
  }, [runCalendarAgent]);

  const handleCalendarFindGaps = useCallback(() => {
    void runCalendarAgent(
      "Find gaps in the content calendar and suggest what to add or reschedule.",
      "calgaps",
    );
  }, [runCalendarAgent]);

  const handleCalendarChatSend = useCallback(
    (message = calendarDraft) => {
      const trimmed = message.trim();
      if (!trimmed) return;
      setCalendarDraft("");
      void runCalendarAgent(trimmed, "calchat");
    },
    [calendarDraft, runCalendarAgent],
  );

  const handleCalendarApply = useCallback(
    async (message = "") => {
      if (!dashboardCampaign) {
        showResult(
          "Select a campaign",
          "Choose a campaign before generating a schedule.",
        );
        return;
      }

      setBusyAction("calapply");
      try {
        const res = await applyCalendarPlan({
          campaign_id: dashboardCampaign.id,
          message,
          days: 14,
        });
        if (res.status === "success") {
          await refreshCampaign();
          setCalendarChatMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              text:
                res.response ??
                `Scheduled ${res.items_created} posts on your calendar.`,
            },
          ]);
          showResult(
            "Calendar updated",
            res.response ?? `Created ${res.items_created} posts.`,
          );
        } else {
          showResult(
            "Could not update calendar",
            res.error_message ?? "Try again.",
          );
        }
      } catch (e) {
        const err = e instanceof Error ? e.message : "Something went wrong";
        showResult("Error", err);
      } finally {
        setBusyAction(null);
      }
    },
    [dashboardCampaign, refreshCampaign, showResult],
  );

  const runAnalyticsAgent = useCallback(
    async (message: string, busyKey: string) => {
      if (!dashboardCampaign) {
        showResult(
          "Select a campaign",
          "Choose a campaign before using the analytics agent.",
        );
        return;
      }

      setBusyAction(busyKey);
      setAnalyticsChatMessages((prev) => [
        ...prev,
        { role: "user", text: message },
      ]);

      try {
        const res = await generateAnalyticsInsight({
          message,
          campaign_id: dashboardCampaign.id,
        });
        setAnalyticsLastResult(res);

        const text =
          res.error_message ||
          res.response ||
          "Analytics agent did not return a response.";

        setAnalyticsChatMessages((prev) => [
          ...prev,
          { role: "assistant", text },
        ]);
      } catch (e) {
        const err = e instanceof Error ? e.message : "Something went wrong";
        setAnalyticsChatMessages((prev) => [
          ...prev,
          { role: "assistant", text: err },
        ]);
        showResult("Error", err);
      } finally {
        setBusyAction(null);
      }
    },
    [dashboardCampaign, showResult],
  );

  const handleAnalyticsSummarize = useCallback(() => {
    void runAnalyticsAgent(
      "Summarize overall marketing performance for this campaign.",
      "asum",
    );
  }, [runAnalyticsAgent]);

  const handleAnalyticsWeakFunnel = useCallback(() => {
    void runAnalyticsAgent(
      "Find the weakest step in the marketing funnel and explain why.",
      "afunnel",
    );
  }, [runAnalyticsAgent]);

  const handleAnalyticsBudgetShift = useCallback(() => {
    void runAnalyticsAgent(
      "Suggest how to shift budget across channels based on current performance.",
      "abudget",
    );
  }, [runAnalyticsAgent]);

  const handleAnalyticsChatSend = useCallback(
    (message = analyticsDraft) => {
      const trimmed = message.trim();
      if (!trimmed) return;
      setAnalyticsDraft("");
      void runAnalyticsAgent(trimmed, "analychat");
    },
    [analyticsDraft, runAnalyticsAgent],
  );

  const handleAnalyticsRun = useCallback(
    async (
      focus: string,
      metrics: Record<string, number> | null,
      question: string,
    ) => {
      if (!dashboardCampaign) {
        showResult(
          "Select a campaign",
          "Choose a campaign before running analytics.",
        );
        return;
      }

      const focusLabels: Record<string, string> = {
        overall: "Summarize overall performance",
        funnel: "Find the weakest funnel step",
        budget: "Recommend a budget reallocation",
        channels: "Compare channel performance",
        audience: "Analyze audience reach and conversion",
      };
      const userText =
        question || focusLabels[focus] || "Run a performance analysis";

      setBusyAction("analyrun");
      setAnalyticsChatMessages((prev) => [
        ...prev,
        { role: "user", text: userText },
      ]);

      try {
        const res = await generateAnalyticsInsight({
          campaign_id: dashboardCampaign.id,
          focus,
          metrics,
          message: question,
        });
        setAnalyticsLastResult(res);
        const text =
          res.error_message ||
          res.response ||
          "Analytics agent did not return a response.";
        setAnalyticsChatMessages((prev) => [
          ...prev,
          { role: "assistant", text },
        ]);
      } catch (e) {
        const err = e instanceof Error ? e.message : "Something went wrong";
        setAnalyticsChatMessages((prev) => [
          ...prev,
          { role: "assistant", text: err },
        ]);
        showResult("Error", err);
      } finally {
        setBusyAction(null);
      }
    },
    [dashboardCampaign, showResult],
  );

  const runBrandCoaching = useCallback(
    async (message: string, busyKey: string) => {
      if (!dashboardCampaign) {
        showResult(
          "Select a campaign",
          "Choose a campaign before using the brand coach.",
        );
        return;
      }

      setBusyAction(busyKey);
      const nextMessages: ChatMessage[] = [
        ...brandChatMessages,
        { role: "user", text: message },
      ];
      setBrandChatMessages(nextMessages);

      try {
        const res = await generateBrandCoaching({
          campaign_id: dashboardCampaign.id,
          messages: nextMessages.map((m) => ({ role: m.role, content: m.text })),
        });
        const text =
          res.error_message ||
          res.response ||
          "Brand agent did not return a response.";
        setBrandChatMessages((prev) => [...prev, { role: "assistant", text }]);
      } catch (e) {
        const err = e instanceof Error ? e.message : "Something went wrong";
        setBrandChatMessages((prev) => [...prev, { role: "assistant", text: err }]);
        showResult("Error", err);
      } finally {
        setBusyAction(null);
      }
    },
    [dashboardCampaign, brandChatMessages, showResult],
  );

  const handleBrandChatSend = useCallback(
    (message = brandDraft) => {
      const trimmed = message.trim();
      if (!trimmed) return;
      setBrandDraft("");
      void runBrandCoaching(trimmed, "brandchat");
    },
    [brandDraft, runBrandCoaching],
  );

  const handleBrandReport = useCallback(async () => {
    if (!dashboardCampaign) {
      showResult(
        "Select a campaign",
        "Choose a campaign before generating a brand report.",
      );
      return;
    }

    setBusyAction("brandreport");
    setBrandChatMessages((prev) => [
      ...prev,
      { role: "user", text: "Generate a full brand strategy report." },
    ]);

    try {
      const res = await generateBrandReport({
        campaign_id: dashboardCampaign.id,
        messages: brandChatMessages.map((m) => ({
          role: m.role,
          content: m.text,
        })),
      });
      const text =
        res.error_message ||
        res.response ||
        "Brand agent did not return a report.";
      setBrandChatMessages((prev) => [...prev, { role: "assistant", text }]);
    } catch (e) {
      const err = e instanceof Error ? e.message : "Something went wrong";
      setBrandChatMessages((prev) => [...prev, { role: "assistant", text: err }]);
      showResult("Error", err);
    } finally {
      setBusyAction(null);
    }
  }, [dashboardCampaign, brandChatMessages, showResult]);

  const handleBrandSaveProfile = useCallback(async () => {
    if (!dashboardCampaign) {
      showResult(
        "Select a campaign",
        "Choose a campaign before saving a brand profile.",
      );
      return;
    }

    setBusyAction("brandsave");
    try {
      const res = await saveBrandProfile({
        campaign_id: dashboardCampaign.id,
        messages: brandChatMessages.map((m) => ({
          role: m.role,
          content: m.text,
        })),
      });

      const text =
        res.error_message ||
        res.response ||
        "Brand profile could not be saved.";
      setBrandChatMessages((prev) => [...prev, { role: "assistant", text }]);

      if (res.status === "success") {
        await refreshCampaign();
        void getBrands()
          .then(setBrands)
          .catch((error) => console.error(error));
        showResult("Brand profile saved", text);
      }
    } catch (e) {
      const err = e instanceof Error ? e.message : "Something went wrong";
      setBrandChatMessages((prev) => [...prev, { role: "assistant", text: err }]);
      showResult("Error", err);
    } finally {
      setBusyAction(null);
    }
  }, [dashboardCampaign, brandChatMessages, refreshCampaign, showResult]);

  const handleBrandProfileSave = useCallback(
    async (form: BrandProfileForm) => {
      if (!dashboardCampaign) {
        showResult(
          "Select a campaign",
          "Choose a campaign before saving a brand profile.",
        );
        return;
      }

      setBusyAction("brandprofile");
      try {
        const res = await saveStructuredBrandProfile({
          campaign_id: dashboardCampaign.id,
          brand_name: form.brandName,
          industry: form.industry,
          target_audience: form.targetAudience,
          value_proposition: form.valueProposition,
          tone_of_voice: form.toneOfVoice,
          positioning: form.positioning,
        });

        if (res.status === "success") {
          setBrandPromptOptions(res.suggestions ?? []);
          await refreshCampaign();
          void getBrands()
            .then(setBrands)
            .catch((error) => console.error(error));
          showResult(
            "Brand profile saved",
            res.response ?? "Your brand profile is now shared with every agent.",
          );
        } else {
          showResult("Could not save", res.error_message ?? "Try again.");
        }
      } catch (e) {
        const err = e instanceof Error ? e.message : "Something went wrong";
        showResult("Error", err);
      } finally {
        setBusyAction(null);
      }
    },
    [dashboardCampaign, refreshCampaign, showResult],
  );

  const runOrchestrator = useCallback(
    async (message: string, busyKey: string) => {
      if (!dashboardCampaign) {
        showResult(
          "Select a campaign",
          "Choose a campaign before using the orchestrator.",
        );
        return;
      }

      setBusyAction(busyKey);
      const history = orchestratorChatMessages.map((m) => ({
        role: m.role,
        content: m.text,
      }));
      setOrchestratorChatMessages((prev) => [
        ...prev,
        { role: "user", text: message },
      ]);

      try {
        const res = await orchestrate({
          campaign_id: dashboardCampaign.id,
          message,
          messages: history,
        });
        const body =
          res.error_message ||
          res.response ||
          "Orchestrator did not return a response.";
        const prefix = res.agent_label ? `[Routed to ${res.agent_label}]\n` : "";

        const images = res.image_result?.images?.map((img) =>
          resolveUploadUrl(img.image_url),
        );
        const videoUrl = res.video_result?.video_url
          ? resolveUploadUrl(res.video_result.video_url)
          : undefined;

        if (res.image_result) {
          setImageLastResult(res.image_result);
        }
        if (res.video_result) {
          setVideoLastResult(res.video_result);
        }
        if (res.marketing_result) {
          setMarketingLastResult(res.marketing_result);
          if (res.marketing_result.calendar_ready) {
            await refreshCampaign();
          }
        }
        setOrchestratorFollowups(res.suggestions ?? []);

        setOrchestratorChatMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            text: `${prefix}${body}`,
            images: images && images.length ? images : undefined,
            videoUrl,
          },
        ]);
      } catch (e) {
        const err = e instanceof Error ? e.message : "Something went wrong";
        setOrchestratorChatMessages((prev) => [
          ...prev,
          { role: "assistant", text: err },
        ]);
        showResult("Error", err);
      } finally {
        setBusyAction(null);
      }
    },
    [dashboardCampaign, orchestratorChatMessages, refreshCampaign, showResult],
  );

  const handleOrchestratorChatSend = useCallback(
    (message = orchestratorDraft) => {
      const trimmed = message.trim();
      if (!trimmed) return;
      setOrchestratorDraft("");
      void runOrchestrator(trimmed, "orchchat");
    },
    [orchestratorDraft, runOrchestrator],
  );

  const runTextGenerate = useCallback(
    async (
      message: string,
      content_type: ContentAgentType,
      platform: ContentAgentPlatform | null,
      busyKey: string,
    ) => {
      if (!dashboardCampaign) return;

      setBusyAction(busyKey);
      setTextChatMessages((prev) => [...prev, { role: "user", text: message }]);

      try {
        const res = await generateContent({
          message,
          campaign_id: dashboardCampaign.id,
          content_type,
          platform: platform ?? undefined,
        });

        setTextLastResult(res);

        const formatted = formatTextAgentResponse(res);

        setTextChatMessages((prev) => [
          ...prev,
          { role: "assistant", text: formatted },
        ]);

        showResult("Generated content", formatted);
      } catch (e) {
        const err = e instanceof Error ? e.message : "Something went wrong";

        setTextChatMessages((prev) => [
          ...prev,
          { role: "assistant", text: err },
        ]);

        showResult("Error", err);
      } finally {
        setBusyAction(null);
      }
    },
    [dashboardCampaign, showResult],
  );

  const handleTextLinkedIn = useCallback(() => {
    if (!dashboardCampaign) return;

    void runTextGenerate(
      `Write a LinkedIn post for ${dashboardCampaign.name}`,
      "social_media_post",
      "linkedin",
      "li",
    );
  }, [dashboardCampaign, runTextGenerate]);

  const handleTextEmail = useCallback(() => {
    if (!dashboardCampaign) return;

    void runTextGenerate(
      `Draft an email sequence for ${dashboardCampaign.name}`,
      "email_campaign",
      "email",
      "email",
    );
  }, [dashboardCampaign, runTextGenerate]);

  const handleTextHooks = useCallback(() => {
    if (!dashboardCampaign) return;

    void runTextGenerate(
      `Create ad hook directions for ${dashboardCampaign.name}`,
      "promotional_message",
      "linkedin",
      "hooks",
    );
  }, [dashboardCampaign, runTextGenerate]);

  const handleTextChatSend = useCallback(
    (message = textDraft) => {
      const trimmed = message.trim();
      if (!trimmed || !dashboardCampaign) return;

      setTextDraft("");

      void runTextGenerate(
        trimmed,
        "social_media_post",
        "instagram",
        "textchat",
      );
    },
    [textDraft, dashboardCampaign, runTextGenerate],
  );

  const runImageGenerate = useCallback(
    async (
      message: string,
      platform: ImageAgentPlatform,
      numVariations: number,
      busyKey: string,
    ) => {
      if (!dashboardCampaign) return;

      setBusyAction(busyKey);
      setImageChatMessages((prev) => [
        ...prev,
        { role: "user", text: message },
      ]);

      try {
        const res = await generateImageAsync({
          message,
          campaign_id: dashboardCampaign.id,
          platform,
          num_variations: numVariations,
          logo_enabled: false,
        });
        setImageLastResult(res);
        const formatted = formatImageAgentResponse(res);
        setImageChatMessages((prev) => [
          ...prev,
          { role: "assistant", text: formatted },
        ]);
        showResult("Generated images", formatted);
      } catch (e) {
        const err =
          e instanceof Error ? e.message : "Something went wrong";
        setImageChatMessages((prev) => [
          ...prev,
          { role: "assistant", text: err },
        ]);
        showResult("Error", err);
      } finally {
        setBusyAction(null);
      }
    },
    [dashboardCampaign, showResult],
  );

  const handleImageGenerateVisual = useCallback(() => {
    if (!dashboardCampaign) return;
    void runImageGenerate(
      `Campaign visual for ${dashboardCampaign.name}`,
      "instagram",
      1,
      "imggen",
    );
  }, [dashboardCampaign, runImageGenerate]);

  const handleImageGenerateVariations = useCallback(() => {
    if (!dashboardCampaign) return;
    void runImageGenerate(
      `A/B test ad creatives for ${dashboardCampaign.name}`,
      "instagram",
      2,
      "imgvar",
    );
  }, [dashboardCampaign, runImageGenerate]);

  const handleImageChatSend = useCallback(
    (message = imageDraft) => {
      const trimmed = message.trim();
      if (!trimmed || !dashboardCampaign) return;
      setImageDraft("");
      void runImageGenerate(trimmed, "instagram", 1, "imgchat");
    },
    [imageDraft, dashboardCampaign, runImageGenerate],
  );

  const handleImageAssets = useCallback(async () => {
    if (!dashboardCampaign) return;

    setBusyAction("assets");

    try {
      const list = await listAssets({ campaign_id: dashboardCampaign.id });

      const text =
        list.length === 0
          ? "No assets found for this campaign."
          : list
              .map(
                (a) =>
                  `* ${a.name} (${a.asset_type}) - ${a.url.slice(0, 80)}${
                    a.url.length > 80 ? "..." : ""
                  }`,
              )
              .join("\n");

      showResult("Campaign assets", text);
    } catch (e) {
      showResult(
        "Error",
        e instanceof Error ? e.message : "Something went wrong",
      );
    } finally {
      setBusyAction(null);
    }
  }, [dashboardCampaign, showResult]);

  const runVideoGenerate = useCallback(
    async (message: string, busyKey: string) => {
      if (!dashboardCampaign) return;

      setBusyAction(busyKey);
      setVideoChatMessages((prev) => [
        ...prev,
        { role: "user", text: message },
      ]);

      try {
        const res = await generateVideoAsync({
          message,
          campaign_id: dashboardCampaign.id,
        });
        setVideoLastResult(res);

        if (res.status === "error" && res.error_message) {
          setVideoChatMessages((prev) => [
            ...prev,
            { role: "assistant", text: res.error_message! },
          ]);
          showResult("Video agent error", res.error_message);
        } else {
          const hook = res.video_plan?.script?.hook;
          const summary = [
            `Status: ${res.status}`,
            res.video_plan?.concept,
            hook ? `Hook: ${hook}` : null,
          ]
            .filter(Boolean)
            .join("\n\n");
          setVideoChatMessages((prev) => [
            ...prev,
            { role: "assistant", text: summary },
          ]);
        }
      } catch (e) {
        const err =
          e instanceof Error ? e.message : "Something went wrong";
        setVideoChatMessages((prev) => [
          ...prev,
          { role: "assistant", text: err },
        ]);
        showResult("Error", err);
      } finally {
        setBusyAction(null);
      }
    },
    [dashboardCampaign, showResult],
  );

  const handleVideoScript = useCallback(() => {
    if (!dashboardCampaign) return;
    void runVideoGenerate(
      `Write a 30-second video script for ${dashboardCampaign.name}`,
      "vscript",
    );
  }, [dashboardCampaign, runVideoGenerate]);

  const handleVideoStoryboard = useCallback(() => {
    if (!dashboardCampaign) return;
    void runVideoGenerate("Create detailed storyboard", "vstoryboard");
  }, [dashboardCampaign, runVideoGenerate]);

  const handleVideoCreatorBrief = useCallback(() => {
    if (!dashboardCampaign) return;
    void runVideoGenerate("Write creator brief", "vbrief");
  }, [dashboardCampaign, runVideoGenerate]);

  const handleVideoChatSend = useCallback(
    (message = videoDraft) => {
      const trimmed = message.trim();
      if (!trimmed || !dashboardCampaign) return;
      setVideoDraft("");
      void runVideoGenerate(trimmed, "videochat");
    },
    [videoDraft, dashboardCampaign, runVideoGenerate],
  );

  const handleDemoAgentAction = useCallback(
    (agentId: AgentId, action: string) => {
      const agentName =
        agents.find((agent) => agent.id === agentId)?.name ?? "Agent";

      showResult(
        `${agentName}: ${action}`,
        buildAgentDemoResponse(
          agentId,
          action,
          dashboardCampaign,
          dashboardBrandAudience,
        ),
      );
    },
    [dashboardBrandAudience, dashboardCampaign, showResult],
  );

  if (campaignLoading && !dashboardCampaign && campaigns.length === 0) {
    return (
      <div className="min-h-screen bg-[radial-gradient(circle_at_top_right,rgba(129,69,255,0.18),transparent_28%),radial-gradient(circle_at_bottom_left,rgba(73,34,151,0.22),transparent_34%),linear-gradient(180deg,#0a0a14_0%,#080910_100%)] p-8 text-white">
        <div className="max-w-lg mx-auto space-y-3">
          <Skeleton className="w-full h-10 bg-white/10" />
          <Skeleton className="w-full h-32 bg-white/10" />
          <Skeleton className="w-full h-48 bg-white/10" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_right,rgba(129,69,255,0.18),transparent_28%),radial-gradient(circle_at_bottom_left,rgba(73,34,151,0.22),transparent_34%),linear-gradient(180deg,#0a0a14_0%,#080910_100%)] text-white">
      <ResultDialog
        open={resultOpen}
        title={resultTitle}
        body={resultBody}
        onOpenChange={setResultOpen}
      />

      <NewCampaignModal
        open={newCampaignOpen}
        mode={modalMode}
        onOpenChange={setNewCampaignOpen}
        onCreated={handleCampaignCreated}
      />

      <div className="flex min-h-screen">
        <aside className="hidden w-72 shrink-0 border-r border-white/10 bg-[rgba(9,11,24,0.88)] px-4 py-5 backdrop-blur-xl lg:block">
          <div className="px-2 mb-8 space-y-3">
            <button
              type="button"
              onClick={() => navigate("/landing")}
              className="transition hover:opacity-90"
            >
              <img
                src={logo}
                alt="CMO.ai"
                className="h-12 w-auto drop-shadow-[0_16px_32px_rgba(97,66,220,0.35)]"
              />
            </button>

            <div>
              <p className="text-sm font-semibold text-white/90">
                Operations workspace
              </p>
              <p className="text-xs text-white/50">
                Campaign orchestration and agent control
              </p>
            </div>

            <button
              type="button"
              onClick={handleLogout}
              className="w-full px-4 py-3 mt-4 text-sm font-semibold text-red-200 transition border rounded-2xl border-red-400/20 bg-red-500/10 hover:bg-red-500/20 hover:text-white"
            >
              Logout
            </button>
          </div>

          <div className="space-y-2">
            {agents.map((agent) => {
              const Icon = agent.icon;
              const isActive = agent.id === activeAgentId;

              return (
                <button
                  key={agent.id}
                  type="button"
                  onClick={() => setActiveAgentId(agent.id)}
                  className={`flex w-full items-center gap-3 rounded-2xl px-3 py-3 text-left transition ${
                    isActive
                      ? "border border-white/10 bg-[linear-gradient(180deg,rgba(151,111,255,0.92),rgba(86,48,204,0.92))] text-white shadow-[0_18px_35px_rgba(65,34,153,0.32)]"
                      : "text-white/70 hover:bg-white/10 hover:text-white"
                  }`}
                >
                  <Icon
                    className={`size-5 shrink-0 ${
                      isActive ? "text-cosmic" : agent.accent
                    }`}
                  />

                  <span className="flex-1 min-w-0">
                    <span className="block text-sm font-medium truncate">
                      {agent.shortName}
                    </span>
                    <span
                      className={`block truncate text-xs ${
                        isActive ? "text-cosmic/60" : "text-white/40"
                      }`}
                    >
                      {agent.navSubtitle}
                    </span>
                  </span>

                  <ChevronRight className="opacity-50 size-4 shrink-0" />
                </button>
              );
            })}
          </div>
        </aside>

        <main className="flex-1 min-w-0">
          <header className="relative z-40 border-b border-white/10 bg-[rgba(12,14,30,0.82)] px-4 py-5 backdrop-blur-xl md:px-6">
            <div className="grid gap-5 xl:grid-cols-[minmax(0,1.1fr)_minmax(380px,0.9fr)] xl:items-start">
              <div className="min-w-0">
                <p className="text-xs uppercase tracking-[0.18em] text-white/40">
                  Dashboard
                </p>

                <div className="flex flex-wrap items-center gap-3 mt-2">
                  <h1 className="text-2xl font-semibold tracking-tight text-white">
                    Campaign overview
                  </h1>

                  {agentStatus ? (
                    <div
                      className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-medium ${
                        agentStatus.mode === "live"
                          ? "border-emerald-400/30 bg-emerald-400/10 text-emerald-200"
                          : "border-amber-400/30 bg-amber-400/10 text-amber-200"
                      }`}
                    >
                      <span className="bg-current rounded-full size-2" />
                      {agentStatus.mode === "live"
                        ? `AI live on ${agentStatus.provider}`
                        : "AI fallback mode"}
                    </div>
                  ) : null}
                </div>

                <div className="mt-4 max-w-[780px] rounded-[28px] border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.04),rgba(255,255,255,0.02))] p-3 shadow-[0_20px_50px_rgba(8,10,24,0.28)]">
                  <div className="grid gap-3 lg:grid-cols-2">
                    <label className="space-y-1.5">
                      <span className="block text-[11px] font-medium uppercase tracking-[0.18em] text-white/38">
                        Brand
                      </span>
                      <select
                        aria-label="Active brand"
                        value={selectedBrandId}
                        onChange={(event) => {
                          const value = event.target.value;

                          if (value === "all") {
                            setSelectedBrandId("all");
                            return;
                          }

                          setSelectedBrandId(Number(value));
                        }}
                        className="h-12 w-full rounded-2xl border border-white/10 bg-white px-4 text-sm font-semibold text-cosmic outline-none"
                      >
                        <option value="all">All brands</option>

                        {brands.map((item) => (
                          <option key={item.id} value={item.id}>
                            {item.brand_name}
                          </option>
                        ))}
                      </select>
                    </label>

                    <label className="space-y-1.5">
                      <span className="block text-[11px] font-medium uppercase tracking-[0.18em] text-white/38">
                        Campaign
                      </span>
                      <select
                        aria-label="Active campaign"
                        value={dashboardCampaign?.id ?? ""}
                        onChange={(event) => {
                          const v = event.target.value;
                          if (v) setCampaignId(Number.parseInt(v, 10));
                        }}
                        disabled={!filteredCampaigns.length}
                        className="h-12 w-full rounded-2xl border border-white/10 bg-white px-4 text-sm font-semibold text-cosmic outline-none disabled:opacity-50"
                      >
                        {!filteredCampaigns.length ? (
                          <option value="">No campaigns</option>
                        ) : (
                          filteredCampaigns.map((item) => (
                            <option key={item.id} value={item.id}>
                              {item.name}
                            </option>
                          ))
                        )}
                      </select>
                    </label>
                  </div>

                  <div className="mt-3 flex flex-wrap gap-2">
                    <Button
                      type="button"
                      className="h-11 rounded-2xl bg-[linear-gradient(90deg,#7b61ff,#42d6ff)] px-4 text-cosmic shadow-[0_16px_30px_rgba(73,125,255,0.25)] hover:opacity-95"
                      onClick={() => {
                        setModalMode("campaign");
                        setNewCampaignOpen(true);
                      }}
                    >
                      <Plus className="size-4" />
                      New Campaign
                    </Button>

                    <Button
                      type="button"
                      className="h-11 rounded-2xl border border-white/10 bg-white/10 px-4 text-white hover:bg-white/15"
                      onClick={() => {
                        setModalMode("brand");
                        setNewCampaignOpen(true);
                      }}
                    >
                      <Plus className="size-4" />
                      New Brand
                    </Button>

                    {!isAllBrandsView && dashboardBrand ? (
                      <Button
                        type="button"
                        className="h-11 rounded-2xl bg-red-500/10 px-4 text-red-200 hover:bg-red-500/20"
                        onClick={() => void handleDeleteBrand()}
                      >
                        Delete Brand
                      </Button>
                    ) : null}

                    {dashboardCampaign ? (
                      <Button
                        type="button"
                        className="h-11 rounded-2xl bg-red-500/10 px-4 text-red-200 hover:bg-red-500/20"
                        onClick={() => void handleDeleteCampaign()}
                      >
                        Delete Campaign
                      </Button>
                    ) : null}
                  </div>
                </div>
              </div>

              <div className="flex flex-col gap-3">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
                  <div className="hidden min-w-[220px] items-center gap-3 rounded-2xl border border-white/10 bg-white/[0.06] px-3 py-2 text-left shadow-[0_12px_30px_rgba(11,13,30,0.25)] md:flex">
                    <div className="flex items-center justify-center overflow-hidden border h-11 w-11 shrink-0 rounded-xl border-white/10 bg-white/10">
                      <img
                        src={headerBrandLogo}
                        alt={headerBrandAlt}
                        className="object-contain w-full h-full p-1"
                      />
                    </div>

                    <div className="min-w-0">
                      <p className="text-sm font-semibold text-white truncate">
                        {headerBrandName}
                      </p>
                      <p className="text-xs truncate text-white/50">
                        {workspaceSummary}
                      </p>
                      <p className="text-[11px] uppercase tracking-[0.16em] text-white/30">
                        {workspaceDetail}
                      </p>
                    </div>
                  </div>

                  <div className="relative" ref={notificationsRef}>
                    <button
                      type="button"
                      onClick={() => setNotificationsOpen((open) => !open)}
                      aria-expanded={notificationsOpen}
                      aria-haspopup="dialog"
                      className="flex h-12 items-center gap-3 rounded-2xl border border-white/10 bg-white/[0.06] px-4 text-sm font-medium text-white shadow-[0_12px_30px_rgba(11,13,30,0.25)] transition hover:bg-white/[0.1]"
                    >
                      <span className="relative inline-flex">
                        <Bell className="size-4" />
                        {activeNotificationCount ? (
                          <span className="absolute -right-1.5 -top-1.5 inline-flex min-h-4 min-w-4 items-center justify-center rounded-full bg-neonPink px-1 text-[10px] font-semibold text-white">
                            {activeNotificationCount}
                          </span>
                        ) : null}
                      </span>
                      Notifications
                    </button>

                    {notificationsOpen ? (
                      <div
                        role="dialog"
                        aria-label="Notifications"
                        className="absolute right-0 top-14 z-[120] flex max-h-[min(70vh,560px)] w-[min(92vw,380px)] flex-col overflow-hidden rounded-2xl border border-white/10 bg-[rgba(13,16,30,0.98)] shadow-[0_24px_60px_rgba(6,8,18,0.55)] backdrop-blur-xl"
                      >
                        <div className="mb-2 flex items-center justify-between border-b border-white/10 px-4 py-3">
                          <div>
                            <p className="text-sm font-semibold text-white">
                              Notifications
                            </p>
                            <p className="text-xs text-white/45">
                              Actionable alerts and workspace status
                            </p>
                          </div>

                          <span className="rounded-full border border-white/10 bg-white/5 px-2 py-1 text-[11px] text-white/60">
                            {activeNotificationCount} active
                          </span>
                        </div>

                        <div className="space-y-2 overflow-y-auto px-3 pb-3">
                          {notifications.length ? (
                            notifications.map((item) => (
                              <div
                                key={item.id}
                                className="rounded-2xl border border-white/10 bg-white/[0.05] p-3"
                              >
                                <div className="flex items-start gap-3">
                                  <span
                                    className={`mt-1 size-2.5 shrink-0 rounded-full ${
                                      item.tone === "success"
                                        ? "bg-emerald-300"
                                        : item.tone === "warn"
                                          ? "bg-amber-300"
                                          : "bg-sky-300"
                                    }`}
                                  />

                                  <div className="flex-1 min-w-0">
                                    <p className="text-sm font-medium text-white">
                                      {item.title}
                                    </p>

                                    <p className="mt-1 text-xs leading-5 break-words text-white/60">
                                      {item.detail}
                                    </p>

                                    {item.actionLabel ? (
                                      <button
                                        type="button"
                                        onClick={() =>
                                          handleNotificationAction(
                                            item.actionType,
                                          )
                                        }
                                        className="mt-3 text-xs font-semibold transition text-cyan-200 hover:text-white"
                                      >
                                        {item.actionLabel}
                                      </button>
                                    ) : null}
                                  </div>
                                </div>
                              </div>
                            ))
                          ) : (
                            <div className="rounded-2xl border border-white/10 bg-white/[0.05] p-4 text-sm text-white/60">
                              No notifications right now.
                            </div>
                          )}
                        </div>
                      </div>
                    ) : null}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
                  <MetricCard
                    label="Readiness"
                    value={readinessDisplay}
                    icon={CheckCircle2}
                  />
                  <MetricCard
                    label="Campaign Status"
                    value={campaignStatusDisplay}
                    icon={MessageSquareText}
                  />
                  <MetricCard
                    label="Launch Window"
                    value={launchWindowDisplay}
                    icon={Target}
                  />
                  <MetricCard
                    label="Projected Lift"
                    value={projectedLiftDisplay}
                    icon={TrendingUp}
                  />
                </div>
              </div>
            </div>
          </header>

          {campaignError ? (
            <div className="px-4 py-3 text-sm text-red-200 border-b border-red-500/40 bg-red-500/10 md:px-6">
              {campaignError}
            </div>
          ) : null}

          <div className="grid min-h-[calc(100vh-96px)] grid-cols-1 xl:grid-cols-[minmax(0,1fr)_380px]">
            <section className="min-w-0 px-4 py-5 md:px-6">
              <div className="grid gap-3 mb-5 lg:hidden">
                <select
                  aria-label="Active agent workspace"
                  value={activeAgentId}
                  onChange={(event) =>
                    setActiveAgentId(event.target.value as AgentId)
                  }
                  className="w-full px-3 text-sm font-semibold bg-white border rounded-md outline-none h-11 border-white/10 text-cosmic"
                >
                  {agents.map((agent) => (
                    <option key={agent.id} value={agent.id}>
                      {agent.name}
                    </option>
                  ))}
                </select>
              </div>

              {!dashboardCampaign && !campaignLoading ? (
                <div className="rounded-md border border-white/10 bg-white/[0.04] p-8 text-center text-white/70">
                  <p className="text-lg font-medium text-white">
                    {selectedBrandId === "all"
                      ? "No campaigns yet"
                      : "No campaigns for this brand"}
                  </p>

                  <p className="mt-2 text-sm">
                    {selectedBrandId === "all"
                      ? "Create a campaign to populate this workspace."
                      : "Create a campaign for the selected brand to populate this workspace."}
                  </p>

                  <Button
                    type="button"
                    className="mt-4 bg-neonBlue text-cosmic hover:bg-neonBlue/90"
                    onClick={() => {
                      setModalMode("campaign");
                      setNewCampaignOpen(true);
                    }}
                  >
                    <Plus className="size-4" />
                    New Campaign
                  </Button>
                </div>
              ) : dashboardCampaign ? (
                <>
                  <CampaignBrief campaign={dashboardCampaign} />

                  {activeAgentId === "orchestrator" ? (
                    <OrchestratorPanel
                      campaign={dashboardCampaign}
                      brandAudience={dashboardBrandAudience}
                      messages={orchestratorChatMessages}
                      busyAction={busyAction}
                      onPickAgent={setActiveAgentId}
                      onQuickAction={handleOrchestratorChatSend}
                    />
                  ) : activeAgentId === "market" ? (
                    <MarketPlannerPanel
                      campaign={dashboardCampaign}
                      brand={dashboardBrand}
                      brandAudience={dashboardBrandAudience}
                      busyAction={busyAction}
                      lastResult={marketingLastResult}
                      onGenerate={handleMarketGenerate}
                      onOpenCalendar={() => setActiveAgentId("calendar")}
                      onExport={handleMarketExport}
                    />
                  ) : activeAgentId === "brand" ? (
                    <BrandPanels
                      campaign={dashboardCampaign}
                      brand={dashboardBrand}
                      brandAudience={dashboardBrandAudience}
                      busyAction={busyAction}
                      suggestions={brandPromptOptions}
                      onSaveProfile={handleBrandProfileSave}
                      onPromptSelect={handleBrandChatSend}
                    />
                  ) : activeAgentId === "calendar" ? (
                    <CalendarPanels
                      busyAction={busyAction}
                      lastResult={calendarLastResult}
                      messages={calendarChatMessages}
                      onPlan14={handleCalendarPlan14}
                      onBalance={handleCalendarBalance}
                      onFindGaps={handleCalendarFindGaps}
                      onApply={handleCalendarApply}
                    />
                  ) : activeAgentId === "text" ? (
                    <TextPanels
                      agentStatus={agentStatus}
                      busyAction={busyAction}
                      lastResult={textLastResult}
                      messages={textChatMessages}
                      onLinkedIn={handleTextLinkedIn}
                      onEmail={handleTextEmail}
                      onHooks={handleTextHooks}
                    />
                  ) : activeAgentId === "image" ? (
                    <ImagePanels
                      agentStatus={imageAgentStatus}
                      busyAction={busyAction}
                      lastResult={imageLastResult}
                      onGenerateVisual={handleImageGenerateVisual}
                      onGenerateVariations={handleImageGenerateVariations}
                      onAssets={handleImageAssets}
                      onReview={() =>
                        handleDemoAgentAction(
                          "image",
                          "Review visual consistency",
                        )
                      }
                    />
                  ) : activeAgentId === "video" ? (
                    <VideoPanels
                      busyAction={busyAction}
                      lastResult={videoLastResult}
                      onScript={handleVideoScript}
                      onStoryboard={handleVideoStoryboard}
                      onCreatorBrief={handleVideoCreatorBrief}
                    />
                  ) : (
                    <AnalyticsPanels
                      busyAction={busyAction}
                      lastResult={analyticsLastResult}
                      messages={analyticsChatMessages}
                      onRunAnalysis={handleAnalyticsRun}
                    />
                  )}
                </>
              ) : (
                <div className="py-6 space-y-3">
                  <Skeleton className="w-full h-24 bg-white/10" />
                  <Skeleton className="w-full h-48 bg-white/10" />
                </div>
              )}
            </section>

            <RightPanel
              activeAgent={activeAgent}
              campaign={dashboardCampaign}
              brand={dashboardBrand}
              brandAudience={dashboardBrandAudience}
              nextActions={nextActions[activeAgentId]}
              onDemoAction={handleDemoAgentAction}
              orchestratorChatMessages={orchestratorChatMessages}
              orchestratorDraft={orchestratorDraft}
              orchestratorFollowups={orchestratorFollowups}
              onOrchestratorDraftChange={setOrchestratorDraft}
              onOrchestratorChatSend={handleOrchestratorChatSend}
              brandChatMessages={brandChatMessages}
              brandDraft={brandDraft}
              onBrandDraftChange={setBrandDraft}
              onBrandChatSend={handleBrandChatSend}
              onBrandReport={handleBrandReport}
              onBrandReportExport={handleBrandReportExport}
              onBrandSaveProfile={handleBrandSaveProfile}
              onCalendarPlan14={handleCalendarPlan14}
              onCalendarBalance={handleCalendarBalance}
              onCalendarFindGaps={handleCalendarFindGaps}
              onMarketQuickAction={handleMarketQuickAction}
              calendarChatMessages={calendarChatMessages}
              calendarDraft={calendarDraft}
              onCalendarDraftChange={setCalendarDraft}
              onCalendarChatSend={handleCalendarChatSend}
              analyticsChatMessages={analyticsChatMessages}
              analyticsDraft={analyticsDraft}
              onAnalyticsDraftChange={setAnalyticsDraft}
              onAnalyticsChatSend={handleAnalyticsChatSend}
              onAnalyticsSummarize={handleAnalyticsSummarize}
              onAnalyticsWeakFunnel={handleAnalyticsWeakFunnel}
              onAnalyticsBudgetShift={handleAnalyticsBudgetShift}
              onTextLi={handleTextLinkedIn}
              onTextEmail={handleTextEmail}
              onTextHooks={handleTextHooks}
              textChatMessages={textChatMessages}
              textDraft={textDraft}
              onTextDraftChange={setTextDraft}
              onTextChatSend={handleTextChatSend}
              imageChatMessages={imageChatMessages}
              imageLastResult={imageLastResult}
              imageDraft={imageDraft}
              onImageDraftChange={setImageDraft}
              onImageChatSend={handleImageChatSend}
              onImgGenerateVisual={handleImageGenerateVisual}
              onImgAssets={handleImageAssets}
              videoChatMessages={videoChatMessages}
              videoLastResult={videoLastResult}
              videoDraft={videoDraft}
              onVideoDraftChange={setVideoDraft}
              onVideoChatSend={handleVideoChatSend}
              onVideoScript={handleVideoScript}
              onVideoStoryboard={handleVideoStoryboard}
              onVideoBrief={handleVideoCreatorBrief}
              busyAction={busyAction}
            />
          </div>
        </main>
      </div>
    </div>
  );
}
