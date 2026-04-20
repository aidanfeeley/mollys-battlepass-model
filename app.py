import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

st.set_page_config(page_title="Molly's Cash Battle Pass Model", layout="wide")
st.title("Molly's Cash Battle Pass Model")
st.caption("Tune win chances, prize values, and economic assumptions to model the battle pass P&L. "
           "Edit the table directly to adjust individual steps, or use the sidebar to change global settings.")

# ===================================================================
# SAVED MODELS (session state)
# ===================================================================
if "saved_models" not in st.session_state:
    st.session_state.saved_models = {}

# ===================================================================
# CURRENT MODEL DATA (exact match to their spreadsheet)
# ===================================================================

CURRENT_STEPS = [
    # FTUE (Steps 1-14): Scripted guaranteed wins with punchier step 1
    # Step 1: Big hook — paid player sees £3.00 right away (12x the old £0.25), free gets £1.00
    # Divergence is intentional: conversion hook to get free players to buy the pass
    {"step": 1,  "level": 1,   "tickets": 50,     "sess_med": 1,    "sess_eng": 1,  "type": "Instant Win",  "win_chance": 1.00,  "free_prize": 1.00,  "paid_prize": 3.00},
    {"step": 2,  "level": 11,  "tickets": 550,    "sess_med": 1,    "sess_eng": 1,  "type": "Instant Win",  "win_chance": 0.01,  "free_prize": 0.10,  "paid_prize": 0.25},
    {"step": 3,  "level": 21,  "tickets": 1155,   "sess_med": 1,    "sess_eng": 1,  "type": "Instant Win",  "win_chance": 1.00,  "free_prize": 0.25,  "paid_prize": 0.75},
    {"step": 4,  "level": 31,  "tickets": 1805,   "sess_med": 2,    "sess_eng": 1,  "type": "Instant Win",  "win_chance": 0.01,  "free_prize": 0.10,  "paid_prize": 0.25},
    {"step": 5,  "level": 41,  "tickets": 2455,   "sess_med": 3,    "sess_eng": 1,  "type": "Instant Win",  "win_chance": 1.00,  "free_prize": 0.25,  "paid_prize": 0.75},
    {"step": 6,  "level": 51,  "tickets": 3105,   "sess_med": 3,    "sess_eng": 1,  "type": "Sweepstakes",  "win_chance": 0.00,  "free_prize": 0.00,  "paid_prize": 0.00,  "sweep_amt": 100},
    {"step": 7,  "level": 61,  "tickets": 3755,   "sess_med": 4,    "sess_eng": 2,  "type": "Instant Win",  "win_chance": 0.01,  "free_prize": 0.10,  "paid_prize": 0.25},
    {"step": 8,  "level": 72,  "tickets": 4470,   "sess_med": 5,    "sess_eng": 2,  "type": "Instant Win",  "win_chance": 1.00,  "free_prize": 0.25,  "paid_prize": 0.50},
    {"step": 9,  "level": 83,  "tickets": 5185,   "sess_med": 6,    "sess_eng": 2,  "type": "Instant Win",  "win_chance": 0.01,  "free_prize": 0.10,  "paid_prize": 0.25},
    {"step": 10, "level": 94,  "tickets": 5900,   "sess_med": 7,    "sess_eng": 3,  "type": "Instant Win",  "win_chance": 1.00,  "free_prize": 0.25,  "paid_prize": 0.50},
    {"step": 11, "level": 105, "tickets": 6615,   "sess_med": 8,    "sess_eng": 4,  "type": "Sweepstakes",  "win_chance": 0.00,  "free_prize": 0.00,  "paid_prize": 0.00,  "sweep_amt": 1000},
    {"step": 12, "level": 116, "tickets": 7330,   "sess_med": 9,    "sess_eng": 4,  "type": "Instant Win",  "win_chance": 0.01,  "free_prize": 0.10,  "paid_prize": 0.25},
    {"step": 13, "level": 127, "tickets": 8045,   "sess_med": 10,   "sess_eng": 4,  "type": "Instant Win",  "win_chance": 0.01,  "free_prize": 0.10,  "paid_prize": 0.25},
    {"step": 14, "level": 138, "tickets": 8760,   "sess_med": 10,   "sess_eng": 5,  "type": "Instant Win",  "win_chance": 1.00,  "free_prize": 0.25,  "paid_prize": 0.50},
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

# Model selector: built-in modes + any saved models
saved_names = list(st.session_state.saved_models.keys())
mode_options = ["Current Model", "Revised Model"] + saved_names

model_mode = st.sidebar.radio(
    "Model Mode",
    mode_options,
    index=1,
    help="Current = existing spreadsheet values. Revised = apply Fengxing's feedback. Saved models appear below."
)

# Determine if we're loading a saved model
is_saved = model_mode in st.session_state.saved_models
saved = st.session_state.saved_models.get(model_mode, {}) if is_saved else {}
is_revised = model_mode == "Revised Model" or is_saved  # Saved models use revised structure

# --- Save / Load / Export / Import ---
st.sidebar.markdown("---")
st.sidebar.header("Save & Load")

save_col1, save_col2 = st.sidebar.columns(2)
with save_col1:
    save_name = st.text_input("Model name", key="save_name_input", label_visibility="collapsed", placeholder="Name your model...")
with save_col2:
    save_clicked = st.button("Save", use_container_width=True)

# Delete saved model
if is_saved:
    if st.sidebar.button(f"Delete '{model_mode}'", use_container_width=True):
        del st.session_state.saved_models[model_mode]
        st.rerun()

# Export / Import
st.sidebar.markdown("---")
export_col, import_col = st.sidebar.columns(2)

with export_col:
    if st.session_state.saved_models:
        export_data = json.dumps(st.session_state.saved_models, indent=2)
        st.download_button(
            "Export All",
            data=export_data,
            file_name="battlepass_models.json",
            mime="application/json",
            use_container_width=True,
        )

with import_col:
    uploaded = st.file_uploader("Import", type="json", label_visibility="collapsed", key="import_file")
    if uploaded is not None:
        try:
            raw = uploaded.read()
            if raw:  # guard against empty read
                imported = json.loads(raw)
                if imported and isinstance(imported, dict):
                    # Check if these models are already loaded to avoid redundant reruns
                    new_models = {k: v for k, v in imported.items()
                                  if k not in st.session_state.saved_models}
                    if new_models:
                        st.session_state.saved_models.update(imported)
                        st.sidebar.success(f"Imported {len(imported)} model(s)")
                        st.rerun()
                    else:
                        st.sidebar.info("Models already loaded.")
                else:
                    st.sidebar.error("JSON file is empty or not a valid model export.")
        except (json.JSONDecodeError, Exception) as e:
            st.sidebar.error(f"Invalid JSON file: {e}")

st.sidebar.markdown("---")
st.sidebar.header("Economics")

# Get defaults: from saved model if loading, otherwise from mode
def get_default(key, revised_val, current_val):
    if is_saved and key in saved.get("settings", {}):
        return saved["settings"][key]
    return revised_val if model_mode == "Revised Model" else current_val

pass_duration_weeks = st.sidebar.radio(
    "Battle Pass Duration",
    options=[1, 2],
    index=0 if get_default("pass_duration_weeks", 1, 1) == 1 else 1,
    format_func=lambda x: f"{x} Week{'s' if x > 1 else ''} ({x * 7} days)",
    help="1 week = 7-day season (current plan). 2 weeks = 14-day season. "
         "Affects income timing, multi-week carryover, and step completion expectations."
)
pass_duration_days = pass_duration_weeks * 7

price_point = st.sidebar.select_slider(
    "Premium Pass Price",
    options=[3.99, 4.99, 6.99, 7.99, 9.99, 12.99, 14.99],
    value=get_default("price_point", 9.99, 4.99),
    format_func=lambda x: f"\u00a3{x:.2f}",
)

platform_take = st.sidebar.slider(
    "Platform Take %", min_value=0, max_value=50,
    value=get_default("platform_take_pct", 15, 15), step=1
) / 100

paypal_fee = st.sidebar.number_input(
    "PayPal Fee (\u00a3)", min_value=0.0, max_value=1.0,
    value=get_default("paypal_fee", 0.08, 0.08), step=0.01
)

target_rtp = st.sidebar.slider(
    "Target RTP %", min_value=30, max_value=95,
    value=get_default("target_rtp_pct", 55, 95), step=5,
    help="Fengxing recommends 50-60% for bingo-pace products."
) / 100

st.sidebar.markdown("---")
st.sidebar.header("Player Mix")

paid_conversion_pct = st.sidebar.slider(
    "Paid Conversion %", min_value=1, max_value=50,
    value=get_default("paid_conversion_pct", 20, 20), step=1,
    help="What % of total players buy the premium pass."
)
free_pct = 100 - paid_conversion_pct

st.sidebar.markdown("---")
st.sidebar.header("Step Completion (Free Players)")
st.sidebar.caption("% of free players who reach each milestone step.")

free_step7 = st.sidebar.slider("Free → Step 7", 0, 100,
    get_default("free_step7", 60, 60), 5, help="% of free players reaching step 7") / 100
free_step14 = st.sidebar.slider("Free → Step 14", 0, 100,
    get_default("free_step14", 30, 30), 5, help="% of free players reaching step 14 (end of FTUE)") / 100
free_step21 = st.sidebar.slider("Free → Step 21", 0, 100,
    get_default("free_step21", 10, 10), 5, help="% of free players reaching step 21") / 100
free_step28 = st.sidebar.slider("Free → Step 28", 0, 100,
    get_default("free_step28", 3, 3), 1, help="% of free players completing the full pass") / 100

st.sidebar.markdown("---")
st.sidebar.header("Step Completion (Paid Players)")
st.sidebar.caption("% of paid players who reach each milestone step.")

paid_step7 = st.sidebar.slider("Paid → Step 7", 0, 100,
    get_default("paid_step7", 90, 90), 5, help="% of paid players reaching step 7") / 100
paid_step14 = st.sidebar.slider("Paid → Step 14", 0, 100,
    get_default("paid_step14", 70, 70), 5, help="% of paid players reaching step 14 (end of FTUE)") / 100
paid_step21 = st.sidebar.slider("Paid → Step 21", 0, 100,
    get_default("paid_step21", 40, 40), 5, help="% of paid players reaching step 21") / 100
paid_step28 = st.sidebar.slider("Paid → Step 28", 0, 100,
    get_default("paid_step28", 20, 20), 5, help="% of paid players completing the full pass") / 100

# Validate step completion curves are monotonically decreasing
_free_steps = [free_step7, free_step14, free_step21, free_step28]
_paid_steps = [paid_step7, paid_step14, paid_step21, paid_step28]
_step_labels = ["Step 7", "Step 14", "Step 21", "Step 28"]
for label, vals in [("Free", _free_steps), ("Paid", _paid_steps)]:
    for i in range(1, len(vals)):
        if vals[i] > vals[i - 1]:
            st.sidebar.warning(
                f"{label}: {_step_labels[i]} ({vals[i]*100:.0f}%) > {_step_labels[i-1]} ({vals[i-1]*100:.0f}%). "
                f"Fewer players should reach later steps."
            )
            break

st.sidebar.markdown("---")
cashout_label = "Single-Season Cashout Rate" if pass_duration_weeks == 2 else "D7 Cashout Rate"
st.sidebar.header(cashout_label)
st.sidebar.caption("Used for single-season economics. Multi-week section uses the full retention curve.")

_cashout_suffix = f"D{pass_duration_days}" if pass_duration_weeks == 2 else "D7"
retention_free = st.sidebar.slider(
    f"Free Tier {_cashout_suffix} Cashout %", min_value=0, max_value=100,
    value=get_default("retention_free_pct", 15, 15), step=5,
    help=f"% of free players who actually cash out by end of a {pass_duration_days}-day season."
) / 100

retention_paid = st.sidebar.slider(
    f"Paid Tier {_cashout_suffix} Cashout %", min_value=0, max_value=100,
    value=get_default("retention_paid_pct", 30, 30), step=5,
    help=f"% of paid players who actually cash out by end of a {pass_duration_days}-day season."
) / 100

st.sidebar.markdown("---")
st.sidebar.header("Cashout Threshold")

cashout_threshold = st.sidebar.slider(
    "Minimum Cashout (£)", min_value=10.0, max_value=50.0,
    value=get_default("cashout_threshold", 20.0, 20.0), step=5.0,
    help="Players must accumulate at least this much in their wallet before they can withdraw. "
         "Balance below the threshold carries over to the next weekly season."
)

# Revised / Saved model controls
if is_revised:
    st.sidebar.markdown("---")
    st.sidebar.header("Cooldown Mechanic")

    win_steps = st.sidebar.number_input(
        "Win Steps (per cycle)", min_value=1, max_value=5,
        value=get_default("win_steps", 1, 1), step=1
    )
    no_win_steps = st.sidebar.number_input(
        "No-Win Steps (per cycle)", min_value=1, max_value=10,
        value=get_default("no_win_steps", 4, 4), step=1,
        help="Fengxing: 50% base + 4-step cooldown = 1-in-5 hit rate"
    )
    cycle_length = win_steps + no_win_steps

    st.sidebar.markdown("---")
    paid_multiplier = st.sidebar.slider(
        "Paid Prize Multiplier", min_value=1.0, max_value=4.0,
        value=get_default("paid_multiplier", 2.0, 2.0), step=0.5,
        help="Paid prize = Free prize x this multiplier. Applied when generating revised model."
    )


# ===================================================================
# MODEL CALCULATION
# ===================================================================

def compute_model_from_df(df, params):
    """Compute wallet/EV from an editable DataFrame. Works for both modes."""
    results = []
    w_fm, w_fe, w_pm, w_pe = 0.0, 0.0, 0.0, 0.0

    for _, row in df.iterrows():
        r = row.to_dict()
        is_sweep = r["type"] == "Sweepstakes"

        if is_sweep:
            win_chance = 0.0
            free_prize = 0.0
            paid_prize = 0.0
        else:
            win_chance = r["win_chance"]
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


def compute_weighted_wallet(results, step_completions, wallet_key):
    """Compute weighted average wallet using step completion distribution.

    step_completions: dict of {step: pct_reaching} e.g. {7: 0.90, 14: 0.70, 21: 0.40, 28: 0.20}
    wallet_key: 'w_fe' for free, 'w_pe' for paid

    The distribution creates tiers:
    - Don't reach step 7:           (1 - pct_step7)       × wallet at step 1
    - Reach step 7 but not 14:      (pct_step7 - pct_14)  × wallet at step 7
    - Reach step 14 but not 21:     (pct_14 - pct_21)     × wallet at step 14
    - Reach step 21 but not 28:     (pct_21 - pct_28)     × wallet at step 21
    - Complete step 28:             pct_28                  × wallet at step 28
    """
    milestones = sorted(step_completions.keys())  # [7, 14, 21, 28]

    # Build wallet lookup: wallet value at each step from results
    wallet_at_step = {}
    for r in results:
        wallet_at_step[r["step"]] = r[wallet_key]

    # Tier weights and wallets
    weighted_wallet = 0.0
    prev_pct = 1.0  # everyone starts
    for ms in milestones:
        pct_reaching = step_completions[ms]
        tier_weight = prev_pct - pct_reaching  # fraction who stop before this milestone
        # Use the wallet at the previous milestone (or step 1 for the first tier)
        prev_step = milestones[milestones.index(ms) - 1] if milestones.index(ms) > 0 else 1
        tier_wallet = wallet_at_step.get(prev_step, 0.0)
        weighted_wallet += tier_weight * tier_wallet
        prev_pct = pct_reaching

    # Final tier: players who complete the last milestone
    weighted_wallet += prev_pct * wallet_at_step.get(milestones[-1], 0.0)

    return weighted_wallet


def compute_economics(results, params):
    """Compute economics using step completion distributions for weighted wallets.

    Formula:
    - Weighted Wallet = weighted average based on step completion distribution
    - Expected Payout = Weighted Wallet × D7 Cashout Rate
    - Net Position = Income − Expected Payout
    - Contribution = Net Position × Incidence (free% or paid%)
    """
    # Compute weighted wallets from step completion curves
    free_completions = {7: params["free_step7"], 14: params["free_step14"],
                        21: params["free_step21"], 28: params["free_step28"]}
    paid_completions = {7: params["paid_step7"], 14: params["paid_step14"],
                        21: params["paid_step21"], 28: params["paid_step28"]}

    free_weighted_wallet = compute_weighted_wallet(results, free_completions, "w_fe")
    paid_weighted_wallet = compute_weighted_wallet(results, paid_completions, "w_pe")

    free_incidence = params["free_pct"] / 100
    paid_incidence = params["paid_conversion_pct"] / 100

    # Use net income (after platform take and PayPal fee) — not gross price
    net_income_paid = params["price_point"] * (1 - params["platform_take"]) - params["paypal_fee"]

    segments = [
        ("Free Players",  free_weighted_wallet, 0.0,              params["retention_free"],  free_incidence),
        ("Paid Players",  paid_weighted_wallet, net_income_paid,  params["retention_paid"],  paid_incidence),
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

        total_blended_payout += expected_payout * incidence
        total_blended_income += income * incidence

        cashout_col_name = f"D{params['pass_duration_days']} Cashout" if params["pass_duration_days"] != 7 else "D7 Cashout"
        rows.append({
            "Segment": name,
            "Wtd. Wallet": f"\u00a3{total_exp:.2f}",
            "Income": f"\u00a3{income:.2f}",
            cashout_col_name: f"{retention*100:.0f}%",
            "Expected Payout": f"\u00a3{expected_payout:.2f}",
            "Net Position": f"\u00a3{net_pos:.2f}",
            "Incidence": f"{incidence*100:.0f}%",
            "Contribution": f"\u00a3{contribution:.2f}",
        })

    calculated_rtp = (total_blended_payout / total_blended_income * 100) if total_blended_income > 0 else 0.0

    return rows, overall, calculated_rtp


# Build params
params = {
    "pass_duration_weeks": pass_duration_weeks,
    "pass_duration_days": pass_duration_days,
    "price_point": price_point,
    "platform_take": platform_take,
    "paypal_fee": paypal_fee,
    "target_rtp": target_rtp,
    "retention_free": retention_free,
    "retention_paid": retention_paid,
    "paid_conversion_pct": paid_conversion_pct,
    "free_pct": free_pct,
    "free_step7": free_step7,
    "free_step14": free_step14,
    "free_step21": free_step21,
    "free_step28": free_step28,
    "paid_step7": paid_step7,
    "paid_step14": paid_step14,
    "paid_step21": paid_step21,
    "paid_step28": paid_step28,
    "cashout_threshold": cashout_threshold,
}

if is_revised:
    params.update({
        "cycle_length": cycle_length,
        "win_steps": win_steps,
        "no_win_steps": no_win_steps,
        "paid_multiplier": paid_multiplier,
    })

# Prepare the editable DataFrame
if model_mode == "Current Model":
    base_df = pd.DataFrame(CURRENT_STEPS)
elif is_saved and "step_data" in saved:
    # Load step data from saved model
    base_df = pd.DataFrame(saved["step_data"])
else:
    # Generate revised step data:
    # - Steps 1-14 (FTUE): keep scripted win chances and prize values from CURRENT_STEPS
    # - Steps 15-28 (post-FTUE): apply cooldown mechanic with hardcoded prize ranges
    #   (small wins £1.50-£2.00, punch wins £3.00-£5.00, 80/20 split)
    #   Prize values can be fine-tuned directly in the editable table.
    SMALL_FLOOR, SMALL_CEIL = 1.00, 1.50
    PUNCH_FLOOR, PUNCH_CEIL = 2.00, 3.50
    PUNCH_EVERY = 5  # every 5th instant win is a punch win (80/20 split)

    revised_rows = []
    instant_idx = 0  # counts instant-win steps in post-FTUE only
    for s in CURRENT_STEPS:
        row = {**s}
        if s["step"] <= 14:
            # FTUE: preserve exactly as designed (includes our added wins at steps 5 and 10)
            pass
        elif s["type"] != "Sweepstakes":
            # Post-FTUE: apply cooldown mechanic
            pos = instant_idx % params["cycle_length"]
            row["win_chance"] = 1.0 if pos < params["win_steps"] else 0.01
            instant_idx += 1

            # Apply prize structure with linear scaling
            progress = (s["step"] - 14) / 14  # normalize post-FTUE progress (0 to 1)
            if instant_idx % PUNCH_EVERY == 0:
                row["free_prize"] = round((PUNCH_FLOOR + progress * (PUNCH_CEIL - PUNCH_FLOOR)) * 4) / 4
            else:
                row["free_prize"] = round((SMALL_FLOOR + progress * (SMALL_CEIL - SMALL_FLOOR)) * 4) / 4
            row["paid_prize"] = round(row["free_prize"] * params["paid_multiplier"] * 4) / 4
        revised_rows.append(row)
    base_df = pd.DataFrame(revised_rows)

# Run model from the base data first (before user edits)
results = compute_model_from_df(base_df, params)
econ_rows, overall_position, calculated_rtp = compute_economics(results, params)


# ===================================================================
# DISPLAY
# ===================================================================

net_rev = price_point * (1 - platform_take) - paypal_fee

# Battle pass table - EDITABLE
st.markdown("---")
st.subheader("Battle Pass Steps")

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

# Build a unique key from sidebar settings so the table resets when sliders change
# (st.data_editor caches by key — if the key stays the same, old edits persist)
_editor_key_parts = [model_mode, str(price_point), str(int(platform_take*100)), str(cashout_threshold), str(paid_conversion_pct)]
if is_revised:
    _editor_key_parts += [str(win_steps), str(no_win_steps), str(paid_multiplier)]
_editor_key = "step_editor_" + "_".join(_editor_key_parts)

st.caption("Edit **Win %**, **Free Prize**, and **Paid Prize** below. Results update automatically.")
edited_df = st.data_editor(
    edit_df,
    use_container_width=True,
    hide_index=True,
    disabled=["Step", "Level", "Tickets", "Type"],
    column_config={
        "Step": st.column_config.NumberColumn("Step", width="small",
            help="Battle pass step number. Steps 1-14 = FTUE (scripted). Steps 15-28 = post-FTUE (cooldown)."),
        "Level": st.column_config.NumberColumn("Level", width="small",
            help="In-game level required to unlock this step."),
        "Tickets": st.column_config.NumberColumn("Tickets", format="%d",
            help="Cumulative tickets needed to reach this step."),
        "Win % (input)": st.column_config.NumberColumn("Win %", min_value=0, max_value=100, step=0.5, format="%.1f%%",
            help="Win chance for this step. 100% = guaranteed. Edit to override the model's default."),
        "Free Prize": st.column_config.NumberColumn("Free Prize", min_value=0, max_value=100, step=0.25, format="\u00a3%.2f",
            help="Prize value for free-tier players on a win."),
        "Paid Prize": st.column_config.NumberColumn("Paid Prize", min_value=0, max_value=200, step=0.25, format="\u00a3%.2f",
            help="Prize value for paid-tier players on a win. Typically Free Prize × Paid Multiplier."),
    },
    key=_editor_key,
)

# Recalculate from edited values
recalc_df = base_df.copy()
for i, row in edited_df.iterrows():
    if i < len(recalc_df):
        recalc_df.at[i, "win_chance"] = row["Win % (input)"] / 100
        recalc_df.at[i, "free_prize"] = row["Free Prize"]
        recalc_df.at[i, "paid_prize"] = row["Paid Prize"]

results = compute_model_from_df(recalc_df, params)
econ_rows, overall_position, calculated_rtp = compute_economics(results, params)

# Key metrics row (placed AFTER recalculation so it reflects table edits)
st.markdown("---")
c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
    st.metric("Pass Price", f"\u00a3{price_point:.2f}",
              help="Gross price of the premium battle pass. Set in the sidebar.")
with c2:
    st.metric("Net Rev / Paid User", f"\u00a3{net_rev:.2f}",
              help="Pass Price × (1 − Platform %) − PayPal Fee. The actual revenue per paid player after fees. Green dashed line on the wallet chart.")
with c3:
    st.metric("RTP (Target)", f"{target_rtp*100:.0f}%",
              help="Your target Return to Player. The model highlights when Actual RTP drifts from this.")
with c4:
    rtp_delta = calculated_rtp - (target_rtp * 100)
    st.metric(
        "RTP (Actual)",
        f"{calculated_rtp:.0f}%",
        delta=f"{rtp_delta:+.0f}% vs target",
        delta_color="inverse" if calculated_rtp > target_rtp * 100 else "normal",
        help="RTP = Total Blended Payout / Total Blended Income x 100. Blended Payout = sum of (Expected Payout x Incidence) across all segments. Blended Income = sum of (Income x Incidence) across all segments. Lower RTP = better for the business."
    )
with c5:
    if is_revised:
        st.metric("Hit Rate", f"1 in {cycle_length}",
                  help="Cooldown mechanic applied to post-FTUE steps (15-28 only). Steps 1-14 use scripted win chances. Controlled by the Cooldown Mechanic sliders in the sidebar.")
    else:
        st.metric("Hit Rate", "Variable",
                  help="Current model uses variable win chances per step as defined in the original spreadsheet.")
with c6:
    st.metric(
        "Overall Position",
        f"\u00a3{overall_position:.2f}",
        delta="Profit" if overall_position >= 0 else "Loss",
        delta_color="normal" if overall_position >= 0 else "inverse",
        help="Blended profit or loss per player across all segments. Calculated as the sum of each segment's Contribution: (Income - Expected Payout) x Incidence. Positive = profitable, negative = losing money."
    )

# Handle save button click
if save_clicked and save_name.strip():
    # Collect current settings
    settings_to_save = {
        "pass_duration_weeks": pass_duration_weeks,
        "price_point": price_point,
        "platform_take_pct": int(platform_take * 100),
        "paypal_fee": paypal_fee,
        "target_rtp_pct": int(target_rtp * 100),
        "retention_free_pct": int(retention_free * 100),
        "retention_paid_pct": int(retention_paid * 100),
        "paid_conversion_pct": paid_conversion_pct,
        "free_step7": int(free_step7 * 100),
        "free_step14": int(free_step14 * 100),
        "free_step21": int(free_step21 * 100),
        "free_step28": int(free_step28 * 100),
        "paid_step7": int(paid_step7 * 100),
        "paid_step14": int(paid_step14 * 100),
        "paid_step21": int(paid_step21 * 100),
        "paid_step28": int(paid_step28 * 100),
        "cashout_threshold": cashout_threshold,
    }
    if is_revised:
        settings_to_save.update({
            "win_steps": win_steps,
            "no_win_steps": no_win_steps,
            "paid_multiplier": paid_multiplier,
        })

    # Save step data from the edited table
    step_data = []
    for i, row in edited_df.iterrows():
        if i < len(base_df):
            s = base_df.iloc[i].to_dict()
            s["win_chance"] = row["Win % (input)"] / 100
            s["free_prize"] = float(row["Free Prize"])
            s["paid_prize"] = float(row["Paid Prize"])
            # Convert any numpy/pandas types to native Python for JSON
            clean_s = {}
            for k, v in s.items():
                if isinstance(v, (np.integer,)):
                    clean_s[k] = int(v)
                elif isinstance(v, (np.floating,)):
                    clean_s[k] = float(v)
                elif pd.isna(v):
                    clean_s[k] = None
                else:
                    clean_s[k] = v
            step_data.append(clean_s)

    st.session_state.saved_models[save_name.strip()] = {
        "settings": settings_to_save,
        "step_data": step_data,
    }
    st.toast(f"Saved model: {save_name.strip()}")
    st.rerun()
elif save_clicked and not save_name.strip():
    st.sidebar.warning("Please enter a name for your model")

# Show recalculated results table
st.markdown("---")
st.subheader("Step Results")
st.caption("Calculated from your edits above. Updates automatically.")

recalc_display = pd.DataFrame([{
    "Step": r["step"],
    "Type": r["type"],
    "Win % (eff.)": f"{r['win_chance_effective']*100:.1f}%",
    "Free Prize": f"\u00a3{r['free_prize']:.2f}" if r["type"] != "Sweepstakes" else f"\u00a3{r.get('sweep_amt', 0):,.0f} sweep",
    "Paid Prize": f"\u00a3{r['paid_prize']:.2f}" if r["type"] != "Sweepstakes" else f"\u00a3{r.get('sweep_amt', 0):,.0f} sweep",
    "EV Free": f"\u00a3{r['ev_free']:.2f}",
    "EV Paid": f"\u00a3{r['ev_paid']:.2f}",
    "Cum. Wallet (Free)": f"\u00a3{r['w_fe']:.2f}",
    "Cum. Wallet (Paid)": f"\u00a3{r['w_pe']:.2f}",
} for r in results])
st.dataframe(recalc_display, use_container_width=True, hide_index=True,
    column_config={
        "Win % (eff.)": st.column_config.TextColumn(
            help="Effective win chance after cooldown mechanic (Revised) or as-is (Current)."),
        "EV Free": st.column_config.TextColumn(
            help="Expected Value = Prize × Win %. Average payout per attempt for free players."),
        "EV Paid": st.column_config.TextColumn(
            help="Expected Value = Prize × Win %. Average payout per attempt for paid players."),
        "Cum. Wallet (Free)": st.column_config.TextColumn(
            help="Running total of EV accumulated by a free player who completes every step up to this point."),
        "Cum. Wallet (Paid)": st.column_config.TextColumn(
            help="Running total of EV accumulated by a paid player who completes every step up to this point."),
    }
)

# Economics table
st.markdown("---")
st.subheader("Economic Summary")
st.dataframe(
    pd.DataFrame(econ_rows),
    use_container_width=True,
    hide_index=True,
    column_config={
        "Segment": st.column_config.TextColumn(
            "Segment",
            help="Free = didn't buy the pass. Paid = bought the pass."
        ),
        "Wtd. Wallet": st.column_config.TextColumn(
            "Wtd. Wallet",
            help="Weighted average wallet based on step completion distribution. Accounts for the fact that not all players finish the pass — players who drop off earlier accumulate less."
        ),
        "Income": st.column_config.TextColumn(
            "Income",
            help="Net revenue after platform take and PayPal fee. Free = £0, Paid = Pass Price × (1 − Platform %) − PayPal Fee."
        ),
        f"D{pass_duration_days} Cashout" if pass_duration_days != 7 else "D7 Cashout": st.column_config.TextColumn(
            help=f"% of players who actually cash out by end of a {pass_duration_days}-day season. Set in the sidebar."
        ),
        "Expected Payout": st.column_config.TextColumn(
            "Expected Payout",
            help="Weighted Wallet × D7 Cashout Rate. What the house actually pays out."
        ),
        "Net Position": st.column_config.TextColumn(
            "Net Position",
            help="Income − Expected Payout. Negative = house loses money on this segment."
        ),
        "Incidence": st.column_config.TextColumn(
            "Incidence",
            help="% of total player base. Free% + Paid% = 100%. Set via Paid Conversion slider."
        ),
        "Contribution": st.column_config.TextColumn(
            "Contribution",
            help="Net Position × Incidence. Sum of both = Overall Position."
        ),
    }
)

if overall_position < 0:
    st.error(f"Blended position: **\u00a3{overall_position:.2f}** per player. "
             f"The model is losing money at these settings.")
else:
    st.success(f"Blended position: **\u00a3{overall_position:.2f}** per player. "
               f"The model is profitable at these settings.")

# ===================================================================
# RETENTION STRESS TEST
# ===================================================================
st.markdown("---")
st.subheader("Retention Stress Test")
st.caption("What happens if more paid players cash out than expected? Tests model resilience at higher cashout rates.")

def stress_test_economics(results, params, paid_ret_override):
    """Run economics with a different paid retention rate."""
    stress_params = {**params, "retention_paid": paid_ret_override}
    _, stress_overall, stress_rtp = compute_economics(results, stress_params)
    return stress_overall, stress_rtp

stress_scenarios = [
    (f"Current ({int(retention_paid*100)}%)", retention_paid),
    ("40% cashout", 0.40),
    ("50% cashout", 0.50),
]

stress_cols = st.columns(len(stress_scenarios))
for col, (label, ret) in zip(stress_cols, stress_scenarios):
    s_pos, s_rtp = stress_test_economics(results, params, ret)
    with col:
        st.metric(
            label,
            f"\u00a3{s_pos:.2f}",
            delta="Profit" if s_pos >= 0 else "Loss",
            delta_color="normal" if s_pos >= 0 else "inverse",
        )
        st.caption(f"RTP: {s_rtp:.0f}%")

# ===================================================================
# MULTI-WEEK CARRYOVER ANALYSIS (Real Retention Curve)
# ===================================================================
st.markdown("---")
st.subheader("Multi-Week Carryover & Breakage Analysis")
st.caption(
    f"Wallet balances carry over across {pass_duration_weeks}-week seasons (tickets reset, balance doesn't). "
    f"Players must reach **£{cashout_threshold:.0f}** to cash out. "
    f"Retention is interpolated daily between milestone data points."
)

# --- Retention curve inputs (editable defaults) ---
max_seasons = 4 if pass_duration_weeks == 1 else 2  # cap at ~28 days either way
num_seasons = st.slider("Seasons to simulate", min_value=1, max_value=max_seasons, value=max_seasons, step=1,
                         help=f"Number of {pass_duration_weeks}-week battle pass seasons to model.")

with st.expander("Retention Curves (click to edit)"):
    st.caption("Retention milestones for free and paid players. Paid players typically retain better (they've invested money).")

    st.markdown("**Free Players**")
    free_rc1, free_rc2, free_rc3, free_rc4 = st.columns(4)
    with free_rc1:
        ret_free_d1 = st.number_input("D1 Free %", min_value=0.0, max_value=100.0, value=50.0, step=1.0, key="ret_free_d1") / 100
    with free_rc2:
        ret_free_d7 = st.number_input("D7 Free %", min_value=0.0, max_value=100.0, value=25.0, step=1.0, key="ret_free_d7") / 100
    with free_rc3:
        ret_free_d14 = st.number_input("D14 Free %", min_value=0.0, max_value=100.0, value=10.0, step=1.0, key="ret_free_d14") / 100
    with free_rc4:
        ret_free_d30 = st.number_input("D30 Free %", min_value=0.0, max_value=100.0, value=3.0, step=0.1, key="ret_free_d30") / 100

    st.markdown("**Paid Players**")
    paid_rc1, paid_rc2, paid_rc3, paid_rc4 = st.columns(4)
    with paid_rc1:
        ret_paid_d1 = st.number_input("D1 Paid %", min_value=0.0, max_value=100.0, value=65.0, step=1.0, key="ret_paid_d1") / 100
    with paid_rc2:
        ret_paid_d7 = st.number_input("D7 Paid %", min_value=0.0, max_value=100.0, value=40.0, step=1.0, key="ret_paid_d7") / 100
    with paid_rc3:
        ret_paid_d14 = st.number_input("D14 Paid %", min_value=0.0, max_value=100.0, value=20.0, step=1.0, key="ret_paid_d14") / 100
    with paid_rc4:
        ret_paid_d30 = st.number_input("D30 Paid %", min_value=0.0, max_value=100.0, value=8.0, step=0.1, key="ret_paid_d30") / 100

def interpolate_daily_retention(d1, d7, d14, d30, num_days=30):
    """Interpolate daily retention from milestone data points.

    Uses log-linear interpolation between milestones, which better fits
    the typical L-shaped retention curve (heavy early churn, then flattening).
    """
    milestones = [(1, d1), (7, d7), (14, d14), (30, d30)]
    daily = {0: 1.0}  # Day 0 = 100% (install day)

    for i in range(len(milestones) - 1):
        day_start, ret_start = milestones[i]
        day_end, ret_end = milestones[i + 1]

        # Log-linear interpolation (handles the L-curve shape better)
        # Avoid log(0) by clamping
        ret_start = max(ret_start, 0.001)
        ret_end = max(ret_end, 0.001)
        log_start = np.log(ret_start)
        log_end = np.log(ret_end)

        for d in range(day_start, day_end + 1):
            t = (d - day_start) / (day_end - day_start)
            daily[d] = np.exp(log_start + t * (log_end - log_start))

    return daily

daily_retention_free = interpolate_daily_retention(ret_free_d1, ret_free_d7, ret_free_d14, ret_free_d30)
daily_retention_paid = interpolate_daily_retention(ret_paid_d1, ret_paid_d7, ret_paid_d14, ret_paid_d30)

def simulate_multi_week_real(results, params, num_seasons, daily_ret_free, daily_ret_paid, cashout_threshold):
    """Simulate multi-season wallet carryover using real daily retention data.

    Each season = pass_duration_days. Retention for end-of-season N = daily_retention[N * duration].
    Wallet accumulates each season; cashout only when balance >= threshold.
    Uses weighted wallets from step completion distribution.
    """
    season_days = params["pass_duration_days"]
    # Compute weighted wallets from step completion curves
    free_completions = {7: params["free_step7"], 14: params["free_step14"],
                        21: params["free_step21"], 28: params["free_step28"]}
    paid_completions = {7: params["paid_step7"], 14: params["paid_step14"],
                        21: params["paid_step21"], 28: params["paid_step28"]}

    free_weighted_wallet = compute_weighted_wallet(results, free_completions, "w_fe")
    paid_weighted_wallet = compute_weighted_wallet(results, paid_completions, "w_pe")

    # Use net income (after platform take and PayPal fee) — consistent with single-season economics
    net_income_paid = params["price_point"] * (1 - params["platform_take"]) - params["paypal_fee"]

    segments = [
        {"name": "Free Players",  "ev_per_week": free_weighted_wallet, "income_per_week": 0.0,
         "incidence": params["free_pct"] / 100, "retention_curve": daily_ret_free},
        {"name": "Paid Players",  "ev_per_week": paid_weighted_wallet, "income_per_week": net_income_paid,
         "incidence": params["paid_conversion_pct"] / 100, "retention_curve": daily_ret_paid},
    ]

    snapshots = []

    for seg in segments:
        balance = 0.0
        cumulative_income = 0.0
        cumulative_payout = 0.0
        cumulative_prizes_won = 0.0
        ret_curve = seg["retention_curve"]

        for season in range(1, num_seasons + 1):
            end_day = season * season_days
            surviving = ret_curve.get(end_day, ret_curve[max(ret_curve.keys())])

            season_income = seg["income_per_week"] * surviving
            cumulative_income += season_income

            balance += seg["ev_per_week"]
            cumulative_prizes_won += seg["ev_per_week"] * surviving

            if balance >= cashout_threshold:
                season_payout = balance * surviving
                cumulative_payout += season_payout
                cashout_happened = True
                balance = 0.0
            else:
                season_payout = 0.0
                cashout_happened = False

            snapshots.append({
                "Season": season,
                "Day": end_day,
                "Segment": seg["name"],
                "Retention": f"{surviving*100:.1f}%",
                "Season Income": season_income,
                "Balance": balance,
                "Cashout": "Yes" if cashout_happened else "No",
                "Season Payout": season_payout,
                "Cum. Income": cumulative_income,
                "Cum. Payout": cumulative_payout,
                "Cum. Position": cumulative_income - cumulative_payout,
                "Cum. Prizes Won": cumulative_prizes_won,
            })

    return snapshots

multi_week_data = simulate_multi_week_real(results, params, num_seasons, daily_retention_free, daily_retention_paid, cashout_threshold)
mw_df = pd.DataFrame(multi_week_data)

# Summary table: final season position by segment
final_week_rows = [r for r in multi_week_data if r["Season"] == num_seasons]
overall_multi_week = 0.0
mw_summary = []
for row in final_week_rows:
    seg_name = row["Segment"]
    inc_map = {"Free Players": free_pct/100, "Paid Players": paid_conversion_pct/100}
    incidence = inc_map[seg_name]
    contribution = row["Cum. Position"] * incidence
    overall_multi_week += contribution
    mw_summary.append({
        "Segment": seg_name,
        f"Balance (S{num_seasons})": f"£{row['Balance']:.2f}",
        "Cum. Income": f"£{row['Cum. Income']:.2f}",
        "Cum. Payout": f"£{row['Cum. Payout']:.2f}",
        "Net Position": f"£{row['Cum. Position']:.2f}",
        "Incidence": f"{incidence*100:.0f}%",
        "Contribution": f"£{contribution:.2f}",
    })

st.dataframe(pd.DataFrame(mw_summary), use_container_width=True, hide_index=True,
    column_config={
        "Segment": st.column_config.TextColumn(help="Player segment."),
        f"Balance (S{num_seasons})": st.column_config.TextColumn(
            help="Remaining wallet balance. If below the cashout threshold, this is breakage — money won but not yet withdrawable."),
        "Cum. Income": st.column_config.TextColumn(help="Total gross income across all simulated weeks."),
        "Cum. Payout": st.column_config.TextColumn(help="Total paid out across all weeks (only when balance hits cashout threshold)."),
        "Net Position": st.column_config.TextColumn(help="Cumulative Income - Cumulative Payout."),
        "Incidence": st.column_config.TextColumn(help="Segment weight in the player base."),
        "Contribution": st.column_config.TextColumn(help="Net Position x Incidence."),
    }
)

total_days = num_seasons * pass_duration_days
if overall_multi_week < 0:
    st.error(f"Blended position: **£{overall_multi_week:.2f}** per player over {num_seasons} season{'s' if num_seasons > 1 else ''} ({total_days} days).")
else:
    st.success(f"Blended position: **£{overall_multi_week:.2f}** per player over {num_seasons} season{'s' if num_seasons > 1 else ''} ({total_days} days).")

# Breakage analysis
total_prizes_won = 0.0
total_paid_out = 0.0
total_unredeemed = 0.0
for row in final_week_rows:
    seg_name = row["Segment"]
    inc_map = {"Free Players": free_pct/100, "Paid Players": paid_conversion_pct/100}
    incidence = inc_map[seg_name]
    total_prizes_won += row["Cum. Prizes Won"] * incidence
    total_paid_out += row["Cum. Payout"] * incidence
    end_day = num_seasons * pass_duration_days
    ret_curve = daily_retention_free if seg_name == "Free Players" else daily_retention_paid
    surviving = ret_curve.get(end_day, ret_curve[max(ret_curve.keys())])
    total_unredeemed += row["Balance"] * surviving * incidence

breakage_rate = ((total_prizes_won - total_paid_out) / total_prizes_won * 100) if total_prizes_won > 0 else 0.0

br_c1, br_c2, br_c3 = st.columns(3)
with br_c1:
    st.metric("Total Prizes Won (blended)", f"£{total_prizes_won:.2f}",
              help="Weighted sum of all expected prizes accumulated across segments over the full simulation period.")
with br_c2:
    st.metric("Total Paid Out (blended)", f"£{total_paid_out:.2f}",
              help="Weighted sum of all actual cashouts. Only counts prizes that hit the cashout threshold and were redeemed.")
with br_c3:
    st.metric("Breakage Rate", f"{breakage_rate:.0f}%",
              help="% of prizes won that are never cashed out. Higher breakage = more favorable for the house. "
                   "Caused by players churning before hitting the cashout threshold, or balance sitting below the threshold at end of simulation.")

# Week-by-week detail with segment filter
with st.expander("Week-by-week detail"):
    all_segments = ["Free Players", "Paid Players"]
    selected_segments = st.multiselect(
        "Show segments", all_segments, default=["Paid Players"],
        help="Select one or more segments to view their weekly breakdown."
    )
    if selected_segments:
        filtered_df = mw_df[mw_df["Segment"].isin(selected_segments)].copy()
        for col in ["Season Income", "Season Payout", "Cum. Income", "Cum. Payout", "Cum. Position", "Balance"]:
            filtered_df[col] = filtered_df[col].apply(lambda x: f"£{x:.2f}")
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    else:
        st.info("Select at least one segment above.")

# P&L chart
fig_mw = go.Figure()
for seg_name in ["Free Players", "Paid Players"]:
    seg_rows = [r for r in multi_week_data if r["Segment"] == seg_name]
    fig_mw.add_trace(go.Scatter(
        x=[f"S{r['Season']} (D{r['Day']})" for r in seg_rows],
        y=[r["Cum. Position"] for r in seg_rows],
        name=seg_name,
        mode="lines+markers",
    ))
fig_mw.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Breakeven")
fig_mw.update_layout(
    xaxis_title="Season (Day)",
    yaxis_title="Cumulative Net Position (£)",
    height=400,
    template="plotly_white",
)
st.plotly_chart(fig_mw, use_container_width=True)


# ===================================================================
# CHARTS
# ===================================================================
st.markdown("---")
st.subheader("Expected Wallet Progression (Engaged Players)")
st.caption("Cumulative wallet for a player who reaches every step. The weighted wallet in the economics table adjusts this downward based on step completion distribution.")

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
# Color by win type: guaranteed (100%) = green, cooldown win = blue, low odds = gray
colors = ["#2ecc71" if r["win_chance_effective"] >= 1.0
          else "#3498db" if r["win_chance_effective"] > 0.05
          else "#95a5a6"
          for r in instant_steps]

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


st.markdown("---")
st.caption("Molly's Cash Battle Pass Model | Built for TXG | v4.0")
