import { request } from "../lib/api";
import type {
  CalendarAgentRequest,
  CalendarAgentResponse,
} from "../types/api";

export async function generateCalendarInsight(
  data: CalendarAgentRequest,
): Promise<CalendarAgentResponse> {
  return request<CalendarAgentResponse>("/agents/calendar/generate", {
    method: "POST",
    body: JSON.stringify(data),
  });
}
