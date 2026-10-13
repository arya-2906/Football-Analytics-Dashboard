# Football Player Performance Analytics Dashboard

An interactive football (soccer) player analytics dashboard built with **Python**, **Streamlit**, and **Plotly**.

> **Synthetic Data Notice:** All player names, clubs, and statistics in this project are entirely synthetic and procedurally generated. They do not represent any real-world football players, clubs, or match results.

---

## Features

- **Overview** — KPI cards (players, goals, assists, minutes, rating) + top-scorer bar chart + rating distribution
- **Player Analysis** — Goals vs Assists scatter, Shots vs Goals scatter with trendline, multi-player radar comparison
- **Team Analysis** — Goals, Assists, and Squad Size bar charts per team + summary table
- **Position Analysis** — Average stats by position, positional distribution pie, top player per position
- **Data Explorer** — Searchable, sortable stats table with CSV download
- **Sidebar Filters** — Season, Team, Position, and Player multiselects that propagate across all tabs
- **Dark, football-inspired UI** — Plotly dark theme with green accent colours

---

## Project Structure

```
Football Analytics Dashboard/
├── app.py                  # Main Streamlit application
├── generate_data.py        # One-time synthetic dataset generator
├── football_players.csv    # Pre-generated synthetic dataset (360 rows)
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## Installation

### Prerequisites
- Python 3.9 or later

### Steps

1. **Clone or download** this repository to your machine.

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **(Optional) Regenerate the dataset** — the CSV is already committed, but you can recreate it:
   ```bash
   python generate_data.py
   ```

---

## Running Locally

```bash
python -m streamlit run app.py
```

Then open your browser to `http://localhost:8501`.

> If `streamlit` is not on your PATH, use `python -m streamlit run app.py`.

---

## Deploying to Streamlit Community Cloud

1. Push the project to a **public GitHub repository** (include `app.py`, `football_players.csv`, and `requirements.txt`).
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app**, select your repository, set the branch to `main`, and set the **Main file path** to `app.py`.
4. Click **Deploy** — Streamlit Cloud will install dependencies automatically from `requirements.txt`.

---

## Dataset Schema

| Column | Type | Description |
|---|---|---|
| player_id | int | Unique player identifier |
| player_name | str | Synthetic full name |
| team | str | Club name (8 synthetic clubs) |
| position | str | GK / DEF / MID / FWD |
| season | str | 2021-22, 2022-23, 2023-24 |
| age | int | Player age (17–35) |
| nationality | str | Synthetic nationality |
| appearances | int | Matches played in season |
| minutes_played | int | Total minutes played |
| goals | int | Goals scored |
| assists | int | Goal assists |
| shots | int | Total shots attempted |
| shots_on_target | int | Shots on target |
| passes | int | Total passes attempted |
| pass_accuracy | float | Pass completion % |
| tackles | int | Defensive tackles |
| interceptions | int | Ball interceptions |
| yellow_cards | int | Yellow cards received |
| red_cards | int | Red cards received |
| clean_sheets | int | Clean sheets kept |
| rating | float | Overall match rating (5.0–9.5) |

---

## License

This project is for portfolio and educational purposes only.
