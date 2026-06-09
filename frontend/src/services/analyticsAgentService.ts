import { request } from "../lib/api";
import type {
  AnalyticsAgentRequest,
  AnalyticsAgentResponse,
} from "../types/api";

export async function generateAnalyticsInsight(
  data: AnalyticsAgentRequest,
): Promise<AnalyticsAgentResponse> {
  return request<AnalyticsAgentResponse>("/agents/analytics/generate", {
    method: "POST",
    body: JSON.stringify(data),
  });
}
