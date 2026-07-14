"""Power BI style analytics dashboard — live Excel data + filters."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from analytics_data import (
    CHANNEL_OPTIONS,
    COUNTRY_OPTIONS,
    PERIOD_OPTIONS,
    STATUS_OPTIONS,
    get_dashboard_metrics,
)
from ui_background import apply_window_background


BG_PANEL = "#0f1224"
BG_CARD = "#171b31"
BG_CARD_ALT = "#1d2340"
ACCENT = "#e11d48"
ACCENT_SOFT = "#f43f5e"
PURPLE = "#7c3aed"
CYAN = "#22d3ee"
AMBER = "#fbbf24"
GREEN = "#34d399"
TEXT = "#f8fafc"
MUTED = "#94a3b8"
GRID = "#2a3152"


def _fmt_money(value: float) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f} M"
    if value >= 1_000:
        return f"{value / 1_000:.1f} K"
    return f"{value:,.2f}"


def _kpi_card(parent: tk.Misc, title: str, value: str, delta: str, color: str) -> tk.Frame:
    card = tk.Frame(parent, bg=BG_CARD, highlightbackground=GRID, highlightthickness=1)
    accent = tk.Frame(card, bg=color, width=5)
    accent.pack(side="left", fill="y")

    body = tk.Frame(card, bg=BG_CARD)
    body.pack(side="left", fill="both", expand=True, padx=14, pady=12)

    tk.Label(body, text=title.upper(), bg=BG_CARD, fg=MUTED, font=("Segoe UI", 9, "bold")).pack(
        anchor="w"
    )
    tk.Label(body, text=value, bg=BG_CARD, fg=TEXT, font=("Segoe UI Semibold", 18)).pack(
        anchor="w", pady=(4, 2)
    )
    tk.Label(body, text=delta, bg=BG_CARD, fg=color, font=("Segoe UI", 9)).pack(anchor="w")
    return card


def _style_axes(ax, title: str) -> None:
    ax.set_facecolor(BG_CARD)
    ax.set_title(title, color=TEXT, fontsize=11, fontweight="bold", pad=10, loc="left")
    ax.tick_params(colors=MUTED, labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    ax.grid(True, axis="y", color=GRID, linestyle="--", linewidth=0.6, alpha=0.7)


def _build_charts(parent: tk.Misc, metrics: dict) -> FigureCanvasTkAgg:
    fig = Figure(figsize=(11.5, 5.0), dpi=100, facecolor=BG_PANEL)
    fig.subplots_adjust(left=0.06, right=0.98, top=0.90, bottom=0.14, wspace=0.28, hspace=0.45)

    ax1 = fig.add_subplot(2, 2, 1)
    months = [p["month"] for p in metrics["transfer_trend"]]
    transfers = [p["transfers"] for p in metrics["transfer_trend"]]
    volumes = [p.get("volume", p.get("volume_m", 0) * 1_000_000) for p in metrics["transfer_trend"]]
    _style_axes(ax1, "Transfers & volume (12 months)")
    ax1.fill_between(months, transfers, color=PURPLE, alpha=0.25)
    ax1.plot(months, transfers, color=CYAN, linewidth=2.2, marker="o", markersize=4)
    ax1.set_ylabel("Transfers", color=MUTED, fontsize=8)

    ax1b = ax1.twinx()
    ax1b.plot(months, volumes, color=AMBER, linewidth=1.6, linestyle="--", marker="s", markersize=3)
    ax1b.set_ylabel("Volume", color=MUTED, fontsize=8)
    ax1b.tick_params(colors=MUTED, labelsize=8)
    for spine in ax1b.spines.values():
        spine.set_color(GRID)

    ax2 = fig.add_subplot(2, 2, 2)
    labels = [r[0] for r in metrics["regions"]] or ["—"]
    values = [r[1] for r in metrics["regions"]] or [0]
    _style_axes(ax2, "Volume by region")
    colors = [ACCENT, PURPLE, CYAN, AMBER, GREEN, "#60a5fa"]
    bars = ax2.barh(labels[::-1], values[::-1], color=(colors * 3)[: len(values)][::-1], height=0.55)
    ax2.set_xlabel("Amount", color=MUTED, fontsize=8)
    max_val = max(values) if values else 0
    for bar, val in zip(bars, values[::-1]):
        ax2.text(
            bar.get_width() + (max_val * 0.02 if max_val else 0.1),
            bar.get_y() + bar.get_height() / 2,
            f"{val:,.0f}",
            va="center",
            color=TEXT,
            fontsize=8,
        )

    ax3 = fig.add_subplot(2, 2, 3)
    ax3.set_facecolor(BG_CARD)
    ch_labels = [c[0] for c in metrics["channels"]]
    ch_values = [max(c[1], 0) for c in metrics["channels"]]
    if sum(ch_values) <= 0:
        ch_labels, ch_values = ["No data"], [1]
    wedges, *_ = ax3.pie(
        ch_values,
        colors=[CYAN, PURPLE, AMBER, ACCENT_SOFT, GREEN][: len(ch_values)],
        startangle=90,
        wedgeprops={"width": 0.42, "edgecolor": BG_CARD, "linewidth": 2},
    )
    ax3.set_title("Channel mix (%)", color=TEXT, fontsize=11, fontweight="bold", pad=10, loc="left")
    ax3.legend(
        wedges,
        [f"{n} — {v}%" for n, v in zip(ch_labels, ch_values)],
        loc="center left",
        bbox_to_anchor=(0.95, 0.5),
        fontsize=8,
        frameon=False,
        labelcolor=MUTED,
    )

    ax4 = fig.add_subplot(2, 2, 4)
    _style_axes(ax4, "Status mix (%) — live")
    p_labels = [p[0] for p in metrics["products"]]
    p_values = [p[1] for p in metrics["products"]]
    if not p_values:
        p_labels, p_values = ["No data"], [0]
    ax4.bar(
        p_labels,
        p_values,
        color=[GREEN, AMBER, ACCENT][: len(p_values)],
        width=0.55,
        edgecolor=BG_CARD,
    )
    ax4.set_ylim(0, max(max(p_values) * 1.25, 1))

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    widget = canvas.get_tk_widget()
    widget.configure(bg=BG_PANEL, highlightthickness=0)
    widget.pack(fill="both", expand=True, padx=8, pady=4)
    return canvas


def _fill_activity_table(tree: ttk.Treeview, rows: list) -> None:
    for item in tree.get_children():
        tree.delete(item)
    for row in rows:
        tree.insert("", "end", values=row)


def mount_powerbi_panel(parent: tk.Misc, theme: dict | None = None):
    """Embed the live BI dashboard into an existing frame (single-app shell)."""
    colors = {
        "panel": (theme or {}).get("bg", BG_PANEL),
        "card": (theme or {}).get("card", BG_CARD),
        "card_alt": (theme or {}).get("bg_alt", BG_CARD_ALT),
        "text": (theme or {}).get("text", TEXT),
        "muted": (theme or {}).get("muted", MUTED),
        "accent": (theme or {}).get("accent", ACCENT),
        "purple": (theme or {}).get("purple", PURPLE),
        "cyan": (theme or {}).get("cyan", CYAN),
        "amber": (theme or {}).get("amber", AMBER),
        "green": (theme or {}).get("green", GREEN),
        "grid": (theme or {}).get("card_border", GRID),
    }

    shell = tk.Frame(parent, bg=colors["panel"])
    shell.pack(fill="both", expand=True)

    header = tk.Frame(shell, bg=colors["panel"])
    header.pack(fill="x", padx=8, pady=(4, 4))

    brand = tk.Frame(header, bg=colors["panel"])
    brand.pack(side="left")
    tk.Label(
        brand,
        text="VERMEG  |  Banking Intelligence",
        bg=colors["panel"],
        fg=colors["accent"],
        font=("Segoe UI", 10, "bold"),
    ).pack(anchor="w")
    tk.Label(
        brand,
        text="Live Power BI Dashboard",
        bg=colors["panel"],
        fg=colors["text"],
        font=("Segoe UI Semibold", 18),
    ).pack(anchor="w")

    meta = tk.Frame(header, bg=colors["panel"])
    meta.pack(side="right")
    refresh_label = tk.Label(meta, text="", bg=colors["panel"], fg=colors["muted"], font=("Segoe UI", 9))
    refresh_label.pack(anchor="e")
    source_label = tk.Label(meta, text="", bg=colors["panel"], fg=colors["muted"], font=("Segoe UI", 9))
    source_label.pack(anchor="e")

    filters = tk.Frame(shell, bg=colors["card_alt"], highlightbackground=colors["grid"], highlightthickness=1)
    filters.pack(fill="x", padx=8, pady=6)

    tk.Label(
        filters,
        text="Filters",
        bg=colors["card_alt"],
        fg=colors["text"],
        font=("Segoe UI Semibold", 10),
    ).grid(row=0, column=0, padx=10, pady=8, sticky="w")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "BI.TCombobox",
        fieldbackground=colors["card"],
        background=colors["card"],
        foreground=colors["text"],
    )

    period_var = tk.StringVar(value="All time")
    country_var = tk.StringVar(value="All")
    channel_var = tk.StringVar(value="All")
    status_var = tk.StringVar(value="All")

    def _filter_label(col: int, text: str):
        tk.Label(
            filters,
            text=text,
            bg=colors["card_alt"],
            fg=colors["muted"],
            font=("Segoe UI", 8, "bold"),
        ).grid(row=0, column=col, padx=(8, 2), pady=4, sticky="w")

    _filter_label(1, "Period")
    period_box = ttk.Combobox(
        filters,
        textvariable=period_var,
        values=list(PERIOD_OPTIONS.keys()),
        state="readonly",
        width=12,
        style="BI.TCombobox",
    )
    period_box.grid(row=0, column=2, padx=4, pady=8)

    _filter_label(3, "Country")
    country_box = ttk.Combobox(
        filters,
        textvariable=country_var,
        values=COUNTRY_OPTIONS,
        state="readonly",
        width=10,
        style="BI.TCombobox",
    )
    country_box.grid(row=0, column=4, padx=4, pady=8)

    _filter_label(5, "Channel")
    channel_box = ttk.Combobox(
        filters,
        textvariable=channel_var,
        values=CHANNEL_OPTIONS,
        state="readonly",
        width=12,
        style="BI.TCombobox",
    )
    channel_box.grid(row=0, column=6, padx=4, pady=8)

    _filter_label(7, "Status")
    status_box = ttk.Combobox(
        filters,
        textvariable=status_var,
        values=STATUS_OPTIONS,
        state="readonly",
        width=10,
        style="BI.TCombobox",
    )
    status_box.grid(row=0, column=8, padx=4, pady=8)

    rows_label = tk.Label(filters, text="", bg=colors["card_alt"], fg=colors["cyan"], font=("Segoe UI", 9))
    rows_label.grid(row=0, column=10, padx=10, pady=8)

    kpi_row = tk.Frame(shell, bg=colors["panel"])
    kpi_row.pack(fill="x", padx=8, pady=4)

    charts_wrap = tk.Frame(shell, bg=colors["panel"], highlightbackground=colors["grid"], highlightthickness=1)
    charts_wrap.pack(fill="both", expand=True, padx=8, pady=(4, 6))

    table_wrap = tk.Frame(shell, bg=colors["panel"])
    table_wrap.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    table_header = tk.Frame(table_wrap, bg=colors["panel"])
    table_header.pack(fill="x")
    tk.Label(
        table_header,
        text="Recent activity (live)",
        bg=colors["panel"],
        fg=colors["text"],
        font=("Segoe UI Semibold", 12),
    ).pack(side="left")
    tk.Label(
        table_header,
        text="Customers + transfers from Excel",
        bg=colors["panel"],
        fg=colors["muted"],
        font=("Segoe UI", 9),
    ).pack(side="right")

    style.configure(
        "BI.Treeview",
        background=colors["card"],
        foreground=colors["text"],
        fieldbackground=colors["card"],
        borderwidth=0,
        rowheight=26,
        font=("Segoe UI", 9),
    )
    style.configure(
        "BI.Treeview.Heading",
        background=colors["card_alt"],
        foreground=colors["muted"],
        relief="flat",
        font=("Segoe UI", 9, "bold"),
    )
    style.map(
        "BI.Treeview",
        background=[("selected", colors["purple"])],
        foreground=[("selected", colors["text"])],
    )

    cols = ("id", "type", "region", "status", "amount")
    tree = ttk.Treeview(table_wrap, columns=cols, show="headings", style="BI.Treeview", height=5)
    headings = {
        "id": "Reference",
        "type": "Type",
        "region": "Region",
        "status": "Status",
        "amount": "Amount / Detail",
    }
    widths = {"id": 100, "type": 130, "region": 100, "status": 80, "amount": 200}
    for col in cols:
        tree.heading(col, text=headings[col])
        tree.column(col, width=widths[col], anchor="w")
    tree.pack(fill="both", expand=True, pady=(6, 0))

    state = {"canvas": None}

    def render():
        metrics = get_dashboard_metrics(
            period=period_var.get(),
            country=country_var.get(),
            channel=channel_var.get(),
            status=status_var.get(),
        )
        kpis = metrics["kpis"]

        refresh_label.config(text=f"Last refresh  {metrics['refreshed_at']}")
        source_label.config(text=f"Data source  {metrics['source']}")
        rows_label.config(text=f"{metrics['filters']['rows']} rows")

        for child in kpi_row.winfo_children():
            child.destroy()

        cards = [
            ("Customers", f"{kpis['customers']:,}", "live customers.xlsx", colors["cyan"]),
            ("Transfers", f"{kpis['transfers_mtd']:,}", "transfers.xlsx", colors["green"]),
            ("Volume", _fmt_money(kpis["volume_mtd"]), "filtered amounts", colors["amber"]),
            ("Success rate", f"{kpis['success_rate']}%", "Success / filtered", colors["green"]),
            (
                "Avg ticket",
                _fmt_money(kpis["avg_ticket"]),
                f"{kpis['active_branches']} regions",
                colors["purple"],
            ),
        ]
        for i, (title, value, delta, color) in enumerate(cards):
            card = _kpi_card(kpi_row, title, value, delta, color)
            card.grid(row=0, column=i, sticky="nsew", padx=5)
            kpi_row.grid_columnconfigure(i, weight=1)

        for child in charts_wrap.winfo_children():
            child.destroy()
        state["canvas"] = _build_charts(charts_wrap, metrics)
        parent._bi_canvas = state["canvas"]

        _fill_activity_table(tree, metrics["recent_activity"])

    tk.Button(
        filters,
        text="Apply",
        command=render,
        bg=colors["purple"],
        fg="#ffffff",
        activebackground=colors["accent"],
        activeforeground="#ffffff",
        relief="flat",
        padx=12,
        pady=3,
        font=("Segoe UI", 9, "bold"),
        cursor="hand2",
    ).grid(row=0, column=9, padx=8, pady=8)

    tk.Button(
        meta,
        text="Refresh",
        command=render,
        bg=colors["purple"],
        fg="#ffffff",
        activebackground=colors["accent"],
        activeforeground="#ffffff",
        relief="flat",
        padx=12,
        pady=3,
        font=("Segoe UI", 9, "bold"),
        cursor="hand2",
    ).pack(anchor="e", pady=(4, 0))

    for box in (period_box, country_box, channel_box, status_box):
        box.bind("<<ComboboxSelected>>", lambda _e: render())

    render()
    return shell


def open_powerbi_dashboard():
    window = tk.Toplevel()
    window.title("Power BI Dashboard")
    window.geometry("1280x860")
    window.minsize(1100, 740)
    apply_window_background(window)

    shell = tk.Frame(window, bg=BG_PANEL)
    shell.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.96)
    mount_powerbi_panel(shell)
