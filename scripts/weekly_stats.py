#!/usr/bin/env python3
"""Недельные средние веса из site/data/weights.csv (недели вс-сб).

Использование:
    python3 scripts/weekly_stats.py [путь/к/weights.csv]

Печатает таблицу в Markdown: неделя, число измерений, среднее, изменение к
предыдущей неделе, минимум и максимум. Для недель с менее чем 4 измерениями
в колонке «Заметка» стоит «мало данных»: решения по весу по такой неделе не принимаются.
"""
import csv
import sys
from datetime import date, timedelta
from pathlib import Path

DEFAULT = Path(__file__).resolve().parent.parent / "site" / "data" / "weights.csv"
MIN_POINTS = 4


def week_start(d: date) -> date:
    """Воскресенье, с которого начинается неделя вс–сб, куда входит дата d."""
    return d - timedelta(days=(d.weekday() + 1) % 7)


def load(path: Path):
    rows = []
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if not r.get("date") or not r.get("weight_kg"):
                continue
            if "исключ" in (r.get("note") or ""):
                continue
            rows.append((date.fromisoformat(r["date"]), float(r["weight_kg"])))
    rows.sort()
    return rows


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    rows = load(path)
    if not rows:
        print("Нет данных в", path)
        return
    weeks = {}
    for d, w in rows:
        weeks.setdefault(week_start(d), []).append(w)
    print("| Неделя с | Измерений | Среднее, кг | К прошлой, кг | Мин | Макс | Заметка |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    prev = None
    for start in sorted(weeks):
        ws = weeks[start]
        mean = sum(ws) / len(ws)
        ok = len(ws) >= MIN_POINTS
        delta = "" if prev is None else f"{mean - prev:+.2f}"
        note = "" if ok else "мало данных"
        print(f"| {start.isoformat()} | {len(ws)} | {mean:.2f} | {delta} | {min(ws):.1f} | {max(ws):.1f} | {note} |")
        if ok:
            prev = mean


if __name__ == "__main__":
    main()
