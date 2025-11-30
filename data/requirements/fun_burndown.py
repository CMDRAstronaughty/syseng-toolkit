import json
import pandas as pd
import plotly.graph_objects as go


# ------------------------------------------------------
# 1. LOAD JSON FILE
# ------------------------------------------------------
json_file = "/home/myintsai/Documents/syseng-toolkit/data/requirements/fun_requirements.json"  # <-- set your file here

with open(json_file, "r") as f:
    data = json.load(f)


# ------------------------------------------------------
# 2. NORMALIZE JSON INTO A FLAT TABLE
# ------------------------------------------------------
rows = []

for item in data:
    for req_id, values in item.items():
        base = {k: v for k, v in values.items() if k != "Closure Details"}
        base["req_id"] = req_id
        
        for cd in values["Closure Details"]:
            row = base.copy()
            row.update(cd)
            rows.append(row)

df = pd.DataFrame(rows)

# Convert dates
df["Baseline Date"] = pd.to_datetime(df["Baseline Date"])
df["Replanned Date"] = pd.to_datetime(df["Replanned Date"])
df["Closure Date"]  = pd.to_datetime(df["Closure Date"], errors="coerce")


# ------------------------------------------------------
# 3. IDENTIFY LATEST STATUS PER REQUIREMENT
# ------------------------------------------------------
latest = df.sort_values("Replanned Date").groupby("req_id").tail(1)

# Technical Debt = failed rows
latest["is_tech_debt"] = latest["Closure Code"].eq("Failed")

# Closed = closed with actual closure date
latest["is_closed"] = latest["Closure Code"].eq("Closed") & latest["Closure Date"].notna()


# ------------------------------------------------------
# 4. BUILD BURNDOWN DATA: REMAINING WORK PER DAY
# ------------------------------------------------------
start_date = df["Baseline Date"].min()
end_date   = df[["Replanned Date", "Closure Date"]].max().max()

date_range = pd.date_range(start=start_date, end=end_date, freq="D")

records = []

for date in date_range:
    remaining = 0
    tech_debt = 0
    
    for _, row in latest.iterrows():
        
        # If closed before this date → not remaining
        if row["is_closed"] and date >= row["Closure Date"]:
            continue
        
        # If failed and replanned date passed → technical debt
        if row["is_tech_debt"] and date >= row["Replanned Date"]:
            tech_debt += 1
        
        else:
            remaining += 1
    
    records.append({
        "date": date,
        "remaining_work": remaining,
        "technical_debt": tech_debt,
        "total_remaining": remaining + tech_debt
    })

burndown_df = pd.DataFrame(records)


# ------------------------------------------------------
# 5. DAILY CLOSURE EVENTS (NORMAL VS TECH DEBT)
# ------------------------------------------------------
closure_events = df[df["Closure Code"].eq("Closed") & df["Closure Date"].notna()].copy()

closure_events = closure_events.merge(
    latest[["req_id", "is_tech_debt"]],
    on="req_id",
    how="left"
)

daily_closures = (
    closure_events
    .groupby(["Closure Date", "is_tech_debt"])
    .size()
    .reset_index(name="count")
)


# ------------------------------------------------------
# 6. UNIFIED CHART: BURNDOWN LINES + DAILY CLOSURE BARS
# ------------------------------------------------------
fig = go.Figure()

# --- Bar: Normal closures ---
fig.add_trace(go.Bar(
    x=daily_closures[daily_closures["is_tech_debt"] == False]["Closure Date"],
    y=daily_closures[daily_closures["is_tech_debt"] == False]["count"],
    name="Closed (Normal)",
    marker_color="steelblue",
    opacity=0.7,
    yaxis="y2"
))

# --- Bar: Technical Debt closures ---
fig.add_trace(go.Bar(
    x=daily_closures[daily_closures["is_tech_debt"] == True]["Closure Date"],
    y=daily_closures[daily_closures["is_tech_debt"] == True]["count"],
    name="Closed (Technical Debt)",
    marker_color="orange",
    opacity=0.7,
    yaxis="y2"
))

# --- Line: Total remaining work ---
fig.add_trace(go.Scatter(
    x=burndown_df["date"],
    y=burndown_df["total_remaining"],
    mode="lines",
    name="Total Remaining Work",
    line=dict(width=3, color="firebrick")
))

# --- Line: Technical debt ---
fig.add_trace(go.Scatter(
    x=burndown_df["date"],
    y=burndown_df["technical_debt"],
    mode="lines",
    name="Technical Debt",
    line=dict(width=3, dash="dash", color="orange")
))

# --- Line: Remaining (excluding technical debt) ---
fig.add_trace(go.Scatter(
    x=burndown_df["date"],
    y=burndown_df["remaining_work"],
    mode="lines",
    name="Remaining (Excl. Tech Debt)",
    line=dict(width=2, dash="dot", color="steelblue")
))


# ------------------------------------------------------
# 7. LAYOUT
# ------------------------------------------------------
fig.update_layout(
    title="Unified Burndown Chart with Daily Closure Bars",
    xaxis=dict(title="Date"),
    
    # Left Y-axis (burndown lines)
    yaxis=dict(
        title="Remaining Work",
        side="left",
        rangemode="tozero"
    ),
    
    # Right Y-axis (closure bars)
    yaxis2=dict(
        title="Daily Closures",
        overlaying="y",
        side="right",
        showgrid=False,
        rangemode="tozero"
    ),
    
    barmode="stack",
    template="plotly_white",
    legend=dict(x=0.01, y=0.99)
)

fig.show()
