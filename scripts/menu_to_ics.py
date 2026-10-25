#!/usr/bin/env python3
"""Меню недели (site/menus/week-NN.json) -> файл .ics для импорта в календарь.

Использование:
    python3 scripts/menu_to_ics.py site/menus/week-02.json > site/menus/week-02.ics

Приёмы пищи: breakfast, snack, lunch, afternoon, dinner. Время по умолчанию
и эмодзи такие же, как в AGENTS.md (раздел 5.1). В JSON у приёма можно задать
свой "time": "HH:MM". Время считается московским (UTC+3, без перехода на летнее).
"""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

MEALS = {
    "breakfast": ("🍳", "Завтрак", "10:00"),
    "snack": ("🍎", "Перекус", "12:30"),
    "lunch": ("🍲", "Обед", "14:30"),
    "afternoon": ("🥪", "Полдник", "17:00"),
    "dinner": ("🐟", "Ужин", "20:00"),
}
MSK = timedelta(hours=3)
DURATION = timedelta(minutes=30)


def esc(text: str) -> str:
    text = text.replace("\\", "\\\\")
    for ch in (";", ","):
        text = text.replace(ch, "\\" + ch)
    return text.replace("\n", "\\n")


def fold(line: str) -> str:
    """Сворачивает строки длиннее 73 символов по правилам RFC 5545 (по символам)."""
    out, cur = [], ""
    for ch in line:
        if len((cur + ch).encode("utf-8")) > 73:
            out.append(cur)
            cur = " " + ch
        else:
            cur += ch
    out.append(cur)
    return "\r\n".join(out)


def stamp(dt: datetime) -> str:
    return dt.strftime("%Y%m%dT%H%M%SZ")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    path = Path(sys.argv[1])
    data = json.loads(path.read_text(encoding="utf-8"))
    week = data.get("week", "?")
    now = datetime.now(timezone.utc)
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//ai-weight-plan//menu//RU", "CALSCALE:GREGORIAN"]
    for day in data["days"]:
        for m in day["meals"]:
            emoji, title, default_time = MEALS[m["meal"]]
            hh, mm = (m.get("time") or default_time).split(":")
            start_local = datetime.fromisoformat(day["date"]).replace(hour=int(hh), minute=int(mm))
            start, end = start_local - MSK, start_local - MSK + DURATION
            desc = list(m["items"])
            if m["meal"] == "breakfast" and day.get("run_fuel"):
                desc.append(day["run_fuel"]["text"] + f" (≈ {day['run_fuel']['kcal']} ккал, входит в дневной итог)")
            if "day_total_kcal" in m:
                desc.append(f"Итого за день: {m['day_total_kcal']} ккал, белок {m.get('day_protein_g', '?')} г")
            desc.append(f"[ai-weight-plan week-{int(week):02d}]" if str(week).isdigit() else "[ai-weight-plan]")
            summary = f"{emoji} {title} · {m['kcal']} ккал"
            description = "\n".join(desc)
            lines += [
                "BEGIN:VEVENT",
                f"UID:{day['date']}-{m['meal']}@ai-weight-plan",
                f"DTSTAMP:{stamp(now)}",
                f"DTSTART:{stamp(start)}",
                f"DTEND:{stamp(end)}",
                fold("SUMMARY:" + esc(summary)),
                fold("DESCRIPTION:" + esc(description)),
                "TRANSP:TRANSPARENT",
                "END:VEVENT",
            ]
    lines.append("END:VCALENDAR")
    sys.stdout.write("\r\n".join(lines) + "\r\n")


if __name__ == "__main__":
    main()
