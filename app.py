"""
app.py
------
Football Player Performance Analytics Dashboard
Run with:  python -m streamlit run app.py
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Football Analytics Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS — dark football theme with green accents ───────────────────────
st.markdown(
    """
    <style>
    /* Main background */
    .stApp { background-color: #0d1117; color: #e6edf3; }

    /* Sidebar */
    section[data-testid="stSidebar"] { background-color: #161b22; }
    section[data-testid="stSidebar"] * { color: #e6edf3 !important; }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background-color: #161b22;
        border: 1px solid #2ecc71;
        border-radius: 8px;
        padding: 16px 20px;
    }
    div[data-testid="metric-container"] label { color: #8b949e !important; font-size: 0.8rem; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #2ecc71 !important; font-size: 1.6rem; font-weight: 700;
    }

    /* Tab bar */
    button[data-baseweb="tab"] { color: #8b949e !important; }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #2ecc71 !important;
        border-bottom: 2px solid #2ecc71 !important;
    }

    /* Headings */
    h1, h2, h3 { color: #2ecc71 !important; }

    /* Dataframe */
    .stDataFrame { border: 1px solid #30363d; border-radius: 6px; }

    /* Download button */
    div[data-testid="stDownloadButton"] button {
        background-color: #2ecc71; color: #0d1117;
        border: none; border-radius: 6px; font-weight: 600;
    }
    div[data-testid="stDownloadButton"] button:hover { background-color: #27ae60; }

    /* Info / warning banners */
    div[data-testid="stAlert"] { border-radius: 6px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Data loading ──────────────────────────────────────────────────────────────
DATA_FILE = "football_players.csv"

@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_FILE)
    # Ensure correct dtypes
    df["player_id"]     = df["player_id"].astype(int)
    df["rating"]        = df["rating"].astype(float)
    df["pass_accuracy"] = df["pass_accuracy"].astype(float)
    return df

try:
    raw_df = load_data()
except FileNotFoundError:
    st.error(
        f"**Data file not found:** `{DATA_FILE}`\n\n"
        "Please run `python generate_data.py` to create the dataset, then refresh this page."
    )
    st.stop()

# Pre-compute global min/max for radar normalisation (unaffected by filters)
RADAR_COLS = ["goals", "assists", "shots_on_target", "pass_accuracy", "tackles", "rating"]
GLOBAL_MIN = raw_df[RADAR_COLS].min()
GLOBAL_MAX = raw_df[RADAR_COLS].max()

# ── Sidebar filters ───────────────────────────────────────────────────────────
st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Football_pictogram.svg/120px-Football_pictogram.svg.png",
    width=60,
)
st.sidebar.title("⚽ Filters")
st.sidebar.markdown("---")

all_seasons   = sorted(raw_df["season"].unique())
all_teams     = sorted(raw_df["team"].unique())
all_positions = sorted(raw_df["position"].unique())

sel_seasons   = st.sidebar.multiselect("Season",   all_seasons,   default=all_seasons)
sel_teams     = st.sidebar.multiselect("Team",     all_teams,     default=all_teams)
sel_positions = st.sidebar.multiselect("Position", all_positions, default=all_positions)

# Derive player list after season/team/position filter
_pre_filtered = raw_df[
    raw_df["season"].isin(sel_seasons if sel_seasons else all_seasons) &
    raw_df["team"].isin(sel_teams if sel_teams else all_teams) &
    raw_df["position"].isin(sel_positions if sel_positions else all_positions)
]
all_players = sorted(_pre_filtered["player_name"].unique())
sel_players = st.sidebar.multiselect("Player", all_players, default=[])

st.sidebar.markdown("---")
st.sidebar.caption("All data is synthetic and for demonstration purposes only.")

# Build filtered_df
def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    seasons   = sel_seasons   if sel_seasons   else all_seasons
    teams     = sel_teams     if sel_teams     else all_teams
    positions = sel_positions if sel_positions else all_positions
    mask = (
        df["season"].isin(seasons) &
        df["team"].isin(teams) &
        df["position"].isin(positions)
    )
    if sel_players:
        mask &= df["player_name"].isin(sel_players)
    return df[mask].copy()

filtered_df = apply_filters(raw_df)

# ── Synthetic data banner ─────────────────────────────────────────────────────
st.info(
    "**Synthetic Data Notice:** All player names, clubs, and statistics displayed here are "
    "procedurally generated for demonstration purposes. They do not represent real-world "
    "football players, clubs, or match results.",
    icon="ℹ️",
)

if filtered_df.empty:
    st.warning("No data matches the current filters. Please adjust the sidebar selections.")
    st.stop()

# ── Helper: Plotly dark layout defaults ──────────────────────────────────────
PLOTLY_TEMPLATE = "plotly_dark"
GREEN = "#2ecc71"
ACCENT_COLOURS = px.colors.qualitative.Vivid


def _fig_layout(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor="#161b22",
        plot_bgcolor="#161b22",
        font=dict(color="#e6edf3", size=12),
        title=dict(text=title, font=dict(color="#2ecc71", size=15)),
        margin=dict(l=40, r=20, t=50, b=40),
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab_overview, tab_player, tab_team, tab_position, tab_explorer = st.tabs([
    "📊 Overview",
    "👤 Player Analysis",
    "🏟️ Team Analysis",
    "🎯 Position Analysis",
    "🔍 Data Explorer",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab_overview:
    st.markdown("## Overview")

    # ── KPI calculations ──────────────────────────────────────────────────────
    total_players     = filtered_df["player_id"].nunique()
    total_goals       = int(filtered_df["goals"].sum())
    total_assists     = int(filtered_df["assists"].sum())
    total_minutes     = int(filtered_df["minutes_played"].sum())
    avg_rating        = filtered_df["rating"].mean()
    top_scorer_row    = filtered_df.loc[filtered_df["goals"].idxmax()]
    top_assister_row  = filtered_df.loc[filtered_df["assists"].idxmax()]

    # ── KPI cards ─────────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Players",       f"{total_players:,}")
    c2.metric("Total Goals",         f"{total_goals:,}")
    c3.metric("Total Assists",       f"{total_assists:,}")
    c4.metric("Total Minutes",       f"{total_minutes:,}")
    c5.metric("Avg Player Rating",   f"{avg_rating:.2f}")

    st.markdown("---")

    # ── Secondary KPIs ────────────────────────────────────────────────────────
    k1, k2 = st.columns(2)
    k1.metric("Top Scorer",   top_scorer_row["player_name"],
              f"{int(top_scorer_row['goals'])} goals — {top_scorer_row['team']}")
    k2.metric("Top Assister", top_assister_row["player_name"],
              f"{int(top_assister_row['assists'])} assists — {top_assister_row['team']}")

    st.markdown("")

    # ── Charts ────────────────────────────────────────────────────────────────
    ch1, ch2 = st.columns(2)

    with ch1:
        # Top 10 scorers horizontal bar
        top10 = (
            filtered_df.groupby(["player_name", "team"], as_index=False)["goals"]
            .sum()
            .nlargest(10, "goals")
            .sort_values("goals")
        )
        fig_scorers = px.bar(
            top10, x="goals", y="player_name",
            orientation="h", color="team",
            color_discrete_sequence=ACCENT_COLOURS,
            labels={"goals": "Goals", "player_name": "Player", "team": "Team"},
            hover_data={"team": True, "goals": True},
        )
        _fig_layout(fig_scorers, "Top 10 Goal Scorers")
        fig_scorers.update_traces(marker_line_width=0)
        st.plotly_chart(fig_scorers, use_container_width=True)

    with ch2:
        # Rating distribution histogram
        fig_rating = px.histogram(
            filtered_df, x="rating", nbins=20,
            color_discrete_sequence=[GREEN],
            labels={"rating": "Player Rating", "count": "Players"},
        )
        _fig_layout(fig_rating, "Player Rating Distribution")
        fig_rating.update_traces(marker_line_color="#0d1117", marker_line_width=0.5)
        fig_rating.update_layout(bargap=0.05)
        st.plotly_chart(fig_rating, use_container_width=True)

    # ── Goals vs Assists overview scatter ─────────────────────────────────────
    st.markdown("### Goals & Assists by Team")
    team_summary = (
        filtered_df.groupby("team", as_index=False)
        .agg(goals=("goals", "sum"), assists=("assists", "sum"))
    )
    fig_ta = px.scatter(
        team_summary, x="goals", y="assists", text="team",
        size="goals", color="team",
        color_discrete_sequence=ACCENT_COLOURS,
        labels={"goals": "Total Goals", "assists": "Total Assists", "team": "Team"},
    )
    fig_ta.update_traces(textposition="top center")
    _fig_layout(fig_ta, "")
    st.plotly_chart(fig_ta, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — PLAYER ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab_player:
    st.markdown("## Player Analysis")

    ch1, ch2 = st.columns(2)

    with ch1:
        # Goals vs Assists scatter — colour by position
        fig_ga = px.scatter(
            filtered_df, x="goals", y="assists",
            color="position",
            color_discrete_sequence=ACCENT_COLOURS,
            hover_data={"player_name": True, "team": True, "rating": True,
                        "goals": True, "assists": True, "position": False},
            labels={"goals": "Goals", "assists": "Assists",
                    "position": "Position", "player_name": "Player", "team": "Team"},
            size="rating", size_max=12,
        )
        _fig_layout(fig_ga, "Goals vs Assists (by Position)")
        st.plotly_chart(fig_ga, use_container_width=True)

    with ch2:
        # Shots vs Goals scatter — colour by team, OLS trendline
        try:
            fig_sg = px.scatter(
                filtered_df, x="shots", y="goals",
                color="team",
                color_discrete_sequence=ACCENT_COLOURS,
                trendline="ols",
                hover_data={"player_name": True, "team": True, "shots": True, "goals": True},
                labels={"shots": "Shots", "goals": "Goals",
                        "team": "Team", "player_name": "Player"},
            )
        except Exception:
            # Fallback without trendline if statsmodels unavailable
            fig_sg = px.scatter(
                filtered_df, x="shots", y="goals",
                color="team",
                color_discrete_sequence=ACCENT_COLOURS,
                hover_data={"player_name": True, "team": True},
                labels={"shots": "Shots", "goals": "Goals"},
            )
        _fig_layout(fig_sg, "Shots vs Goals (by Team)")
        st.plotly_chart(fig_sg, use_container_width=True)

    st.markdown("---")

    # ── Radar / Spider chart ──────────────────────────────────────────────────
    st.markdown("### Player Comparison Radar")
    st.caption("Select up to 3 players to compare across 6 key attributes.")

    available_players = sorted(filtered_df["player_name"].unique())
    radar_players = st.multiselect(
        "Select players for radar chart",
        options=available_players,
        default=available_players[:2] if len(available_players) >= 2 else available_players,
        max_selections=3,
        key="radar_select",
    )

    if len(radar_players) < 1:
        st.info("Select at least one player above to display the radar chart.")
    else:
        radar_labels = ["Goals", "Assists", "Shots on Target", "Pass Accuracy", "Tackles", "Rating"]

        # Normalise to 0–10 using global min/max
        def normalise(series_name: str, value: float) -> float:
            lo = GLOBAL_MIN[series_name]
            hi = GLOBAL_MAX[series_name]
            if hi == lo:
                return 5.0
            return round((value - lo) / (hi - lo) * 10, 2)

        radar_fig = go.Figure()
        colours = ["#2ecc71", "#3498db", "#e74c3c"]

        for idx, pname in enumerate(radar_players):
            pdata = filtered_df[filtered_df["player_name"] == pname]
            if pdata.empty:
                continue
            # Aggregate across seasons in the filtered set
            vals = {
                "goals":           pdata["goals"].sum(),
                "assists":         pdata["assists"].sum(),
                "shots_on_target": pdata["shots_on_target"].sum(),
                "pass_accuracy":   pdata["pass_accuracy"].mean(),
                "tackles":         pdata["tackles"].sum(),
                "rating":          pdata["rating"].mean(),
            }
            norm_vals = [normalise(k, v) for k, v in vals.items()]
            norm_vals_closed = norm_vals + [norm_vals[0]]  # close the polygon

            radar_fig.add_trace(go.Scatterpolar(
                r=norm_vals_closed,
                theta=radar_labels + [radar_labels[0]],
                fill="toself",
                fillcolor=colours[idx % 3],
                opacity=0.25,
                line=dict(color=colours[idx % 3], width=2),
                name=pname,
            ))

        radar_fig.update_layout(
            template=PLOTLY_TEMPLATE,
            paper_bgcolor="#161b22",
            polar=dict(
                bgcolor="#161b22",
                radialaxis=dict(visible=True, range=[0, 10], color="#8b949e"),
                angularaxis=dict(color="#8b949e"),
            ),
            font=dict(color="#e6edf3"),
            legend=dict(bgcolor="#161b22", bordercolor="#30363d"),
            margin=dict(l=60, r=60, t=60, b=40),
        )
        st.plotly_chart(radar_fig, use_container_width=True)

    st.markdown("---")

    # ── Goals per 90 top chart ────────────────────────────────────────────────
    st.markdown("### Goals per 90 Minutes (Top 15)")
    gp90 = filtered_df.copy()
    gp90["goals_per_90"] = (gp90["goals"] / (gp90["minutes_played"] / 90)).replace([np.inf, -np.inf], 0).fillna(0)
    gp90 = gp90[gp90["minutes_played"] >= 400]  # minimum minutes threshold
    top15_gp90 = gp90.nlargest(15, "goals_per_90").sort_values("goals_per_90")

    fig_gp90 = px.bar(
        top15_gp90, x="goals_per_90", y="player_name", orientation="h",
        color="team", color_discrete_sequence=ACCENT_COLOURS,
        hover_data={"player_name": True, "team": True, "goals": True, "minutes_played": True},
        labels={"goals_per_90": "Goals / 90 min", "player_name": "Player"},
    )
    _fig_layout(fig_gp90, "")
    st.plotly_chart(fig_gp90, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — TEAM ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab_team:
    st.markdown("## Team Analysis")

    team_agg = (
        filtered_df.groupby("team", as_index=False)
        .agg(
            total_goals   = ("goals",      "sum"),
            total_assists = ("assists",    "sum"),
            avg_rating    = ("rating",     "mean"),
            player_count  = ("player_id",  "nunique"),
        )
        .sort_values("total_goals", ascending=False)
    )

    ch1, ch2, ch3 = st.columns(3)

    with ch1:
        fig_tg = px.bar(
            team_agg.sort_values("total_goals"),
            x="total_goals", y="team", orientation="h",
            color="team", color_discrete_sequence=ACCENT_COLOURS,
            labels={"total_goals": "Goals", "team": "Team"},
        )
        _fig_layout(fig_tg, "Goals by Team")
        fig_tg.update_layout(showlegend=False)
        st.plotly_chart(fig_tg, use_container_width=True)

    with ch2:
        fig_ta = px.bar(
            team_agg.sort_values("total_assists"),
            x="total_assists", y="team", orientation="h",
            color="team", color_discrete_sequence=ACCENT_COLOURS,
            labels={"total_assists": "Assists", "team": "Team"},
        )
        _fig_layout(fig_ta, "Assists by Team")
        fig_ta.update_layout(showlegend=False)
        st.plotly_chart(fig_ta, use_container_width=True)

    with ch3:
        fig_pc = px.bar(
            team_agg.sort_values("player_count"),
            x="player_count", y="team", orientation="h",
            color="team", color_discrete_sequence=ACCENT_COLOURS,
            labels={"player_count": "Players", "team": "Team"},
        )
        _fig_layout(fig_pc, "Squad Size by Team")
        fig_pc.update_layout(showlegend=False)
        st.plotly_chart(fig_pc, use_container_width=True)

    st.markdown("---")
    st.markdown("### Team Summary Table")

    display_team = team_agg.rename(columns={
        "team":          "Team",
        "total_goals":   "Goals",
        "total_assists": "Assists",
        "avg_rating":    "Avg Rating",
        "player_count":  "Players",
    })
    display_team["Avg Rating"] = display_team["Avg Rating"].round(2)
    st.dataframe(
        display_team,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Goals":     st.column_config.NumberColumn(format="%d"),
            "Assists":   st.column_config.NumberColumn(format="%d"),
            "Avg Rating": st.column_config.NumberColumn(format="%.2f"),
            "Players":   st.column_config.NumberColumn(format="%d"),
        },
    )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — POSITION ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab_position:
    st.markdown("## Position Analysis")

    pos_agg = (
        filtered_df.groupby("position", as_index=False)
        .agg(
            avg_goals        = ("goals",        "mean"),
            avg_assists      = ("assists",       "mean"),
            avg_tackles      = ("tackles",       "mean"),
            avg_clean_sheets = ("clean_sheets",  "mean"),
            avg_rating       = ("rating",        "mean"),
            player_count     = ("player_id",     "nunique"),
        )
    )

    ch1, ch2 = st.columns(2)

    with ch1:
        # Grouped bar: avg stats by position
        melt_cols = ["avg_goals", "avg_assists", "avg_tackles", "avg_clean_sheets"]
        melt_labels = {"avg_goals": "Goals", "avg_assists": "Assists",
                       "avg_tackles": "Tackles", "avg_clean_sheets": "Clean Sheets"}
        pos_long = pos_agg.melt(
            id_vars="position", value_vars=melt_cols,
            var_name="Statistic", value_name="Average"
        )
        pos_long["Statistic"] = pos_long["Statistic"].map(melt_labels)

        fig_pos = px.bar(
            pos_long, x="position", y="Average", color="Statistic",
            barmode="group",
            color_discrete_sequence=ACCENT_COLOURS,
            labels={"position": "Position", "Average": "Season Average"},
        )
        _fig_layout(fig_pos, "Average Stats by Position")
        st.plotly_chart(fig_pos, use_container_width=True)

    with ch2:
        # Pie: position distribution
        fig_pie = px.pie(
            pos_agg, values="player_count", names="position",
            color_discrete_sequence=["#2ecc71", "#3498db", "#e67e22", "#e74c3c"],
            hole=0.35,
        )
        _fig_layout(fig_pie, "Player Distribution by Position")
        fig_pie.update_traces(textinfo="label+percent", textfont_color="#e6edf3")
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    st.markdown("### Top Player per Position")

    pos_order = ["GK", "DEF", "MID", "FWD"]
    top_cards = st.columns(4)

    for i, pos in enumerate(pos_order):
        pos_df = filtered_df[filtered_df["position"] == pos]
        if pos_df.empty:
            top_cards[i].metric(f"Top {pos}", "N/A", "No data")
        else:
            best = pos_df.loc[pos_df["rating"].idxmax()]
            top_cards[i].metric(
                f"Top {pos}",
                best["player_name"],
                f"Rating {best['rating']:.2f} — {best['team']}",
            )

    st.markdown("---")
    st.markdown("### Average Rating by Position")

    fig_rating_pos = px.bar(
        pos_agg.sort_values("avg_rating", ascending=False),
        x="position", y="avg_rating",
        color="position",
        color_discrete_sequence=["#2ecc71", "#3498db", "#e67e22", "#e74c3c"],
        labels={"position": "Position", "avg_rating": "Average Rating"},
        text="avg_rating",
    )
    fig_rating_pos.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    _fig_layout(fig_rating_pos, "")
    st.plotly_chart(fig_rating_pos, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — DATA EXPLORER
# ══════════════════════════════════════════════════════════════════════════════
with tab_explorer:
    st.markdown("## Data Explorer")
    st.caption("Search, sort, and download the filtered player dataset.")

    # Player name search
    search_query = st.text_input("Search by player name", placeholder="e.g. Carlos Silva")
    display_df = filtered_df.copy()
    if search_query.strip():
        display_df = display_df[
            display_df["player_name"].str.contains(search_query.strip(), case=False, na=False)
        ]

    # Sort controls
    sort_col, sort_dir_col = st.columns([3, 1])
    with sort_col:
        sort_by = st.selectbox(
            "Sort by",
            options=["goals", "assists", "rating", "minutes_played", "shots", "tackles", "player_name"],
            index=0,
        )
    with sort_dir_col:
        sort_asc = st.radio("Order", ["Descending", "Ascending"], horizontal=True) == "Ascending"

    display_df = display_df.sort_values(sort_by, ascending=sort_asc)

    st.caption(f"Showing **{len(display_df):,}** rows × **{len(display_df.columns)}** columns")

    st.dataframe(
        display_df.reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
        column_config={
            "player_id":       st.column_config.NumberColumn("ID",        format="%d"),
            "age":             st.column_config.NumberColumn("Age",       format="%d"),
            "appearances":     st.column_config.NumberColumn("Apps",      format="%d"),
            "minutes_played":  st.column_config.NumberColumn("Minutes",   format="%d"),
            "goals":           st.column_config.NumberColumn("Goals",     format="%d"),
            "assists":         st.column_config.NumberColumn("Assists",   format="%d"),
            "shots":           st.column_config.NumberColumn("Shots",     format="%d"),
            "shots_on_target": st.column_config.NumberColumn("SoT",       format="%d"),
            "passes":          st.column_config.NumberColumn("Passes",    format="%d"),
            "pass_accuracy":   st.column_config.NumberColumn("Pass Acc%", format="%.1f"),
            "tackles":         st.column_config.NumberColumn("Tackles",   format="%d"),
            "interceptions":   st.column_config.NumberColumn("Intercepts",format="%d"),
            "yellow_cards":    st.column_config.NumberColumn("YC",        format="%d"),
            "red_cards":       st.column_config.NumberColumn("RC",        format="%d"),
            "clean_sheets":    st.column_config.NumberColumn("CS",        format="%d"),
            "rating":          st.column_config.NumberColumn("Rating",    format="%.2f"),
        },
    )

    st.markdown("")

    # CSV download
    csv_bytes = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇ Download filtered data as CSV",
        data=csv_bytes,
        file_name="football_players_filtered.csv",
        mime="text/csv",
    )
