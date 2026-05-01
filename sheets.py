import aiohttp
import json
import logging
from datetime import date

import config

logger = logging.getLogger(__name__)

GVIZ_URL = (
    f"https://docs.google.com/spreadsheets/d/{config.SPREADSHEET_ID}"
    f"/gviz/tq?tqx=out:json&gid={config.SHEET_GID}&range=A:J&headers=1"
)


def _parse_date(v) -> str:
    """Parse Date(yyyy,m,d) → 'yyyy-mm-dd'"""
    if not v:
        return ""
    if isinstance(v, str) and v.startswith("Date("):
        parts = v.replace("Date(", "").replace(")", "").split(",")
        try:
            d = date(int(parts[0]), int(parts[1]) + 1, int(parts[2]))
            return d.isoformat()
        except Exception:
            return ""
    return ""


def _clean(v) -> str:
    if not v:
        return ""
    s = str(v).strip()
    return "" if s in ("—", "-", "\u2014") else s


async def fetch_events() -> list[dict]:
    async with aiohttp.ClientSession() as session:
        async with session.get(GVIZ_URL) as resp:
            text = await resp.text()

    # Strip gviz wrapper: /*O_o*/\ngoogle.visualization.Query.setResponse({...});
    start = text.find("{")
    end = text.rfind("}") + 1
    data = json.loads(text[start:end])

    rows = data.get("table", {}).get("rows", [])
    events = []

    for row in rows:
        cols = row.get("c", [])
        while len(cols) < 10:
            cols.append(None)

        # A=0=id, B=1=date_start, C=2=date_end, D=3=time_start,
        # E=4=time_end, F=5=tz, G=6=month, H=7=title, I=8=resp, J=9=format
        ev_id    = _clean(cols[0]["v"] if cols[0] else "")
        date_start = _parse_date(cols[1]["v"] if cols[1] else "")
        date_end   = _parse_date(cols[2]["v"] if cols[2] else "") or date_start
        time_start = _clean(cols[3]["v"] if cols[3] else "")
        time_end   = _clean(cols[4]["v"] if cols[4] else "")
        tz         = _clean(cols[5]["v"] if cols[5] else "")
        title      = _clean(cols[7]["v"] if cols[7] else "")
        responsible = _clean(cols[8]["v"] if cols[8] else "")
        fmt        = _clean(cols[9]["v"] if cols[9] else "")

        if not ev_id or not date_start or not title:
            continue

        events.append({
            "id": ev_id,
            "date_start": date_start,
            "date_end": date_end,
            "time_start": time_start,
            "time_end": time_end,
            "timezone": tz,
            "title": title,
            "responsible": responsible,
            "format": fmt,
        })

    logger.info(f"Fetched {len(events)} events")
    return events


def events_to_text(events: list[dict]) -> str:
    """Compact text for AI context."""
    lines = ["Актуальное расписание мероприятий:\n"]
    for e in events:
        date_str = e["date_start"]
        if e["date_end"] and e["date_end"] != e["date_start"]:
            date_str += f"–{e['date_end']}"
        time_str = e["time_start"]
        if e["time_end"]:
            time_str += f"–{e['time_end']}"
        if e["timezone"]:
            time_str += f" {e['timezone']}"
        parts = [f"[{e['id']}] {date_str} | {e['title']}"]
        if time_str:
            parts.append(f"Время: {time_str}")
        if e["responsible"]:
            parts.append(f"Отв: {e['responsible']}")
        if e["format"]:
            parts.append(f"Формат: {e['format']}")
        lines.append(" | ".join(parts))
    return "\n".join(lines)
