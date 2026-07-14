"""Live analytics for the Power BI dashboard (reads Excel history)."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta

from database import (
    ACTIVITY_PATH,
    CHANNELS,
    FILE_PATH,
    REGION_META,
    TRANSFERS_PATH,
    customer_count,
    list_activity,
    list_transfers,
)


PERIOD_OPTIONS = {
    "All time": None,
    "Last 7 days": 7,
    "Last 30 days": 30,
    "Last 90 days": 90,
    "This year": "year",
}

COUNTRY_OPTIONS = ["All", "Tunisia", "France"]
CHANNEL_OPTIONS = ["All", *CHANNELS]
STATUS_OPTIONS = ["All", "Success", "Pending", "Failed"]


def _parse_date(value: str) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(str(value)[:19], fmt)
        except ValueError:
            continue
    return None


def _in_period(when: datetime | None, period_key: str) -> bool:
    spec = PERIOD_OPTIONS.get(period_key, None)
    if spec is None or when is None:
        return True if spec is None else False
    now = datetime.now()
    if spec == "year":
        return when.year == now.year
    return when >= now - timedelta(days=int(spec))


def filter_transfers(
    period: str = "All time",
    country: str = "All",
    channel: str = "All",
    status: str = "All",
) -> list[dict]:
    filtered = []
    for row in list_transfers():
        when = _parse_date(row["date"])
        if not _in_period(when, period):
            continue
        if country != "All" and row.get("country") != country:
            continue
        if channel != "All" and row.get("channel") != channel:
            continue
        if status != "All" and row.get("status") != status:
            continue
        filtered.append(row)
    return filtered


def get_dashboard_metrics(
    period: str = "All time",
    country: str = "All",
    channel: str = "All",
    status: str = "All",
) -> dict:
    transfers = filter_transfers(period, country, channel, status)
    customers = customer_count()

    total_volume = sum(t["amount"] for t in transfers)
    transfers_count = len(transfers)
    success_count = sum(1 for t in transfers if t["status"] == "Success")
    success_rate = round((success_count / transfers_count) * 100, 1) if transfers_count else 0.0
    avg_ticket = round(total_volume / transfers_count, 2) if transfers_count else 0.0

    # Trend by month (last 12 calendar months)
    now = datetime.now()
    month_keys = []
    y, m = now.year, now.month
    for _ in range(12):
        month_keys.append((y, m))
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    month_keys.reverse()

    by_month_count = Counter()
    by_month_volume = defaultdict(float)
    for t in transfers:
        when = _parse_date(t["date"])
        if when is None:
            continue
        key = (when.year, when.month)
        by_month_count[key] += 1
        by_month_volume[key] += t["amount"]

    transfer_trend = []
    for y, m in month_keys:
        label = datetime(y, m, 1).strftime("%b")
        transfer_trend.append(
            {
                "month": label,
                "transfers": by_month_count[(y, m)],
                "volume_m": round(by_month_volume[(y, m)] / 1_000_000, 4),
                "volume": round(by_month_volume[(y, m)], 2),
            }
        )

    region_volume = defaultdict(float)
    for t in transfers:
        region_volume[t["region"] or "Unknown"] += t["amount"]
    regions = sorted(
        ((region, round(vol, 2)) for region, vol in region_volume.items()),
        key=lambda item: item[1],
        reverse=True,
    )
    if not regions:
        regions = [(name, 0.0) for name in REGION_META.keys()]

    channel_counts = Counter(t["channel"] or "Unknown" for t in transfers)
    total_ch = sum(channel_counts.values()) or 1
    channels = [
        (name, round(channel_counts.get(name, 0) * 100 / total_ch, 1))
        for name in CHANNELS
        if channel_counts.get(name, 0) or channel == "All"
    ]
    if not any(v > 0 for _, v in channels):
        channels = [(name, 0.0) for name in CHANNELS]

    status_counts = Counter(t["status"] or "Unknown" for t in transfers)
    total_st = sum(status_counts.values()) or 1
    status_mix = [
        (name, round(status_counts.get(name, 0) * 100 / total_st, 1))
        for name in ("Success", "Pending", "Failed")
    ]

    country_volume = defaultdict(float)
    for t in transfers:
        country_volume[t["country"] or "Unknown"] += t["amount"]
    countries = sorted(
        ((name, round(vol, 2)) for name, vol in country_volume.items()),
        key=lambda item: item[1],
        reverse=True,
    )

    # Recent activity: transfers + customer events, newest first
    recent = []
    for t in transfers:
        currency = "TND" if t.get("country") == "Tunisia" else "EUR"
        recent.append(
            (
                t.get("transfer_id") or "TRX",
                "Transfer",
                t.get("region") or "",
                t.get("status") or "",
                f"{t['amount']:,.2f} {currency}",
                _parse_date(t["date"]) or datetime.min,
            )
        )

    for event in list_activity():
        if event["event_type"] != "CustomerCreated":
            continue
        when = _parse_date(event["date"])
        if not _in_period(when, period):
            continue
        if country != "All" and event.get("country") != country:
            continue
        if channel != "All" and event.get("channel") != channel:
            continue
        recent.append(
            (
                event.get("reference") or "CUST",
                "CustomerCreated",
                event.get("region") or "",
                event.get("status") or "Success",
                event.get("detail") or "New customer",
                when or datetime.min,
            )
        )

    recent.sort(key=lambda item: item[5], reverse=True)
    recent_activity = [row[:5] for row in recent[:12]]

    return {
        "kpis": {
            "customers": customers,
            "transfers_mtd": transfers_count,
            "volume_mtd": total_volume,
            "success_rate": success_rate,
            "avg_ticket": avg_ticket,
            "active_branches": len({t["region"] for t in transfers if t.get("region")}) or 0,
        },
        "transfer_trend": transfer_trend,
        "channels": channels,
        "regions": regions,
        "products": status_mix,  # reused chart slot: status mix from live data
        "countries": countries,
        "recent_activity": recent_activity,
        "filters": {
            "period": period,
            "country": country,
            "channel": channel,
            "status": status,
            "rows": transfers_count,
        },
        "refreshed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": f"{TRANSFERS_PATH} + {FILE_PATH}",
        "activity_source": ACTIVITY_PATH,
    }
