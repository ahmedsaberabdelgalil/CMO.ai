import { request } from "../lib/api";
import { pollJob, startJob } from "./jobsService";
import type { VideoAgentRequest, VideoAgentResponse } from "../types/api";

export async function generateVideo(
  data: VideoAgentRequest
): Promise<VideoAgentResponse> {
  return request<VideoAgentResponse>("/agents/video/generate", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function generateVideoAsync(
  data: VideoAgentRequest
): Promise<VideoAgentResponse> {
  const { job_id } = await startJob("/agents/video/generate-async", data);
  return pollJob<VideoAgentResponse>(job_id, { timeoutMs: 360000 });
}
