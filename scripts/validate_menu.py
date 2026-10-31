#!/usr/bin/env python3
"""Проверка недельных меню перед публикацией."""

import json
import re
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path


MEALS = {"breakfast", "snack", "lunch", "afternoon", "dinner"}
FORBIDDEN = re.compile(r"мяс|куриц|говядин|свинин|индей|тофу|бур(?:ый|ого) рис", re.I)
FISH = re.compile(r"треск|минтай|хек|лосос|форел|тунец", re.I)
MAGURO = re.compile(r"магуро", re.I)


def validate(data):
    errors = []
    days = data.get("days", [])
    if len(days) != 7:
        errors.append(f"нужно 7 дней, найдено {len(days)}")
        return errors

    try:
        dates = [date.fromisoformat(day["date"]) for day in days]
    except (KeyError, ValueError) as exc:
        return [f"некорректная дата: {exc}"]

    if data.get("start") != dates[0].isoformat():
        errors.append("поле start не совпадает с первым днём")
    if dates[0].weekday() != 6:
        errors.append("неделя должна начинаться в воскресенье")
    for previous, current in zip(dates, dates[1:]):
        if current != previous + timedelta(days=1):
            errors.append(f"даты не последовательны: {previous} → {current}")

    regular_fish = 0
    maguro = 0
    dinners = Counter()
    for day in days:
        meals = day.get("meals", [])
        if day.get("kcal_target") is None and "без плана" in day.get("type", ""):
            if meals:
                errors.append(f"{day['date']}: день без плана должен быть пустым")
            continue

        meal_names = [meal.get("meal") for meal in meals]
        if len(meals) != 5 or set(meal_names) != MEALS:
            errors.append(f"{day['date']}: нужны пять уникальных приёмов пищи")
            continue

        total = sum(meal.get("kcal", 0) for meal in meals)
        total += day.get("run_fuel", {}).get("kcal", 0)
        target = day.get("kcal_target")
        if not isinstance(target, (int, float)) or abs(total - target) > 100:
            errors.append(f"{day['date']}: {total} ккал вне допуска ±100 от цели {target}")

        dinner = next(meal for meal in meals if meal["meal"] == "dinner")
        recorded_total = dinner.get("day_total_kcal")
        if recorded_total != total:
            errors.append(f"{day['date']}: day_total_kcal={recorded_total}, сумма={total}")
        if dinner.get("day_protein_g", 0) < 140:
            errors.append(f"{day['date']}: белок ниже 140 г")
        if dinner.get("items"):
            dinners[dinner["items"][0].strip().lower()] += 1

        for meal in meals:
            text = " ".join(meal.get("items", []))
            if FORBIDDEN.search(text):
                errors.append(f"{day['date']}: запрещённый продукт в {meal['meal']}")
            if MAGURO.search(text):
                maguro += 1
            elif FISH.search(text):
                regular_fish += 1

    if not 2 <= regular_fish <= 3:
        errors.append(f"обычных рыбных приёмов должно быть 2–3, найдено {regular_fish}")
    if not 3 <= maguro <= 4:
        errors.append(f"приёмов с Магуро должно быть 3–4, найдено {maguro}")
    for dinner, count in dinners.items():
        if count > 2:
            errors.append(f"ужин повторяется {count} раз: {dinner}")
    return errors


def validate_file(path):
    return validate(json.loads(Path(path).read_text(encoding="utf-8")))


def main():
    paths = [Path(arg) for arg in sys.argv[1:]]
    if not paths:
        paths = sorted(Path("site/menus").glob("week-*.json"))
    failed = False
    for path in paths:
        errors = validate_file(path)
        if errors:
            failed = True
            print(f"{path}:")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"{path}: OK")
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
