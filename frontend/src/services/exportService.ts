import { BASE_URL, getAuthHeaders } from "../lib/api";

async function downloadBlob(endpoint: string, init: RequestInit, fallbackName: string) {
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...init,
    headers: {
      ...(init.headers ?? {}),
      ...getAuthHeaders(),
    },
  });

  if (!response.ok) {
    let message = "Export failed";
    try {
      const body = await response.json();
      if (typeof body?.detail === "string") message = body.detail;
    } catch {
      // ignore non-JSON error bodies
    }
    throw new Error(message);
  }

  const blob = await response.blob();
  const disposition = response.headers.get("Content-Disposition") ?? "";
  const match = disposition.match(/filename=([^;]+)/);
  const filename = match ? match[1].trim() : fallbackName;

  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

export async function exportDocx(payload: {
  title: string;
  content: string;
  subtitle?: string;
  filename?: string;
}) {
  await downloadBlob(
    "/export/docx",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    },
    `${payload.filename ?? payload.title ?? "document"}.docx`,
  );
}

export async function exportMarketingPlan(campaignId: number, name = "marketing_plan") {
  await downloadBlob(
    `/export/marketing-plan/${campaignId}`,
    { method: "GET" },
    `${name}.docx`,
  );
}
