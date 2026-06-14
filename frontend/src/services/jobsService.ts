import { request } from "../lib/api";

export interface JobState<T> {
  job_id: string;
  kind: string;
  status: "pending" | "running" | "succeeded" | "failed";
  result: T | null;
  error: string | null;
}

export async function getJob<T>(jobId: string): Promise<JobState<T>> {
  return request<JobState<T>>(`/jobs/${jobId}`, { method: "GET" });
}

/**
 * Poll a background job until it finishes. Returns the job result on success,
 * throws on failure or timeout.
 */
export async function pollJob<T>(
  jobId: string,
  { intervalMs = 2500, timeoutMs = 240000 }: { intervalMs?: number; timeoutMs?: number } = {},
): Promise<T> {
  const deadline = Date.now() + timeoutMs;
  // small initial delay so very fast jobs are caught on first poll
  await new Promise((r) => setTimeout(r, 600));

  while (Date.now() < deadline) {
    const state = await getJob<T>(jobId);
    if (state.status === "succeeded") {
      if (state.result == null) {
        throw new Error("Job finished but returned no result.");
      }
      return state.result;
    }
    if (state.status === "failed") {
      throw new Error(state.error || "Background job failed.");
    }
    await new Promise((r) => setTimeout(r, intervalMs));
  }
  throw new Error("Generation timed out. Please try again.");
}

export async function startJob(
  endpoint: string,
  body: unknown,
): Promise<{ job_id: string; status: string }> {
  return request<{ job_id: string; status: string }>(endpoint, {
    method: "POST",
    body: JSON.stringify(body),
  });
}
