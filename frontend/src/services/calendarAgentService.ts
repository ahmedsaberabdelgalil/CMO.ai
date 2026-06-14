import { request } from "../lib/api";
import type {
  CalendarAgentRequest,
  CalendarAgentResponse,
  CalendarApplyRequest,
  CalendarApplyResponse,
} from "../types/api";

export async function generateCalendarInsight(
  data: CalendarAgentRequest,
): Promise<CalendarAgentResponse> {
  return request<CalendarAgentResponse>("/agents/calendar/generate", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function applyCalendarPlan(
  data: CalendarApplyRequest,
): Promise<CalendarApplyResponse> {
  return request<CalendarApplyResponse>("/agents/calendar/apply", {
    method: "POST",
    body: JSON.stringify(data),
  });
}
