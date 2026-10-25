---
description: Добавить тренировки в site/data/workouts.csv из Coros (аргумент: даты; запасной вариант — путь к .fit)
---

Прочитай AGENTS.md (разделы 2 и 6). Аргументы команды: $ARGUMENTS

1. Основной путь: получи активности за период (по аргументу, иначе за последние 7 дней) из коннектора Coros через `querySportRecords`, детали и пульс — `getActivityDetail`, `queryActivityLapData`. `.fit` для этого не нужен.
   Запасной путь, только если Coros недоступен (ошибка и после повторной попытки) или в аргументах путь к `.fit`: `python3 -I scripts/summarize_fit.py <путь> --csv`.
2. Строку из вывода (`date,sport,duration_min,distance_km,avg_hr,max_hr,kcal_watch,note`) добавь в `site/data/workouts.csv`, если такой даты и вида спорта там ещё нет. Дубли не создавай.
3. Никогда не коммить `.fit` и координаты. Проверь `git status`: в индексе только CSV.
4. Закоммить: `Workout YYYY-MM-DD: <вид>, <время> мин` и запушь в `main`.
5. Кратко сообщи пользователю: вид, время, дистанция, средний пульс.
