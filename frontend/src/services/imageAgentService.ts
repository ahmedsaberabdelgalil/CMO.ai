import { request } from "../lib/api";
import { pollJob, startJob } from "./jobsService";
import type {
  ImageAgentRequest,
  ImageAgentResponse,
  ImageAgentStatus,
} from "../types/api";

export async function getImageAgentStatus(): Promise<ImageAgentStatus> {
  return request<ImageAgentStatus>("/agents/image/status", {
    method: "GET",
  });
}

export async function generateImage(
  data: ImageAgentRequest
): Promise<ImageAgentResponse> {
  return request<ImageAgentResponse>("/agents/image/generate", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function generateImageAsync(
  data: ImageAgentRequest
): Promise<ImageAgentResponse> {
  const { job_id } = await startJob("/agents/image/generate-async", data);
  return pollJob<ImageAgentResponse>(job_id);
}
