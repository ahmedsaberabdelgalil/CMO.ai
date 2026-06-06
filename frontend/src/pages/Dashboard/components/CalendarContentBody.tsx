import type { ChannelBreakdown, ContentCalendarMap } from "../../../types/api";
import { PANEL_CLASS } from "../constants";

export function CalendarContentBody({
  calendarData,
  channelsView,
  calendarMessage,
}: {
  calendarData: ContentCalendarMap | null;
  channelsView: ChannelBreakdown[] | null;
  calendarMessage: string | null;
}) {
  if (calendarMessage) {
    return (
      <p className="rounded-md border border-amber-400/30 bg-amber-400/10 px-4 py-3 text-sm text-amber-100">
        {calendarMessage}
      </p>
    );
  }

  if (calendarData && Object.keys(calendarData).length > 0) {
    return (
      <div className={`max-h-[40rem] space-y-4 overflow-y-auto ${PANEL_CLASS} p-4`}>
        <p className="text-xs uppercase tracking-[0.16em] text-white/40">
          Scheduled content
        </p>
        {Object.entries(calendarData)
          .sort(([a], [b]) => a.localeCompare(b))
          .map(([date, items]) => (
            <div key={date} className="border-b border-white/10 pb-4 last:border-0">
              <p className="font-semibold text-neonBlue">{date}</p>
              <ul className="mt-2 space-y-2">
                {items.map((item) => (
                  <li
                    key={item.id}
                    className="rounded-md border border-white/10 bg-[#090A0F] px-3 py-2 text-sm text-white/75"
                  >
                    <p className="font-medium text-white/90">{item.title}</p>
                    <p className="text-xs text-white/50">
                      {item.platform} · {item.content_type} · {item.status}
                    </p>
                    {item.body_text ? (
                      <p className="mt-1 line-clamp-2 text-white/60">
                        {item.body_text}
                      </p>
                    ) : null}
                  </li>
                ))}
              </ul>
            </div>
          ))}
      </div>
    );
  }

  if (channelsView && channelsView.length > 0) {
    return (
      <div className={`space-y-3 ${PANEL_CLASS} p-4`}>
        <p className="text-xs uppercase tracking-[0.16em] text-white/40">
          Channel breakdown
        </p>
        {channelsView.map((row) => (
          <div
            key={row.platform}
            className="rounded-md border border-white/10 bg-[#090A0F] px-3 py-2 text-sm text-white/75"
          >
            <span className="font-medium text-white/90">{row.platform}</span>
            <span className="text-white/50">
              {" "}
              — reach {row.total_reach.toLocaleString()}, clicks{" "}
              {row.total_clicks.toLocaleString()}
            </span>
          </div>
        ))}
      </div>
    );
  }

  return (
    <p className="text-sm text-white/70">
      Load scheduled posts with Generate next 14 days, or review channel
      performance with Balance channels. The AI calendar gap agent is coming
      soon.
    </p>
  );
}
