/** Strip markdown noise and render strategy as readable plain text. */
export function plainStrategyText(raw: string): string {
  return raw
    .replace(/\r\n/g, "\n")
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/\*\*([^*]+)\*\*/g, "$1")
    .replace(/\*([^*]+)\*/g, "$1")
    .replace(/__([^_]+)__/g, "$1")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/^---+$/gm, "")
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/\|/g, " · ")
    .replace(/[ \t]+\n/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

export function StrategyText({ text }: { text: string }) {
  const cleaned = plainStrategyText(text);
  const blocks = cleaned.split(/\n\n+/);

  return (
    <div className="space-y-4">
      {blocks.map((block, index) => {
        const lines = block.split("\n").filter(Boolean);
        const first = lines[0] ?? "";
        const isSection =
          /^\d+\.\s/.test(first) ||
          (/^[A-Z]/.test(first.trim()) &&
            !first.includes("·") &&
            first.length < 80 &&
            lines.length === 1);

        if (isSection && lines.length === 1) {
          return (
            <h3
              key={`${index}-${first.slice(0, 24)}`}
              className="text-base font-semibold text-white"
            >
              {first}
            </h3>
          );
        }

        return (
          <div
            key={`${index}-${first.slice(0, 24)}`}
            className="space-y-1.5 text-sm leading-7 text-white/85"
          >
            {lines.map((line, lineIndex) => (
              <p key={`${index}-${lineIndex}`}>{line}</p>
            ))}
          </div>
        );
      })}
    </div>
  );
}
