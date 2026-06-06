import { Loader2 } from "lucide-react";
import type { ChannelBreakdown, ContentCalendarMap } from "../../../types/api";
import { PANEL_CLASS } from "../constants";
import { ActionRow } from "../components/ActionRow";
import { CalendarContentBody } from "../components/CalendarContentBody";

export function CalendarPanels({
  calendarData,
  calendarMessage,
  channelsView,
  busyAction,
  onGenerate14,
  onBalance,
  onFindGaps,
}: {
  calendarData: ContentCalendarMap | null;
  calendarMessage: string | null;
  channelsView: ChannelBreakdown[] | null;
  busyAction: string | null;
  onGenerate14: () => void;
  onBalance: () => void;
  onFindGaps: () => void;
}) {
  const isLoading =
    busyAction === "cal14" ||
    busyAction === "channels" ||
    busyAction === "calgaps";

  return (
    <div className="grid gap-5 2xl:grid-cols-[minmax(0,1fr)_320px]">
      <section className={`${PANEL_CLASS} p-5`}>
        <h2 className="text-2xl font-semibold">Market Calendar</h2>
        <p className="mt-2 text-sm text-white/50">
          Content schedule from GET /api/v1/content-calendar/calendar
        </p>

        {isLoading ? (
          <p className="mt-4 flex items-center gap-2 text-sm text-white/60">
            <Loader2 className="size-4 animate-spin" />
            Loading calendar data…
          </p>
        ) : (
          <div className="mt-4">
            <CalendarContentBody
              calendarData={calendarData}
              channelsView={channelsView}
              calendarMessage={calendarMessage}
            />
          </div>
        )}
      </section>

      <section className={`${PANEL_CLASS} p-5`}>
        <p className="text-xs uppercase tracking-[0.16em] text-white/40">
          Current focus
        </p>
        <div className="mt-4 grid gap-2">
          <ActionRow
            label="Load calendar"
            loading={busyAction === "cal14"}
            onClick={onGenerate14}
          />
          <ActionRow
            label="Balance channels"
            loading={busyAction === "channels"}
            onClick={onBalance}
          />
          <ActionRow
            label="Find calendar gaps"
            loading={busyAction === "calgaps"}
            onClick={onFindGaps}
          />
        </div>
        <p className="mt-4 text-xs leading-5 text-white/45">
          Your marketing plan seeds 14 days of posts automatically. Use Load
          calendar to view scheduled content for this month.
        </p>
      </section>
    </div>
  );
}
