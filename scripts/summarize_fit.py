#!/usr/bin/env python3
"""Сводка тренировок из .fit без GPS и без сырых записей.

Зависимость: pip install fitparse

Использование:
    python3 -I scripts/summarize_fit.py файл1.fit [файл2.fit ...] [--csv]

Без --csv печатает JSON по каждому файлу. С --csv печатает строки для
site/data/workouts.csv: date,sport,duration_min,distance_km,avg_hr,max_hr,kcal_watch,note

Координаты, маршруты и точное время старта в вывод не попадают: только дата
в часовом поясе Europe/Moscow и итоговые показатели сессии.
"""
import json
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

try:
    from fitparse import FitFile
except ImportError:  # pragma: no cover
    sys.exit("Нужна библиотека fitparse: pip install fitparse")

TZ = ZoneInfo("Europe/Moscow")


def summarize(path: Path) -> dict:
    ff = FitFile(str(path))
    sessions = list(ff.get_messages("session"))
    if not sessions:
        raise ValueError(f"{path.name}: в файле нет сообщения session")
    # Мультиспорт: суммируем время/дистанцию, пульс берём по максимуму/средневзвешенно
    total_time = 0.0
    total_dist = 0.0
    kcal = 0.0
    hr_weighted = 0.0
    hr_time = 0.0
    max_hr = None
    sport = None
    start = None
    for s in sessions:
        v = {f.name: f.value for f in s}
        t = v.get("total_timer_time") or v.get("total_elapsed_time") or 0
        total_time += t
        total_dist += v.get("total_distance") or 0
        kcal += v.get("total_calories") or 0
        if v.get("avg_heart_rate"):
            hr_weighted += v["avg_heart_rate"] * t
            hr_time += t
        if v.get("max_heart_rate"):
            max_hr = max(max_hr or 0, v["max_heart_rate"])
        sport = sport or v.get("sport")
        st = v.get("start_time")
        if st and (start is None or st < start):
            start = st
    if start is None:
        raise ValueError(f"{path.name}: нет start_time")
    if start.tzinfo is None:
        from datetime import timezone
        start = start.replace(tzinfo=timezone.utc)
    local_date = start.astimezone(TZ).date().isoformat()
    return {
        "file": path.name,
        "date": local_date,
        "sport": str(sport) if sport else "unknown",
        "duration_min": round(total_time / 60, 1),
        "distance_km": round(total_dist / 1000, 2),
        "avg_hr": round(hr_weighted / hr_time) if hr_time else None,
        "max_hr": max_hr,
        "kcal_watch": round(kcal) if kcal else None,
    }


def csv_row(d: dict) -> str:
    def f(x):
        return "" if x is None else str(x)
    return ",".join([d["date"], d["sport"], f(d["duration_min"]), f(d["distance_km"]),
                     f(d["avg_hr"]), f(d["max_hr"]), f(d["kcal_watch"]), ""])


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_csv = "--csv" in sys.argv
    if not args:
        sys.exit(__doc__)
    out = []
    for a in args:
        try:
            out.append(summarize(Path(a)))
        except Exception as e:  # продолжаем по остальным файлам
            print(f"# ошибка: {e}", file=sys.stderr)
    out.sort(key=lambda d: d["date"])
    for d in out:
        print(csv_row(d) if as_csv else json.dumps(d, ensure_ascii=False))


if __name__ == "__main__":
    main()
