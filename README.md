# ai-weight-plan

Сайт с планом питания и недельными отчётами. Публикуется на GitHub Pages из папки `site/`.

- `site/index.html`, `site/app.js` — страница с графиком веса и отчётами
- `site/plan.md` — текущий план (обновляется по итогам недельного разбора)
- `site/data/weights.csv` — ежедневный вес (`date,weight_kg,note`)
- `site/data/weeks.json` — список недель
- `site/reports/week-NN.md` — отчёт за неделю: анализ и что изменилось в плане
- `site/menus/week-NN.json` — меню на неделю (из него события попадают в Google Calendar)

Сырые `.fit`-файлы в репозиторий не добавляются (содержат GPS-маршруты). Публикуются только сводки.

Публикация: Settings → Pages → Source: GitHub Actions. Workflow `.github/workflows/pages.yml` запускается при каждом пуше в `main`.

## Для агентов (OpenCode и др.)

Контекст, правила и порядок работы — в [`AGENTS.md`](AGENTS.md). Конфиг OpenCode — `opencode.json`, команды — `.opencode/command/` (`/log-weight`, `/ingest-fit`, `/weekly-review`). Скрипты: `scripts/weekly_stats.py`, `scripts/summarize_fit.py` (запасной вариант для `.fit`, если Coros недоступен; нужен `pip install fitparse`).
