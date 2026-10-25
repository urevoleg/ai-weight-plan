#!/usr/bin/env python3
"""Список закупок из меню недели (site/menus/week-NN.json).

Использование:
    python3 scripts/shopping_list.py site/menus/week-NN.json > site/menus/week-NN-shopping.md

Суммирует граммы и штуки по простым позициям меню («Гречка варёная 150 г»,
«Яблоко 1 шт.»). Составные блюда («Тыквенная каша: тыква 150 г + ...», «Салат ...: огурец, ...»)
и строки без веса печатаются в разделе «Не разобрано» и закупаются вручную.
Веса — как в меню: круп, риса и гарниров — в готовом (варёном) виде.
Для закупки сухих круп пересчитать: гречка ×0,3, басмати и бурый рис ×0,35, овсянка — как есть.
"""
import json
import math
import re
import sys
from collections import defaultdict

PAT = re.compile(r"^(?P<name>.+?)\s+(?P<num>\d+(?:[.,]\d+)?)\s*(?P<unit>г|шт\.?)$")
PERCENT = re.compile(r"\s+\d+(?:[.,]\d+)?\s*%$")
STATE = re.compile(r"\s+(варёная|варёный|варёные|запечённая|запечённый|тушёные|тушёный|вкрутую|в соку|консервированный)\b.*$", re.I)
CATS = [
    ("Рыба и тунец", ["треска", "хек", "лосось", "тунец"]),
    ("Молочное и яйца", ["творог", "кефир", "йогурт", "яйц", "молоко", "сыр", "брынза"]),
    ("Крупы и хлеб", ["гречка", "басмати", "рис", "овсян", "хлеб", "чечевица", "мука"]),
    ("Овощи и фрукты", ["огурец", "помидор", "банан", "яблоко", "груша", "ягод", "финик", "овощ", "тыква", "лимон", "авокадо", "листовой", "картофель", "груша"]),
    ("Орехи, мёд и прочее", ["миндаль", "орех", "мёд", "мед", "магуро"]),
]


def parse(item):
    text = item.strip()
    if ":" in text or "+" in text:
        return None
    m = PAT.match(text)
    if not m:
        return None
    name = PERCENT.sub("", m["name"]).strip()
    name = STATE.sub("", name).strip()
    return name, float(m["num"].replace(",", ".")), m["unit"].rstrip(".")


def category(key):
    for title, words in CATS:
        if any(w in key for w in words):
            return title
    return "Прочее"


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    total, label, unparsed = defaultdict(float), {}, set()
    for day in data["days"]:
        for meal in day["meals"]:
            for item in meal["items"]:
                parsed = parse(item)
                if not parsed:
                    unparsed.add(item)
                    continue
                name, num, unit = parsed
                key = name.lower()
                total[key] += num
                label[key] = (name, unit)
    groups = defaultdict(list)
    for key in total:
        name, unit = label[key]
        if "магуро" in key:
            line = f"- Салат Магуро с тунцом (банка 230 г): {round(total[key] / 230)} шт."
        elif unit == "шт":
            line = f"- {name}: {total[key]:g} шт."
        else:
            line = f"- {name}: {total[key]:g} г"
        groups[category(key)].append((name.lower(), line))
    print(f"# Закупки на неделю {data.get('week', '?')} (с {data.get('start', '?')})\n")
    print("Веса — как в меню (готовые). Сухие крупы пересчитать вручную.\n")
    for title, _ in CATS + [("Прочее", [])]:
        if groups.get(title):
            print(f"## {title}")
            for _, line in sorted(groups[title]):
                print(line)
            print()
    if unparsed:
        print("## Не разобрано (закупить вручную по рецепту)")
        for item in sorted(unparsed):
            print(f"- {item}")


if __name__ == "__main__":
    main()
