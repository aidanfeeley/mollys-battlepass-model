import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Molly's Cash Battle Pass Model", layout="wide")
st.title("Molly's Cash Battle Pass Model")
st.caption("Interactive model for tuning battle pass economics")

# ===================================================================
# CURRENT MODEL DATA (exact match to their spreadsheet)
# ===================================================================

CURRENT_STEPS = [
    {"step": 1,  "level": 1,   "tickets": 50,     "sess_med": 1,    "sess_eng": 1,  "type": "Instant Win",  "win_chance": 1.00,  "free_prize": 5.00,  "paid_prize": 10.00},
    {"step": 2,  "level": 11,  "tickets": 550,    "sess_med": 1,    "sess_eng": 1,  "type": "Instant Win",  "win_chance": 0.00,  "free_prize": 0.50,  "paid_prize": 1.00},
    {"step": 3,  "level": 21,  "tickets": 1155,   "sess_med": 1,    "sess_eng": 1,  "type": "Instant Win",  "win_chance": 1.00,  "free_prize": 1.00,  "paid_prize": 2.00},
    {"step": 4,  "level": 31,  "tickets": 1805,   "sess_med": 2,    "sess_eng": 1,  "type": "Instant Win",  "win_chance": 0.00,  "free_prize": 1.50,  "paid_prize": 3.00},
    {"step": 5,  "level": 41,  "tickets": 2455,   "sess_med": 3,    "sess_eng": 1,  "type": "Instant Win",  "win_chance": 0.00,  "free_prize": 0.50,  "paid_prize": 1.00},
    {"step": 6,  "level": 51,  "tickets": 3105,   "sess_med": 3,    "sess_eng": 1,  "type": "Sweepstakes",  "win_chance": 0.00,  "free_prize": 0.00,  "paid_prize": 0.00,  "sweep_amt": 100},
    {"step": 7,  "level": 61,  "tickets": 3755,   "sess_med": 4,    "sess_eng": 2,  "type": "Instant Win",  "win_chance": 0.00,  "free_prize": 1.50,  "paid_prize": 3.00},
    {"step": 8,  "level": 72,  "tickets": 4470,   "sess_med": 5,    "sess_eng": 2,  "type": "Instant Win",  "win_chance": 1.00,  "free_prize": 0.50,  "paid_prize": 1.00},
    {"step": 9,  "level": 83,  "tickets": 5185,   "sess_med": 6,    "sess_eng": 2,  "type": "Instant Win",  "win_chance": 0.00,  "free_prize": 0.50,  "paid_prize": 1.00},
    {"step": 10, "level": 94,  "tickets": 5900,   "sess_med": 7,    "sess_eng": 3,  "type": "Instant Win",  "win_chance": 0.00,  "free_prize": 1.00,  "paid_prize": 2.00},
    {"step": 11, "level": 105, "tickets": 6615,   "sess_med": 8,    "sess_eng": 4,  "type": "Sweepstakes",  "win_chance": 0.00,  "free_prize": 0.00,  "paid_prize": 0.00,  "sweep_amt": 1000},
    {"step": 12, "level": 116, "tickets": 7330,   "sess_med": 9,    "sess_eng": 4,  "type": "Instant Win",  "win_chance": 0.00,  "free_prize": 0.50,  "paid_prize": 1.00},
    {"step": 13, "level": 127, "tickets": 8045,   "sess_med": 10,   "sess_eng": 4,  "type": "Instant Win",  "win_chance": 0.00,  "free_prize": 1.50,  "paid_prize": 3.00},
    {"step": 14, "level": 138, "tickets": 8760,   "sess_med": 10,   "sess_eng": 5,  "type": "Instant Win",  "win_chance": 1.00,  "free_prize": 1.00,  "paid_prize": 2.00},
    {"step": 15, "level": 149, "tickets": 9695,   "sess_med": None,  "sess_eng": 5,  "type": "Instant Win",  "win_chance": 0.25,  "free_prize": 0.50,  "paid_prize": 1.00},
    {"step": 16, "level": 160, "tickets": 10630,  "sess_med": None,  "sess_eng": 6,  "type": "Instant Win",  "win_chance": 0.20,  "free_prize": 1.50,  "paid_prize": 3.00},
    {"step": 17, "level": 172, "tickets": 11650,  "sess_med": None,  "sess_eng": 6,  "type": "Sweepstakes",  "win_chance": 0.00,  "free_prize": 0.00,  "paid_prize": 0.00,  "sweep_amt": 10000},
    {"step": 18, "level": 184, "tickets": 12670,  "sess_med": None,  "sess_eng": 7,  "type": "Instant Win",  "win_chance": 0.25,  "free_prize": 1.00,  "paid_prize": 2.00},
    {"step": 19, "level": 196, "tickets": 13690,  "sess_med": None,  "sess_eng": 8,  "type": "Instant Win",  "win_chance": 0.05,  "free_prize": 2.00,  "paid_prize": 5.00},
    {"step": 20, "level": 209, "tickets": 14795,  "sess_med": None,  "sess_eng": 8,  "type": "Instant Win",  "win_chance": 0.25,  "free_prize": 1.00,  "paid_prize": 2.00},
    {"step": 21, "level": 222, "tickets": 15900,  "sess_med": None,  "sess_eng": 9,  "type": "Instant Win",  "win_chance": 0.10,  "free_prize": 1.50,  "paid_prize": 3.00},
    {"step": 22, "level": 235, "tickets": 17005,  "sess_med": None,  "sess_eng": 10, "type": "Instant Win",  "win_chance": 0.20,  "free_prize": 1.00,  "paid_prize": 2.00},
    {"step": 23, "level": 249, "tickets": 18195,  "sess_med": None,  "sess_eng": 10, "type": "Sweepstakes",  "win_chance": 0.00,  "free_prize": 0.00,  "paid_prize": 0.00,  "sweep_amt": 100000},
    {"step": 24, "level": 263, "tickets": 19385,  "sess_med": None,  "sess_eng": 11, "type": "Instant Win",  "win_chance": 0.25,  "free_prize": 1.00,  "paid_prize": 2.00},
    {"step": 25, "level": 277, "tickets": 20575,  "sess_med": None,  "sess_eng": 12, "type": "Instant Win",  "win_chance": 0.10,  "free_prize": 2.00,  "paid_prize": 2.50},
    {"step": 26, "level": 291, "tickets": 21765,  "sess_med": None,  "sess_eng": 15, "type": "Instant Win",  "win_chance": 0.03,  "free_prize": 5.00,  "paid_prize": 10.00},
    {"step": 27, "level": 306, "tickets": 23040,  "sess_med": None,  "sess_eng": 18, "type": "Instant Win",  "win_chance": 0.20,  "free_prize": 1.00,  "paid_prize": 2.00},
    {"step": 28, "level": 321, "tickets": 24315,  "sess_med": None,  "sess_eng": 26, "type": "Sweepstakes",  "win_chance": 0.00,  "free_prize": 0.00,  "paid_prize": 0.00,  "sweep_amt": 1000000},
]


# ===================================================================
# SIDEBAR CONTROLS
# ===================================================================

model_mode = st.sidebar.radio(
    "Model Mode",
    ["Current Model", "Revised Model"],
    index=1,
    help="Current = existing spreadsheet values. Revised = apply Fengxing's feedback."
)

st.sidebar.markdown("---")
st.sidebar.header("Economics")

price_point = st.sidebar.select_slider(
    "Premium Pass Price",
    options=[3.99, 4.99, 6.99, 7.99, 9.99, 12.99, 14.99],
    value=9.99 if model_mode == "Revised Model" else 4.99,
    format_func=lambda x: f"\u00a3{x:.2f}",
)

platform_take = st.sidebar.slider(
    "Platform Take %", min_value=0, max_value=50, value=15, step=1
) / 100

paypal_fee = st.sidebar.number_input(
    "PayPal Fee (\u00a3)", min_value=0.0, max_value=1.0, value=0.08, step=0.01
)

rtp_default = 55 if model_mode == "Revised Model" else 95
target_rtp = st.sidebar.slider(
    "Return to Player (RTP) %", min_value=30, max_value=95, value=rtp_default, step=5,
    help="Current model uses 95%. Fengxing recommends 50-60% for bingo-pace products."
) / 100

st.sidebar.markdown("---")
st.sidebar.header("Player Segments")

free_median_pct = st.sidebar.slider("Free Median %", 0, 100, 50, 5)
free_engaged_pct = st.sidebar.slider("Free Engaged %", 0, 100, 30, 5)
paid_median_pct = st.sidebar.slider("Paid Median %", 0, 100, 5, 1)
paid_engaged_pct = st.sidebar.slider("Paid Engaged %", 0, 100, 15, 1)

total_pct = free_median_pct + free_engaged_pct + paid_median_pct + paid_engaged_pct
if total_pct != 100:
    st.sidebar.warning(f"Segments sum to {total_pct}%, should be 100%")

st.sidebar.markdown("---")
st.sidebar.header("Regulatory")

min_odds_pct = st.sidebar.slider(
    "Minimum Win Chance %", min_value=0.0, max_value=5.0, value=1.0, step=0.1,
    help="ContestPR: no 0% odds. Set floor to 1% (or 0.1% at higher volume)."
)
min_odds = min_odds_pct / 100

st.sidebar.markdown("---")
st.sidebar.header("D7 Retention (Cashout Rate)")

retention_free = st.sidebar.slider(
    "Free Tier D7 Retention %", min_value=0, max_value=100, value=15, step=5,
    help="% of free players still active at D7 who collect winnings"
) / 100

retention_paid = st.sidebar.slider(
    "Paid Tier D7 Retention %", min_value=0, max_value=100, value=30, step=5,
    help="% of paid players still active at D7 who collect winnings"
) / 100

# Revised model controls
if model_mode == "Revised Model":
    st.sidebar.markdown("---")
    st.sidebar.header("Cooldown Mechanic")

    win_steps = st.sidebar.number_input(
        "Win Steps (per cycle)", min_value=1, max_value=5, value=1, step=1
    )
    no_win_steps = st.sidebar.number_input(
        "No-Win Steps (per cycle)", min_value=1, max_value=10, value=5, step=1,
        help="Fengxing: 1 win / 5 no-win = 1-in-6 hit rate"
    )
    cycle_length = win_steps + no_win_steps

    st.sidebar.markdown("---")
    st.sidebar.header("Prize Tuning")

    prize_floor = st.sidebar.number_input(
        "Small Win Floor (\u00a3)", min_value=0.10, max_value=1.00, value=0.25, step=0.05
    )
    prize_ceiling_small = st.sidebar.number_input(
        "Small Win Ceiling (\u00a3)", min_value=0.25, max_value=2.00, value=0.50, step=0.05
    )
    prize_floor_punch = st.sidebar.number_input(
        "Punch Win Floor (\u00a3)", min_value=0.50, max_value=5.00, value=1.00, step=0.25
    )
    prize_ceiling_punch = st.sidebar.number_input(
        "Punch Win Ceiling (\u00a3)", min_value=1.00, max_value=15.00, value=5.00, step=0.50
    )
    small_win_pct = st.sidebar.slider(
        "Small Win % (of all wins)", min_value=50, max_value=100, value=80, step=5,
        help="Fengxing recommends 80% small / 20% punch"
    )
    paid_multiplier = st.sidebar.slider(
        "Paid Prize Multiplier", min_value=1.0, max_value=4.0, value=2.0, step=0.5,
        help="Paid prize = Free prize x this multiplier"
    )


# ===================================================================
# MODEL CALCULATION
# ===================================================================

def compute_model_from_df(df, params):
    """Compute wallet/EV from an editable DataFrame. Works for both modes."""
    results = []
    w_fm, w_fe, w_pm, w_pe = 0.0, 0.0, 0.0, 0.0
    min_odds = params.get("min_odds", 0.0)

    for _, row in df.iterrows():
        r = row.to_dict()
        is_sweep = r["type"] == "Sweepstakes"

        if is_sweep:
            win_chance = 0.0
            free_prize = 0.0
            paid_prize = 0.0
        else:
            win_chance = max(r["win_chance"], min_odds) if r["win_chance"] < 1.0 else r["win_chance"]
            free_prize = r["free_prize"]
            paid_prize = r["paid_prize"]

        ev_free = free_prize * win_chance
        ev_paid = paid_prize * win_chance

        sess_med = r.get("sess_med")
        if sess_med is not None and not (isinstance(sess_med, float) and np.isnan(sess_med)):
            w_fm += ev_free
            w_pm += ev_paid
        w_fe += ev_free
        w_pe += ev_paid

        r["win_chance_effective"] = win_chance
        r["ev_free"] = ev_free
        r["ev_paid"] = ev_paid
        r["w_fm"] = w_fm
        r["w_fe"] = w_fe
        r["w_pm"] = w_pm
        r["w_pe"] = w_pe
        results.append(r)

    return results


def compute_economics(results, params):
    """Compute segment-level economics and overall position.

    Formula (matches their spreadsheet):
    - Expected Payout = Wallet * D7 Retention Rate
    - Net Position = Gross Income - Expected Payout
    - Contribution = Net Position * Segment Incidence
    """
    last = results[-1]
    last_med = [r for r in results if r["sess_med"] is not None][-1]

    # Also compute "Prize Available" for informational purposes
    remainder_paid = params["price_point"] * (1 - params["platform_take"])
    prize_available = (remainder_paid - params["paypal_fee"]) * params["target_rtp"]

    segments = [
        ("Free Median",   last_med["w_fm"], 0.0,                  params["retention_free"],  params["free_median_pct"] / 100),
        ("Free Engaged",  last["w_fe"],     0.0,                  params["retention_free"],  params["free_engaged_pct"] / 100),
        ("Paid Median",   last_med["w_pm"], params["price_point"], params["retention_paid"],  params["paid_median_pct"] / 100),
        ("Paid Engaged",  last["w_pe"],     params["price_point"], params["retention_paid"],  params["paid_engaged_pct"] / 100),
    ]

    overall = 0.0
    total_blended_payout = 0.0
    total_blended_income = 0.0
    rows = []

    for name, total_exp, income, retention, incidence in segments:
        expected_payout = total_exp * retention
        net_pos = income - expected_payout
        contribution = net_pos * incidence
        overall += contribution

        # Track blended totals for RTP calc
        total_blended_payout += expected_payout * incidence
        total_blended_income += income * incidence

        rows.append({
            "Segment": name,
            "Exp. Wallet": f"\u00a3{total_exp:.2f}",
            "Income": f"\u00a3{income:.2f}",
            "D7 Retention": f"{retention*100:.0f}%",
            "Expected Payout": f"\u00a3{expected_payout:.2f}",
            "Net Position": f"\u00a3{net_pos:.2f}",
            "Incidence": f"{incidence*100:.0f}%",
            "Contribution": f"\u00a3{contribution:.2f}",
        })

    # Calculate effective RTP from actual prize schedule
    # RTP = total blended payout / total blended income
    calculated_rtp = (total_blended_payout / total_blended_income * 100) if total_blended_income > 0 else 0.0

    return rows, overall, prize_available, calculated_rtp


# Build params
params = {
    "price_point": price_point,
    "platform_take": platform_take,
    "paypal_fee": paypal_fee,
    "target_rtp": target_rtp,
    "min_odds": min_odds,
    "retention_free": retention_free,
    "retention_paid": retention_paid,
    "free_median_pct": free_median_pct,
    "free_engaged_pct": free_engaged_pct,
    "paid_median_pct": paid_median_pct,
    "paid_engaged_pct": paid_engaged_pct,
}

if model_mode == "Revised Model":
    params.update({
        "cycle_length": cycle_length,
        "win_steps": win_steps,
        "no_win_steps": no_win_steps,
        "prize_floor": prize_floor,
        "prize_ceiling_small": prize_ceiling_small,
        "prize_floor_punch": prize_floor_punch,
        "prize_ceiling_punch": prize_ceiling_punch,
        "small_win_pct": small_win_pct,
        "paid_multiplier": paid_multiplier,
    })

# Prepare the editable DataFrame
if model_mode == "Current Model":
    base_df = pd.DataFrame(CURRENT_STEPS)
else:
    # Generate revised step data using cooldown + prize structure
    revised_rows = []
    instant_idx = 0
    for s in CURRENT_STEPS:
        row = {**s}
        if s["type"] != "Sweepstakes":
            if s["step"] == 1:
                row["win_chance"] = 1.0
            else:
                pos = instant_idx % params["cycle_length"]
                row["win_chance"] = 1.0 if pos < params["win_steps"] else 0.0
            instant_idx += 1

            punch_every = max(1, round(100 / max(1, 100 - params["small_win_pct"])))
            if instant_idx % punch_every == 0:
                progress = s["step"] / 28
                row["free_prize"] = round((params["prize_floor_punch"] + progress * (params["prize_ceiling_punch"] - params["prize_floor_punch"])) * 4) / 4
            else:
                progress = s["step"] / 28
                row["free_prize"] = round((params["prize_floor"] + progress * (params["prize_ceiling_small"] - params["prize_floor"])) * 4) / 4
            row["paid_prize"] = round(row["free_prize"] * params["paid_multiplier"] * 4) / 4
        revised_rows.append(row)
    base_df = pd.DataFrame(revised_rows)

# Run model from the base data first (before user edits)
results = compute_model_from_df(base_df, params)
econ_rows, overall_position, prize_available, calculated_rtp = compute_economics(results, params)


# ===================================================================
# DISPLAY
# ===================================================================

# Key metrics row
st.markdown("---")
c1, c2, c3, c4, c5, c6 = st.columns(6)

net_rev = price_point * (1 - platform_take) - paypal_fee
with c1:
    st.metric("Pass Price", f"\u00a3{price_point:.2f}")
with c2:
    st.metric("Net Rev / Paid User", f"\u00a3{net_rev:.2f}")
with c3:
    st.metric("RTP (Target)", f"{target_rtp*100:.0f}%")
with c4:
    rtp_delta = calculated_rtp - (target_rtp * 100)
    st.metric(
        "RTP (Actual)",
        f"{calculated_rtp:.0f}%",
        delta=f"{rtp_delta:+.0f}% vs target",
        delta_color="inverse" if calculated_rtp > target_rtp * 100 else "normal",
        help="Calculated from current prize schedule. Lower is better for the business."
    )
with c5:
    if model_mode == "Revised Model":
        st.metric("Hit Rate", f"1 in {cycle_length}")
    else:
        st.metric("Hit Rate", "Variable")
with c6:
    st.metric(
        "Overall Position",
        f"\u00a3{overall_position:.2f}",
        delta="Profit" if overall_position >= 0 else "Loss",
        delta_color="normal" if overall_position >= 0 else "inverse",
    )

# Battle pass table - EDITABLE
st.markdown("---")
st.subheader("Battle Pass Steps (edit values below)")
st.caption("Change any Win %, Free Prize, or Paid Prize value and the economics will recalculate automatically.")

# Prepare editable columns (only show editable fields + context)
edit_df = pd.DataFrame([{
    "Step": r["step"],
    "Level": r.get("level", ""),
    "Tickets": r["tickets"],
    "Type": r["type"],
    "Win % (input)": r["win_chance"] * 100,
    "Free Prize": r["free_prize"] if r["type"] != "Sweepstakes" else 0.0,
    "Paid Prize": r["paid_prize"] if r["type"] != "Sweepstakes" else 0.0,
} for r in results])

# Let user edit the key columns
st.caption("Edit **Win %**, **Free Prize**, and **Paid Prize** below. The results table underneath will update automatically.")
edited_df = st.data_editor(
    edit_df,
    use_container_width=True,
    hide_index=True,
    disabled=["Step", "Level", "Tickets", "Type"],
    column_config={
        "Step": st.column_config.NumberColumn("Step", width="small"),
        "Level": st.column_config.NumberColumn("Level", width="small"),
        "Tickets": st.column_config.NumberColumn("Tickets", format="%d"),
        "Win % (input)": st.column_config.NumberColumn("Win %", min_value=0, max_value=100, step=0.5, format="%.1f%%",
            help="Set your desired win chance. Values below the regulatory minimum will be bumped up automatically."),
        "Free Prize": st.column_config.NumberColumn("Free Prize", min_value=0, max_value=100, step=0.25, format="\u00a3%.2f"),
        "Paid Prize": st.column_config.NumberColumn("Paid Prize", min_value=0, max_value=200, step=0.25, format="\u00a3%.2f"),
    },
    key="step_editor",
)

# Recalculate from edited values
recalc_df = base_df.copy()
for i, row in edited_df.iterrows():
    if i < len(recalc_df):
        recalc_df.at[i, "win_chance"] = row["Win % (input)"] / 100
        recalc_df.at[i, "free_prize"] = row["Free Prize"]
        recalc_df.at[i, "paid_prize"] = row["Paid Prize"]

results = compute_model_from_df(recalc_df, params)
econ_rows, overall_position, prize_available, calculated_rtp = compute_economics(results, params)

# Show recalculated results table
st.markdown("---")
st.subheader("Recalculated Step Economics")
st.caption("These values reflect your edits above and update automatically.")

recalc_display = pd.DataFrame([{
    "Step": r["step"],
    "Type": r["type"],
    "Win % (eff.)": f"{r['win_chance_effective']*100:.1f}%",
    "Free Prize": f"\u00a3{r['free_prize']:.2f}" if r["type"] != "Sweepstakes" else f"\u00a3{r.get('sweep_amt', 0):,.0f} sweep",
    "Paid Prize": f"\u00a3{r['paid_prize']:.2f}" if r["type"] != "Sweepstakes" else f"\u00a3{r.get('sweep_amt', 0):,.0f} sweep",
    "EV Free": f"\u00a3{r['ev_free']:.4f}",
    "EV Paid": f"\u00a3{r['ev_paid']:.4f}",
    "Wallet (Free Eng)": f"\u00a3{r['w_fe']:.2f}",
    "Wallet (Paid Eng)": f"\u00a3{r['w_pe']:.2f}",
} for r in results])
st.dataframe(recalc_display, use_container_width=True, hide_index=True)

# Economics table
st.markdown("---")
st.subheader("Economic Summary by Segment")
st.dataframe(pd.DataFrame(econ_rows), use_container_width=True, hide_index=True)

if overall_position < 0:
    st.error(f"Blended position: **\u00a3{overall_position:.2f}** per player. "
             f"The model is losing money at these settings.")
else:
    st.success(f"Blended position: **\u00a3{overall_position:.2f}** per player. "
               f"The model is profitable at these settings.")

# RTP summary after edits
rtp_col1, rtp_col2, rtp_col3 = st.columns(3)
with rtp_col1:
    st.metric("Actual RTP (from prize schedule)", f"{calculated_rtp:.0f}%")
with rtp_col2:
    st.metric("Target RTP (Fengxing)", f"{target_rtp*100:.0f}%")
with rtp_col3:
    rtp_gap = calculated_rtp - (target_rtp * 100)
    if rtp_gap > 10:
        st.metric("RTP Gap", f"{rtp_gap:+.0f}%", delta="Too high", delta_color="inverse")
    elif rtp_gap > 0:
        st.metric("RTP Gap", f"{rtp_gap:+.0f}%", delta="Slightly over target", delta_color="inverse")
    else:
        st.metric("RTP Gap", f"{rtp_gap:+.0f}%", delta="At or below target", delta_color="normal")

# Quick comparison for revised mode
if model_mode == "Revised Model":
    st.markdown("---")
    st.subheader("Quick Comparison: Current vs Revised")

    # Run current model for comparison
    current_base_df = pd.DataFrame(CURRENT_STEPS)
    current_params = {**params, "price_point": 4.99, "min_odds": 0.0}
    current_results = compute_model_from_df(current_base_df, current_params)
    current_econ, current_overall, _, current_calc_rtp = compute_economics(current_results, current_params)

    comp_c1, comp_c2, comp_c3 = st.columns(3)
    with comp_c1:
        st.metric(
            "Current Overall Position",
            f"\u00a3{current_overall:.2f}",
        )
    with comp_c2:
        st.metric(
            "Revised Overall Position",
            f"\u00a3{overall_position:.2f}",
        )
    with comp_c3:
        delta = overall_position - current_overall
        st.metric(
            "Improvement",
            f"\u00a3{delta:.2f}",
            delta=f"\u00a3{delta:.2f}",
            delta_color="normal" if delta >= 0 else "inverse",
        )

    # Wallet comparison
    current_paid_eng_wallet = current_results[-1]["w_pe"]
    revised_paid_eng_wallet = results[-1]["w_pe"]

    comp_c4, comp_c5, comp_c6 = st.columns(3)
    with comp_c4:
        st.metric("Current Paid Eng. Wallet", f"\u00a3{current_paid_eng_wallet:.2f}")
    with comp_c5:
        st.metric("Revised Paid Eng. Wallet", f"\u00a3{revised_paid_eng_wallet:.2f}")
    with comp_c6:
        wallet_delta = revised_paid_eng_wallet - current_paid_eng_wallet
        st.metric(
            "Wallet Change",
            f"\u00a3{wallet_delta:.2f}",
            delta=f"\u00a3{wallet_delta:.2f}",
            delta_color="inverse" if wallet_delta > 0 else "normal",  # Lower wallet = better for house
        )


# ===================================================================
# CHARTS
# ===================================================================
st.markdown("---")
st.subheader("Expected Wallet Progression (Engaged Players)")

fig_wallet = go.Figure()
fig_wallet.add_trace(go.Scatter(
    x=[r["step"] for r in results],
    y=[r["w_fe"] for r in results],
    name="Free Engaged",
    mode="lines+markers",
    line=dict(color="#636EFA"),
))
fig_wallet.add_trace(go.Scatter(
    x=[r["step"] for r in results],
    y=[r["w_pe"] for r in results],
    name="Paid Engaged",
    mode="lines+markers",
    line=dict(color="#EF553B"),
))

# Add net revenue line for reference
fig_wallet.add_hline(
    y=net_rev,
    line_dash="dash",
    line_color="green",
    annotation_text=f"Net Revenue (\u00a3{net_rev:.2f})",
)

fig_wallet.update_layout(
    xaxis_title="Step",
    yaxis_title="Expected Wallet (\u00a3)",
    height=400,
    template="plotly_white",
)
st.plotly_chart(fig_wallet, use_container_width=True)


# Win probability chart
st.subheader("Win Probability by Step")

instant_steps = [r for r in results if r["type"] != "Sweepstakes"]
colors = ["#2ecc71" if r["win_chance_effective"] > min_odds else "#f39c12" if r["win_chance_effective"] > 0 else "#e74c3c" for r in instant_steps]

fig_win = go.Figure()
fig_win.add_trace(go.Bar(
    x=[r["step"] for r in instant_steps],
    y=[r["win_chance_effective"] * 100 for r in instant_steps],
    marker_color=colors,
    name="Win % (effective)",
))
fig_win.update_layout(
    xaxis_title="Step",
    yaxis_title="Win Chance (%)",
    height=350,
    template="plotly_white",
    yaxis=dict(range=[0, 105]),
)
st.plotly_chart(fig_win, use_container_width=True)


# Prize value chart
st.subheader("Prize Values by Step")

fig_prize = make_subplots(specs=[[{"secondary_y": True}]])
fig_prize.add_trace(go.Bar(
    x=[r["step"] for r in instant_steps],
    y=[r["free_prize"] for r in instant_steps],
    name="Free Prize",
    marker_color="#636EFA",
    opacity=0.7,
), secondary_y=False)
fig_prize.add_trace(go.Bar(
    x=[r["step"] for r in instant_steps],
    y=[r["paid_prize"] for r in instant_steps],
    name="Paid Prize",
    marker_color="#EF553B",
    opacity=0.7,
), secondary_y=False)
fig_prize.update_layout(
    xaxis_title="Step",
    height=350,
    template="plotly_white",
    barmode="group",
)
fig_prize.update_yaxes(title_text="Prize Value (\u00a3)", secondary_y=False)
st.plotly_chart(fig_prize, use_container_width=True)


# ===================================================================
# WEEK 1 / WEEK 2 ANALYSIS
# ===================================================================
st.markdown("---")
st.subheader("Week 1 vs Week 2 Economics")
st.caption("Based on session counts: Week 1 = sessions reachable in ~7 days")

# Estimate week 1 boundary: engaged player at ~7 sessions
# From the data, sess_eng goes 1,1,1,1,1,1,2,2,2,3,4,4,4,5...
# Cumulative sessions for engaged player
cum_sessions = 0
week1_boundary = len(results)  # Default to all steps
for i, r in enumerate(results):
    cum_sessions += r["sess_eng"]
    if cum_sessions > 7:
        week1_boundary = i
        break

week1_steps = results[:week1_boundary]
week2_steps = results[week1_boundary:]

if week1_steps:
    w1_wallet_paid = week1_steps[-1]["w_pe"]
    w1_wallet_free = week1_steps[-1]["w_fe"]
else:
    w1_wallet_paid = 0
    w1_wallet_free = 0

w2_wallet_paid = results[-1]["w_pe"] - w1_wallet_paid if week2_steps else 0
w2_wallet_free = results[-1]["w_fe"] - w1_wallet_free if week2_steps else 0

wk_c1, wk_c2, wk_c3, wk_c4 = st.columns(4)
with wk_c1:
    st.metric("Week 1 Steps", len(week1_steps))
with wk_c2:
    st.metric("Week 1 Paid Wallet", f"\u00a3{w1_wallet_paid:.2f}")
with wk_c3:
    st.metric("Week 2 Steps", len(week2_steps))
with wk_c4:
    st.metric("Week 2 Paid Wallet Added", f"\u00a3{w2_wallet_paid:.2f}")

# Week 1 P&L
w1_income = price_point * (paid_median_pct + paid_engaged_pct) / 100
w1_net_income = w1_income * (1 - platform_take) - paypal_fee * (paid_median_pct + paid_engaged_pct) / 100
w1_payout = (w1_wallet_free * (1 - retention_free) * (free_median_pct + free_engaged_pct) / 100 +
             w1_wallet_paid * (1 - retention_paid) * (paid_median_pct + paid_engaged_pct) / 100)
w1_net = w1_net_income - w1_payout

wk_c5, wk_c6, wk_c7 = st.columns(3)
with wk_c5:
    st.metric("Week 1 Blended Income", f"\u00a3{w1_net_income:.2f}")
with wk_c6:
    st.metric("Week 1 Blended Payout", f"\u00a3{w1_payout:.2f}")
with wk_c7:
    st.metric(
        "Week 1 Net",
        f"\u00a3{w1_net:.2f}",
        delta="Profit" if w1_net >= 0 else "Loss",
        delta_color="normal" if w1_net >= 0 else "inverse",
    )

if w1_net_income > 0:
    w1_loss_pct = (w1_net / w1_net_income) * 100
    st.info(f"Week 1 loss as % of income: **{w1_loss_pct:.1f}%** (Fengxing target: manageable at ~10%)")


st.markdown("---")
st.caption("Molly's Cash Battle Pass Model | Built for TXG | v2.0")
