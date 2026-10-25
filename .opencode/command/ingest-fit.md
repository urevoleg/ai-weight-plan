---
description: Добавить тренировку в site/data/workouts.csv из .fit-файла или из Coros (аргумент: путь к .fit или даты)
---

Прочитай AGENTS.md (разделы 2 и 6). Аргументы команды: $ARGUMENTS

1. Если в аргументах путь к `.fit` — выполни `python3 -I scripts/summarize_fit.py <путь> --csv`. Если даты или аргументов нет и доступен MCP Coros — получи активности за период через `querySportRecords` и, при необходимости, `downloadActivityFitFiles` во временную папку `inbox/`.
2. Строку из вывода (`date,sport,duration_min,distance_km,avg_hr,max_hr,kcal_watch,note`) добавь в `site/data/workouts.csv`, если такой даты и вида спорта там ещё нет. Дубли не создавай.
3. Никогда не коммить `.fit` и координаты. Проверь `git status`: в индексе только CSV.
4. Закоммить: `Workout YYYY-MM-DD: <вид>, <время> мин` и запушь в `main`.
5. Кратко сообщи пользователю: вид, время, дистанция, средний пульс.
