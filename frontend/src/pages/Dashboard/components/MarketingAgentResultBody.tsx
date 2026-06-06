import type { MarketingAgentResponse } from "../../../types/api";
import { StrategyText } from "./StrategyText";
import { PANEL_CLASS } from "../constants";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../../../components/ui/table";

function isBudgetTable(
  value: MarketingAgentResponse["budget_allocation"]
): value is Record<string, { ads: number; content: number }> {
  return (
    !!value &&
    typeof value === "object" &&
    !Array.isArray(value) &&
    typeof value !== "string"
  );
}

export function MarketingAgentResultBody({
  result,
}: {
  result: MarketingAgentResponse;
}) {
  if (result.error_message) {
    return <p className="text-sm text-red-300">{result.error_message}</p>;
  }

  const financials = result.financial_model ?? {};
  const strategyFailed = result.strategy?.startsWith("Strategy generation failed:");

  if (strategyFailed) {
    return <p className="text-sm text-red-300">{result.strategy}</p>;
  }

  const metricCards = [
    { label: "Estimated Clicks", value: financials["Estimated Clicks"] },
    { label: "Estimated Sales", value: financials["Estimated Sales"] },
    { label: "Estimated Revenue", value: financials["Estimated Revenue"] },
    { label: "CPA", value: financials["CPA"] },
    { label: "ROAS", value: financials["ROAS"] },
  ];

  return (
    <div className="space-y-4 text-sm text-white/85">
      {result.competitor_insight ? (
        <div className={`${PANEL_CLASS} p-4`}>
          <p className="text-xs uppercase tracking-[0.16em] text-white/40">
            Competitor insight
          </p>
          <p className="mt-2 leading-6">{result.competitor_insight}</p>
        </div>
      ) : null}

      {result.platform_insight ? (
        <div className={`${PANEL_CLASS} p-4`}>
          <p className="text-xs uppercase tracking-[0.16em] text-white/40">
            Platform insight
          </p>
          <p className="mt-2 leading-6">{result.platform_insight}</p>
        </div>
      ) : null}

      {result.decision ? (
        <div className="rounded-md border border-neonBlue/40 bg-neonBlue/10 px-4 py-3">
          <p className="text-xs uppercase tracking-[0.16em] text-neonBlue">
            Decision
          </p>
          <p className="mt-2 leading-6 text-white/90">{result.decision}</p>
        </div>
      ) : null}

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
        {metricCards.map((metric) => (
          <div key={metric.label} className={`${PANEL_CLASS} px-4 py-3`}>
            <p className="text-xs uppercase tracking-[0.16em] text-white/45">
              {metric.label}
            </p>
            <p className="mt-2 text-2xl font-semibold text-white">
              {metric.value === undefined || metric.value === null
                ? "-"
                : String(metric.value)}
            </p>
          </div>
        ))}
      </div>

      {isBudgetTable(result.budget_allocation) ? (
        <div className={`overflow-hidden ${PANEL_CLASS}`}>
          <p className="border-b border-white/10 px-4 py-3 text-xs uppercase tracking-[0.16em] text-white/40">
            Budget allocation
          </p>
          <Table className="min-w-[480px] text-white">
            <TableHeader>
              <TableRow className="border-white/10 hover:bg-transparent">
                <TableHead className="px-4 text-white/55">Platform</TableHead>
                <TableHead className="px-4 text-white/55">Ads</TableHead>
                <TableHead className="px-4 text-white/55">Content</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {Object.entries(result.budget_allocation).map(([platform, split]) => (
                <TableRow
                  key={platform}
                  className="border-white/10 hover:bg-white/[0.03]"
                >
                  <TableCell className="px-4 font-medium text-white/90">
                    {platform}
                  </TableCell>
                  <TableCell className="px-4 text-white/70">
                    ${split.ads.toLocaleString("en-US")}
                  </TableCell>
                  <TableCell className="px-4 text-white/70">
                    ${split.content.toLocaleString("en-US")}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      ) : null}

      {result.strategy ? (
        <div className={`max-h-[28rem] overflow-y-auto ${PANEL_CLASS} p-4`}>
          <p className="text-xs uppercase tracking-[0.16em] text-white/40">
            Strategy
          </p>
          <div className="mt-3">
            <StrategyText text={result.strategy} />
          </div>
        </div>
      ) : null}
    </div>
  );
}
