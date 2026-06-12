import { request } from "../lib/api";
import type {
  OrchestratorAgentRequest,
  OrchestratorAgentResponse,
} from "../types/api";

export async function orchestrate(
  data: OrchestratorAgentRequest,
): Promise<OrchestratorAgentResponse> {
  return request<OrchestratorAgentResponse>("/agents/orchestrator/generate", {
    method: "POST",
    body: JSON.stringify(data),
  });
}
