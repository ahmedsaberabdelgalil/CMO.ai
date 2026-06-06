import { request } from "../lib/api";
import type {
  MarketingAgentRequest,
  MarketingAgentResponse,
} from "../types/api";

export async function generateMarketingStrategy(
  data: MarketingAgentRequest
): Promise<MarketingAgentResponse> {
  return request<MarketingAgentResponse>("/agents/marketing/generate", {
    method: "POST",
    body: JSON.stringify(data),
  });
}
