import { request } from "../lib/api";
import type {
  BrandAgentRequest,
  BrandAgentResponse,
  BrandSaveResponse,
} from "../types/api";

export async function generateBrandCoaching(
  data: BrandAgentRequest,
): Promise<BrandAgentResponse> {
  return request<BrandAgentResponse>("/agents/brand/generate", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function generateBrandReport(
  data: BrandAgentRequest,
): Promise<BrandAgentResponse> {
  return request<BrandAgentResponse>("/agents/brand/report", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function saveBrandProfile(
  data: BrandAgentRequest,
): Promise<BrandSaveResponse> {
  return request<BrandSaveResponse>("/agents/brand/save", {
    method: "POST",
    body: JSON.stringify(data),
  });
}
