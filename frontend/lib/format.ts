export function formatDate(iso: string, lang: "hi" | "en" = "en"): string {
  try {
    const d = new Date(iso);
    return new Intl.DateTimeFormat(lang === "hi" ? "hi-IN" : "en-IN", {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(d);
  } catch {
    return iso;
  }
}

export function timeAgo(iso: string, lang: "hi" | "en" = "en"): string {
  const seconds = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000);
  const units: [number, string, string][] = [
    [60, "s", "से"],
    [60, "m", "मि"],
    [24, "h", "घं"],
    [7, "d", "दिन"],
  ];
  let unitIndex = 0;
  let value = seconds;
  while (unitIndex < units.length && value >= units[unitIndex][0]) {
    value = value / units[unitIndex][0];
    unitIndex++;
  }
  const v = Math.max(1, Math.floor(value));
  const suffixEn = ["s", "m", "h", "d", "w"][unitIndex] || "w";
  const suffixHi = ["से", "मि", "घं", "दिन", "सप्ताह"][unitIndex] || "सप्ताह";
  return lang === "hi" ? `${v} ${suffixHi} पहले` : `${v}${suffixEn} ago`;
}
