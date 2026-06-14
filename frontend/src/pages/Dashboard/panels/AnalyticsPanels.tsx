import { useState } from "react";
import { BarChart3, Loader2 } from "lucide-react";
import { Button } from "../../../components/ui/button";
import { Input } from "../../../components/ui/input";
import { Textarea } from "../../../components/ui/textarea";
import type { AnalyticsAgentResponse } from "../../../types/api";
import { PANEL_CLASS, SUBPANEL_CLASS } from "../constants";
import type { ChatMessage } from "../types";

const FOCUS_OPTIONS = [
  { value: "overall", label: "Overall performance" },
  { value: "funnel", label: "Funnel weakness" },
  { value: "budget", label: "Budget allocation" },
  { value: "channels", label: "Channel comparison" },
  { value: "audience", label: "Audience insights" },
];

const METRIC_FIELDS = [
  { key: "reach", label: "Reach" },
  { key: "impressions", label: "Impressions" },
  { key: "clicks", label: "Clicks" },
  { key: "conversions", label: "Conversions" },
  { key: "spend", label: "Spend ($)" },
];

export function AnalyticsPanels({
  busyAction,
  lastResult,
  messages,
  onRunAnalysis,
}: {
  busyAction: string | null;
  lastResult: AnalyticsAgentResponse | null;
  messages: ChatMessage[];
  onRunAnalysis: (
    focus: string,
    metrics: Record<string, number> | null,
    question: string,
  ) => void;
}) {
  const [focus, setFocus] = useState("overall");
  const [question, setQuestion] = useState("");
  const [useManual, setUseManual] = useState(false);
  const [metrics, setMetrics] = useState<Record<string, string>>({});

  const isGenerating =
    busyAction === "asum" ||
    busyAction === "afunnel" ||
    busyAction === "abudget" ||
    busyAction === "analychat" ||
    busyAction === "analyrun";
  const hasChatHistory = messages.length > 1;
  const visibleMessages = hasChatHistory ? messages.slice(1) : messages;

  const handleRun = () => {
    let parsed: Record<string, number> | null = null;
    if (useManual) {
      parsed = {};
      for (const field of METRIC_FIELDS) {
        const raw = metrics[field.key];
        if (raw !== undefined && raw !== "" && !Number.isNaN(Number(raw))) {
          parsed[field.key] = Number(raw);
        }
      }
      if (Object.keys(parsed).length === 0) parsed = null;
    }
    onRunAnalysis(focus, parsed, question.trim());
  };

  return (
    <div className="space-y-5">
      <section className="grid gap-5 2xl:grid-cols-[minmax(0,1.2fr)_320px]">
        <div className={`${PANEL_CLASS} p-5`}>
          <div className="flex items-center gap-2 text-neonBlue">
            <BarChart3 className="size-5" />
            <h2 className="text-2xl font-semibold">Performance Analytics</h2>
          </div>
          <p className="mt-3 text-sm leading-6 text-white/70">
            Choose what to analyze and (optionally) enter your own numbers. The
            agent uses your brand, plan, and metrics to produce insights.
          </p>

          <div className="grid gap-4 mt-5">
            <label className="space-y-2">
              <span className="text-sm text-white/70">Analysis focus</span>
              <select
                value={focus}
                onChange={(e) => setFocus(e.target.value)}
                className="w-full px-3 text-sm border rounded-md outline-none h-11 border-white/10 bg-white text-cosmic"
              >
                {FOCUS_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>

            <label className="space-y-2">
              <span className="text-sm text-white/70">
                Specific question (optional)
              </span>
              <Textarea
                rows={2}
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="e.g. Why did conversions drop last week?"
                className="bg-white resize-none border-white/10 text-cosmic"
              />
            </label>

            <label className="flex items-center gap-2 text-sm text-white/70">
              <input
                type="checkbox"
                checked={useManual}
                onChange={(e) => setUseManual(e.target.checked)}
                className="accent-neonBlue"
              />
              Enter metrics manually (otherwise uses stored campaign metrics)
            </label>

            {useManual ? (
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {METRIC_FIELDS.map((field) => (
                  <label key={field.key} className="space-y-1">
                    <span className="text-xs text-white/55">{field.label}</span>
                    <Input
                      type="number"
                      value={metrics[field.key] ?? ""}
                      onChange={(e) =>
                        setMetrics((current) => ({
                          ...current,
                          [field.key]: e.target.value,
                        }))
                      }
                      className="bg-white border-white/10 text-cosmic"
                    />
                  </label>
                ))}
              </div>
            ) : null}
          </div>

          <div className="mt-5">
            <Button
              type="button"
              disabled={isGenerating}
              className="bg-neonBlue text-cosmic hover:bg-neonBlue/90"
              onClick={handleRun}
            >
              {isGenerating ? (
                <span className="flex items-center gap-2">
                  <Loader2 className="size-4 animate-spin" />
                  Analyzing…
                </span>
              ) : (
                "Run analysis"
              )}
            </Button>
          </div>
        </div>

        <section className={`${PANEL_CLASS} p-5`}>
          <p className="text-xs uppercase tracking-[0.16em] text-white/40">
            How it works
          </p>
          <div className={`mt-4 p-4 ${SUBPANEL_CLASS}`}>
            <p className="text-sm leading-6 text-white/75">
              The agent structures every answer into Key Findings, Areas of
              Concern, What's Working, Recommendations, and Predicted Impact.
            </p>
          </div>
          <p className="mt-4 text-xs text-white/50">
            Tip: you can also ask follow-up questions in the chat panel on the
            right.
          </p>
        </section>
      </section>

      {hasChatHistory ? (
        <div className="rounded-md border border-white/10 bg-[#0D1018] p-4 text-sm leading-6 text-white/80">
          <div className="space-y-3 overflow-y-auto max-h-96">
            {visibleMessages.map((message, index) => (
              <div
                key={`${message.role}-${index}`}
                className={`rounded-md px-3 py-2 ${
                  message.role === "user"
                    ? "ml-auto max-w-[88%] bg-neonBlue text-cosmic"
                    : "mr-auto max-w-full bg-white/[0.06] text-white/85"
                }`}
              >
                <p className="break-words whitespace-pre-wrap">{message.text}</p>
              </div>
            ))}
            {isGenerating ? (
              <p className="flex items-center gap-2 text-sm text-white/60">
                <Loader2 className="size-4 animate-spin" />
                Analytics agent working…
              </p>
            ) : null}
          </div>
        </div>
      ) : isGenerating ? (
        <p className="flex items-center gap-2 text-sm text-white/60">
          <Loader2 className="size-4 animate-spin" />
          Analytics agent working…
        </p>
      ) : lastResult?.response ? (
        <div className="rounded-md border border-white/10 bg-[#0D1018] p-4 text-sm leading-6 text-white/80">
          <p className="whitespace-pre-wrap">{lastResult.response}</p>
        </div>
      ) : null}
    </div>
  );
}
