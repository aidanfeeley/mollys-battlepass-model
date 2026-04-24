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

# Determine total steps for this model (needed for dynamic milestones)
if is_saved and "step_data" in saved:
    total_steps = len(saved["step_data"])
else:
    total_steps = len(CURRENT_STEPS)  # 28 for both Current and Revised

# Compute milestone steps (quartiles of total steps)
# For 28 steps: [7, 14, 21, 28]. For 35 steps: [9, 18, 26, 35].
milestones = [round(total_steps * q) for q in [0.25, 0.5, 0.75, 1.0]]

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
        # Build filename: use save name input if filled, else current model name, else generic
        _raw_name = (save_name.strip() if save_name.strip()
                     else model_mode if is_saved
                     else "battlepass_models")
        _export_name = _raw_name.replace(" ", "_").lower() + ".json"
        st.download_button(
            "Export All",
            data=export_data,
            file_name=_export_name,
            mime="application/json",
            use_container_width=True,
        )

with import_col:
    uploaded = st.file_uploader("Import", type="json", label_visibility="collapsed", key="import_file")
    if uploaded is not None:
        try:
            raw = uploaded.read()
            if raw:
                imported = json.loads(raw)

                # Format 1: Full export — {"Model Name": {"settings": {...}, "step_data": [...]}}
                if imported and isinstance(imported, dict) and not any(k in imported for k in ["Step", "step"]):
                    new_models = {k: v for k, v in imported.items()
                                  if k not in st.session_state.saved_models}
                    if new_models:
                        st.session_state.saved_models.update(imported)
                        st.sidebar.success(f"Imported {len(imported)} model(s)")
                        st.rerun()
                    else:
                        st.sidebar.info("Models already loaded.")

                # Format 2: Flat step array — [{Step, Type, Win %, Free Prize, Paid Prize}, ...]
                elif imported and isinstance(imported, list) and len(imported) > 0:
                    model_name = uploaded.name.replace(".json", "").replace("_", " ").title()
                    # Convert to internal step_data format
                    step_data = []
                    for i, row in enumerate(imported):
                        step_num = row.get("Step", row.get("step", i + 1))
                        step_type = row.get("Type", row.get("type", "Instant Win"))
                        win_pct = row.get("Win %", row.get("win_chance", 0))
                        free_p = row.get("Free Prize", row.get("free_prize", 0))
                        paid_p = row.get("Paid Prize", row.get("paid_prize", 0))
                        # Handle sweep text like "£100 sweep"
                        if isinstance(free_p, str):
                            free_p = 0.0
                        if isinstance(paid_p, str):
                            paid_p = 0.0
                        # Match against CURRENT_STEPS for metadata (level, tickets, etc.)
                        base = CURRENT_STEPS[i] if i < len(CURRENT_STEPS) else {}
                        step_data.append({
                            "step": step_num,
                            "level": base.get("level", 0),
                            "tickets": base.get("tickets", 0),
                            "sess_med": base.get("sess_med"),
                            "sess_eng": base.get("sess_eng", 0),
                            "type": step_type,
                            "win_chance": win_pct,
                            "free_prize": float(free_p),
                            "paid_prize": float(paid_p),
                        })
                        if step_type == "Sweepstakes" and "sweep_amt" in base:
                            step_data[-1]["sweep_amt"] = base["sweep_amt"]

                    if model_name not in st.session_state.saved_models:
                        st.session_state.saved_models[model_name] = {
                            "settings": {},  # uses current sidebar defaults
                            "step_data": step_data,
                        }
                        st.sidebar.success(f"Imported '{model_name}'")
                        st.rerun()
                    else:
                        st.sidebar.info(f"'{model_name}' already loaded.")
                else:
                    st.sidebar.error("JSON file is empty or not a recognized format.")
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
_free_defaults = [60, 30, 10, 3]
_paid_defaults = [90, 70, 40, 20]

with st.sidebar.expander("W1 Step Completion", expanded=False):
    st.caption(f"% of players reaching each milestone. Steps {', '.join(str(m) for m in milestones)}.")

    st.markdown("**Free Players**")
    free_completions = {}
    for i, ms in enumerate(milestones):
        _key = f"free_step{ms}"
        _step_size = 5 if i < 3 else 1
        _help = f"% of free players reaching step {ms}" + (" (end of pass)" if i == 3 else "")
        free_completions[ms] = st.slider(
            f"Free \u2192 Step {ms}", 0, 100,
            get_default(_key, _free_defaults[i], _free_defaults[i]), _step_size,
            help=_help, key=f"free_comp_{ms}"
        ) / 100

    st.markdown("**Paid Players**")
    paid_completions = {}
    for i, ms in enumerate(milestones):
        _key = f"paid_step{ms}"
        _step_size = 5 if i < 3 else 1
        _help = f"% of paid players reaching step {ms}" + (" (end of pass)" if i == 3 else "")
        paid_completions[ms] = st.slider(
            f"Paid \u2192 Step {ms}", 0, 100,
            get_default(_key, _paid_defaults[i], _paid_defaults[i]), _step_size,
            help=_help, key=f"paid_comp_{ms}"
        ) / 100

    # Validate step completion curves are monotonically decreasing
    _free_vals = list(free_completions.values())
    _paid_vals = list(paid_completions.values())
    _step_labels = [f"Step {m}" for m in milestones]
    for label, vals in [("Free", _free_vals), ("Paid", _paid_vals)]:
        for i in range(1, len(vals)):
            if vals[i] > vals[i - 1]:
                st.warning(
                    f"{label}: {_step_labels[i]} ({vals[i]*100:.0f}%) > {_step_labels[i-1]} ({vals[i-1]*100:.0f}%). "
                    f"Fewer players should reach later steps."
                )
                break

# ===================================================================
# WEEK 2 SIDEBAR CONTROLS
# ===================================================================
st.sidebar.markdown("---")
st.sidebar.header("Week 2 Pass")
st.sidebar.caption("Week 2 is a second battle pass with lower prizes. Wallet carries over from Week 1.")

# Week 2 Pass Price
_w2_price_options = [3.99, 4.99, 6.99, 7.99, 9.99, 12.99, 14.99]
w2_price_point = st.sidebar.select_slider(
    "Week 2 Pass Price",
    options=_w2_price_options,
    value=get_default("w2_price_point", price_point, price_point),
    format_func=lambda x: f"\u00a3{x:.2f}",
    key="w2_price_slider",
    help="Price of the Week 2 premium pass. Defaults to the same as Week 1."
)

# Re-purchase Rate
w2_repurchase_rate = st.sidebar.slider(
    "Re-purchase Rate %", min_value=0, max_value=100,
    value=get_default("w2_repurchase_rate", 40, 40), step=5,
    help="% of retained Week 1 paid players who buy the Week 2 pass.",
    key="w2_repurchase_slider"
) / 100

# Week 2 Free->Paid Conversion
w2_free_conversion = st.sidebar.slider(
    "Week 2 Free\u2192Paid Conversion %", min_value=0, max_value=50,
    value=get_default("w2_free_conversion", 10, 10), step=1,
    help="% of retained Week 1 free players who buy the Week 2 pass.",
    key="w2_free_conv_slider"
) / 100

_w2_paid_defaults = [95, 80, 55, 30]  # Higher than W1 — repurchasers are self-selected engaged

with st.sidebar.expander("W2 Step Completion", expanded=False):
    st.caption(f"% of Week 2 players reaching each milestone. Steps {', '.join(str(m) for m in milestones)}.")

    st.markdown("**Free Players**")
    w2_free_completions = {}
    for i, ms in enumerate(milestones):
        _key = f"w2_free_step{ms}"
        _step_size = 5 if i < 3 else 1
        _def_val = get_default(_key, _free_defaults[i], _free_defaults[i])
        w2_free_completions[ms] = st.slider(
            f"W2 Free \u2192 Step {ms}", 0, 100,
            _def_val, _step_size,
            help=f"% of Week 2 free players reaching step {ms}",
            key=f"w2_free_comp_{ms}"
        ) / 100

    st.markdown("**Paid Players** *(higher defaults — self-selected engaged cohort)*")
    w2_paid_completions = {}
    for i, ms in enumerate(milestones):
        _key = f"w2_paid_step{ms}"
        _step_size = 5 if i < 3 else 1
        _def_val = get_default(_key, _w2_paid_defaults[i], _w2_paid_defaults[i])
        w2_paid_completions[ms] = st.slider(
            f"W2 Paid \u2192 Step {ms}", 0, 100,
            _def_val, _step_size,
            help=f"% of Week 2 paid players reaching step {ms}",
            key=f"w2_paid_comp_{ms}"
        ) / 100

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
    "Minimum Cashout (\u00a3)", min_value=10.0, max_value=50.0,
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
                      Milestones are dynamic — quartiles of total steps (28 → [7,14,21,28], 35 → [9,18,26,35]).
    wallet_key: 'w_fe' for free, 'w_pe' for paid

    The distribution creates tiers between each milestone pair. Players who drop off
    before a milestone contribute their wallet at the previous milestone step.
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
    free_weighted_wallet = compute_weighted_wallet(results, params["free_completions"], "w_fe")
    paid_weighted_wallet = compute_weighted_wallet(results, params["paid_completions"], "w_pe")

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


def simulate_pass_with_carryover(results, starting_wallet, cashout_threshold, wallet_key):
    """Walk through each step. When wallet >= threshold, cashout fires, wallet resets to 0, player continues.

    Used for Week 2 simulation where players carry over wallet from Week 1.
    Returns the wallet state at each step and total amount cashed out.
    """
    ev_key = "ev_free" if wallet_key == "w_fe" else "ev_paid"
    wallet = starting_wallet
    total_cashout = 0.0
    wallet_at_step = {}

    for r in results:
        wallet += r[ev_key]
        if wallet >= cashout_threshold:
            total_cashout += wallet
            wallet = 0.0
        wallet_at_step[r["step"]] = wallet

    return wallet_at_step, total_cashout


def compute_w2_segment_payout(w2_results, starting_wallet, cashout_threshold, wallet_key, step_completions):
    """Compute expected payout for a Week 2 segment using step-by-step cashout simulation.

    Simulates the full pass, tracking mid-pass cashouts when wallet hits threshold.
    Then weights the outcome by step completion distribution (players drop off at milestones).

    Returns (expected_payout, weighted_ending_wallet).
    """
    ev_key = "ev_free" if wallet_key == "w_fe" else "ev_paid"
    ms_list = sorted(step_completions.keys())

    # Simulate the full pass step by step
    wallet = starting_wallet
    total_cashout_at_step = {}  # step -> cumulative cashout up to that step
    wallet_state_at_step = {}   # step -> wallet after that step
    running_cashout = 0.0

    for r in w2_results:
        wallet += r[ev_key]
        if wallet >= cashout_threshold:
            running_cashout += wallet
            wallet = 0.0
        wallet_state_at_step[r["step"]] = wallet
        total_cashout_at_step[r["step"]] = running_cashout

    # Weight by step completion distribution
    weighted_cashout = 0.0
    weighted_wallet = 0.0
    prev_pct = 1.0

    for ms in ms_list:
        pct_reaching = step_completions[ms]
        tier_weight = prev_pct - pct_reaching
        # Players who drop before this milestone: use previous milestone's state
        prev_step = ms_list[ms_list.index(ms) - 1] if ms_list.index(ms) > 0 else w2_results[0]["step"] if w2_results else 1
        tier_cashout = total_cashout_at_step.get(prev_step, 0.0)
        tier_wallet = wallet_state_at_step.get(prev_step, starting_wallet)
        weighted_cashout += tier_weight * tier_cashout
        weighted_wallet += tier_weight * tier_wallet
        prev_pct = pct_reaching

    # Final tier: players who complete the last milestone
    last_step = ms_list[-1] if ms_list else (w2_results[-1]["step"] if w2_results else 1)
    weighted_cashout += prev_pct * total_cashout_at_step.get(last_step, 0.0)
    weighted_wallet += prev_pct * wallet_state_at_step.get(last_step, 0.0)

    return weighted_cashout, weighted_wallet


def compute_w2_economics(w2_results, w1_results, params):
    """Compute Week 2 economics with 4 player segments and mid-pass cashout simulation.

    Segments:
    - W1 Free -> W2 Free: carries W1 free wallet, plays free
    - W1 Free -> W2 Paid: carries W1 free wallet, pays for W2, plays paid
    - W1 Paid -> W2 Repurchase: carries W1 paid wallet, pays for W2, plays paid
    - W1 Paid -> W2 Free: carries W1 paid wallet, plays free
    """
    free_pct_frac = params["free_pct"] / 100
    paid_pct_frac = params["paid_conversion_pct"] / 100
    repurchase_rate = params["w2_repurchase_rate"]
    w2_free_conv = params["w2_free_conversion"]
    w2_net_income = params["w2_price_point"] * (1 - params["platform_take"]) - params["paypal_fee"]
    threshold = params["cashout_threshold"]

    # Week 1 weighted wallets (carryover amounts)
    w1_free_wallet = compute_weighted_wallet(w1_results, params["free_completions"], "w_fe")
    w1_paid_wallet = compute_weighted_wallet(w1_results, params["paid_completions"], "w_pe")

    # 4 segments: (name, incidence, income, starting_wallet, wallet_key_for_w2, step_completions_for_w2)
    segments = [
        (
            "W1 Free \u2192 W2 Free",
            free_pct_frac * (1 - w2_free_conv),
            0.0,
            w1_free_wallet,
            "w_fe",
            params["w2_free_completions"],
        ),
        (
            "W1 Free \u2192 W2 Paid",
            free_pct_frac * w2_free_conv,
            w2_net_income,
            w1_free_wallet,
            "w_pe",
            params["w2_paid_completions"],
        ),
        (
            "W1 Paid \u2192 W2 Repurchase",
            paid_pct_frac * repurchase_rate,
            w2_net_income,
            w1_paid_wallet,
            "w_pe",
            params["w2_paid_completions"],
        ),
        (
            "W1 Paid \u2192 W2 Free",
            paid_pct_frac * (1 - repurchase_rate),
            0.0,
            w1_paid_wallet,
            "w_fe",
            params["w2_free_completions"],
        ),
    ]

    overall = 0.0
    total_blended_payout = 0.0
    total_blended_income = 0.0
    rows = []

    for name, incidence, income, starting_wallet, wallet_key, step_comps in segments:
        expected_payout, ending_wallet = compute_w2_segment_payout(
            w2_results, starting_wallet, threshold, wallet_key, step_comps
        )
        net_pos = income - expected_payout
        contribution = net_pos * incidence
        overall += contribution

        total_blended_payout += expected_payout * incidence
        total_blended_income += income * incidence

        rows.append({
            "Segment": name,
            "Carryover Wallet": f"\u00a3{starting_wallet:.2f}",
            "Income": f"\u00a3{income:.2f}",
            "Expected Payout": f"\u00a3{expected_payout:.2f}",
            "Ending Wallet": f"\u00a3{ending_wallet:.2f}",
            "Net Position": f"\u00a3{net_pos:.2f}",
            "Incidence": f"{incidence*100:.1f}%",
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
    "milestones": milestones,
    "free_completions": free_completions,
    "paid_completions": paid_completions,
    "cashout_threshold": cashout_threshold,
    "w2_price_point": w2_price_point,
    "w2_repurchase_rate": w2_repurchase_rate,
    "w2_free_conversion": w2_free_conversion,
    "w2_free_completions": w2_free_completions,
    "w2_paid_completions": w2_paid_completions,
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
# DISPLAY — TABBED UI
# ===================================================================

net_rev = price_point * (1 - platform_take) - paypal_fee

# Create tabs
tab_w1, tab_w2, tab_combined = st.tabs(["Week 1", "Week 2", "Combined"])

# ===================================================================
# TAB 1: WEEK 1 (all existing display content)
# ===================================================================
with tab_w1:
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
                help="Prize value for paid-tier players on a win. Typically Free Prize x Paid Multiplier."),
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
                  help="Pass Price x (1 - Platform %) - PayPal Fee. The actual revenue per paid player after fees. Green dashed line on the wallet chart.")
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

    # (Save logic moved after all tabs so W2 data is available)

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
                help="Expected Value = Prize x Win %. Average payout per attempt for free players."),
            "EV Paid": st.column_config.TextColumn(
                help="Expected Value = Prize x Win %. Average payout per attempt for paid players."),
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
                help="Net revenue after platform take and PayPal fee. Free = \u00a30, Paid = Pass Price x (1 - Platform %) - PayPal Fee."
            ),
            f"D{pass_duration_days} Cashout" if pass_duration_days != 7 else "D7 Cashout": st.column_config.TextColumn(
                help=f"% of players who actually cash out by end of a {pass_duration_days}-day season. Set in the sidebar."
            ),
            "Expected Payout": st.column_config.TextColumn(
                "Expected Payout",
                help="Weighted Wallet x D7 Cashout Rate. What the house actually pays out."
            ),
            "Net Position": st.column_config.TextColumn(
                "Net Position",
                help="Income - Expected Payout. Negative = house loses money on this segment."
            ),
            "Incidence": st.column_config.TextColumn(
                "Incidence",
                help="% of total player base. Free% + Paid% = 100%. Set via Paid Conversion slider."
            ),
            "Contribution": st.column_config.TextColumn(
                "Contribution",
                help="Net Position x Incidence. Sum of both = Overall Position."
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
    # CHARTS (collapsed by default)
    # ===================================================================
    st.markdown("---")
    with st.expander("Charts", expanded=False):
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


# ===================================================================
# TAB 2: WEEK 2
# ===================================================================
with tab_w2:
    st.subheader("Week 2 Battle Pass Steps")
    st.caption(
        "Week 2 pass defaults from Week 1 data. Edit prizes and win chances independently. "
        "Wallet carries over from Week 1 — players with high carryover may hit the cashout threshold mid-pass."
    )

    # Build Week 2 base DataFrame from Week 1's base step data (before W1 user edits)
    if is_saved and "w2_step_data" in saved and saved["w2_step_data"]:
        w2_base_df = pd.DataFrame(saved["w2_step_data"])
    else:
        # Default from base_df (Week 1 base data, before user edits)
        w2_base_df = base_df.copy()

    # Run model to get initial results for display
    w2_initial_results = compute_model_from_df(w2_base_df, params)

    # Prepare editable columns for Week 2
    w2_edit_df = pd.DataFrame([{
        "Step": r["step"],
        "Level": r.get("level", ""),
        "Tickets": r["tickets"],
        "Type": r["type"],
        "Win % (input)": r["win_chance"] * 100,
        "Free Prize": r["free_prize"] if r["type"] != "Sweepstakes" else 0.0,
        "Paid Prize": r["paid_prize"] if r["type"] != "Sweepstakes" else 0.0,
    } for r in w2_initial_results])

    # Unique key for Week 2 editor
    _w2_editor_key_parts = ["w2", model_mode, str(w2_price_point), str(int(platform_take*100)), str(cashout_threshold)]
    if is_revised:
        _w2_editor_key_parts += [str(win_steps), str(no_win_steps), str(paid_multiplier)]
    _w2_editor_key = "w2_step_editor_" + "_".join(_w2_editor_key_parts)

    st.caption("Edit **Win %**, **Free Prize**, and **Paid Prize** below. Week 2 is typically 'more sober' with lower prizes.")
    w2_edited_df = st.data_editor(
        w2_edit_df,
        use_container_width=True,
        hide_index=True,
        disabled=["Step", "Level", "Tickets", "Type"],
        column_config={
            "Step": st.column_config.NumberColumn("Step", width="small",
                help="Week 2 battle pass step number."),
            "Level": st.column_config.NumberColumn("Level", width="small",
                help="In-game level required to unlock this step."),
            "Tickets": st.column_config.NumberColumn("Tickets", format="%d",
                help="Cumulative tickets needed to reach this step."),
            "Win % (input)": st.column_config.NumberColumn("Win %", min_value=0, max_value=100, step=0.5, format="%.1f%%",
                help="Win chance for this Week 2 step. Edit to adjust independently from Week 1."),
            "Free Prize": st.column_config.NumberColumn("Free Prize", min_value=0, max_value=100, step=0.25, format="\u00a3%.2f",
                help="Prize value for free-tier players on a win in Week 2."),
            "Paid Prize": st.column_config.NumberColumn("Paid Prize", min_value=0, max_value=200, step=0.25, format="\u00a3%.2f",
                help="Prize value for paid-tier players on a win in Week 2."),
        },
        key=_w2_editor_key,
    )

    # Recalculate Week 2 from edited values
    w2_recalc_df = w2_base_df.copy()
    for i, row in w2_edited_df.iterrows():
        if i < len(w2_recalc_df):
            w2_recalc_df.at[i, "win_chance"] = row["Win % (input)"] / 100
            w2_recalc_df.at[i, "free_prize"] = row["Free Prize"]
            w2_recalc_df.at[i, "paid_prize"] = row["Paid Prize"]

    w2_results = compute_model_from_df(w2_recalc_df, params)

    # Update w2_base_df to reflect edits (for save)
    w2_base_df = w2_recalc_df.copy()

    # Show Week 2 step results (collapsed)
    with st.expander("Week 2 Step Results", expanded=False):
        st.caption("Per-step EVs before carryover wallet is applied.")

        w2_recalc_display = pd.DataFrame([{
            "Step": r["step"],
            "Type": r["type"],
            "Win % (eff.)": f"{r['win_chance_effective']*100:.1f}%",
            "Free Prize": f"\u00a3{r['free_prize']:.2f}" if r["type"] != "Sweepstakes" else f"\u00a3{r.get('sweep_amt', 0):,.0f} sweep",
            "Paid Prize": f"\u00a3{r['paid_prize']:.2f}" if r["type"] != "Sweepstakes" else f"\u00a3{r.get('sweep_amt', 0):,.0f} sweep",
            "EV Free": f"\u00a3{r['ev_free']:.2f}",
            "EV Paid": f"\u00a3{r['ev_paid']:.2f}",
            "Cum. Wallet (Free)": f"\u00a3{r['w_fe']:.2f}",
            "Cum. Wallet (Paid)": f"\u00a3{r['w_pe']:.2f}",
        } for r in w2_results])
        st.dataframe(w2_recalc_display, use_container_width=True, hide_index=True,
            column_config={
                "Win % (eff.)": st.column_config.TextColumn(
                    help="Effective win chance for this Week 2 step."),
                "EV Free": st.column_config.TextColumn(
                    help="Expected Value = Prize x Win %. Average payout per attempt for free players in Week 2."),
                "EV Paid": st.column_config.TextColumn(
                    help="Expected Value = Prize x Win %. Average payout per attempt for paid players in Week 2."),
                "Cum. Wallet (Free)": st.column_config.TextColumn(
                    help="Running total of EV accumulated in Week 2 only (excludes carryover from Week 1)."),
                "Cum. Wallet (Paid)": st.column_config.TextColumn(
                    help="Running total of EV accumulated in Week 2 only (excludes carryover from Week 1)."),
            }
        )

    # Week 2 Economics with mid-pass cashout simulation
    st.markdown("---")
    st.subheader("Week 2 Economic Summary")
    st.caption(
        "Week 2 uses step-by-step cashout simulation. Players carrying wallet from Week 1 may hit the "
        f"\u00a3{cashout_threshold:.0f} threshold mid-pass, triggering a cashout and wallet reset to \u00a30. "
        "Expected payout is weighted by step completion distribution."
    )

    w2_econ_rows, w2_overall, w2_rtp = compute_w2_economics(w2_results, results, params)

    w2_net_rev = w2_price_point * (1 - platform_take) - paypal_fee

    # Key metrics for Week 2
    w2c1, w2c2, w2c3, w2c4 = st.columns(4)
    with w2c1:
        st.metric("W2 Pass Price", f"\u00a3{w2_price_point:.2f}",
                  help="Gross price of the Week 2 premium pass.")
    with w2c2:
        st.metric("W2 Net Rev / Paid User", f"\u00a3{w2_net_rev:.2f}",
                  help="Week 2 Pass Price x (1 - Platform %) - PayPal Fee.")
    with w2c3:
        st.metric("W2 Repurchase Rate", f"{w2_repurchase_rate*100:.0f}%",
                  help="% of Week 1 paid players who buy Week 2 pass.")
    with w2c4:
        st.metric(
            "W2 Overall Position",
            f"\u00a3{w2_overall:.2f}",
            delta="Profit" if w2_overall >= 0 else "Loss",
            delta_color="normal" if w2_overall >= 0 else "inverse",
            help="Blended profit or loss per player across all Week 2 segments. Accounts for wallet carryover and mid-pass cashouts."
        )

    st.dataframe(
        pd.DataFrame(w2_econ_rows),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Segment": st.column_config.TextColumn(
                "Segment",
                help="Player segment showing Week 1 origin and Week 2 tier."
            ),
            "Carryover Wallet": st.column_config.TextColumn(
                "Carryover Wallet",
                help="Weighted wallet balance carried over from Week 1. This is the starting balance before Week 2 steps begin."
            ),
            "Income": st.column_config.TextColumn(
                "Income",
                help="Net revenue for this segment. Paid segments pay the Week 2 pass price (after fees). Free segments = \u00a30."
            ),
            "Expected Payout": st.column_config.TextColumn(
                "Expected Payout",
                help="Expected total cashout from step-by-step simulation, weighted by step completion. Includes mid-pass cashouts when wallet hits threshold."
            ),
            "Ending Wallet": st.column_config.TextColumn(
                "Ending Wallet",
                help="Expected wallet balance remaining after Week 2, weighted by step completion. Carries forward to Week 3 if applicable."
            ),
            "Net Position": st.column_config.TextColumn(
                "Net Position",
                help="Income - Expected Payout. Negative = house loses money on this segment."
            ),
            "Incidence": st.column_config.TextColumn(
                "Incidence",
                help="% of total original player base in this segment. All 4 segments sum to 100%."
            ),
            "Contribution": st.column_config.TextColumn(
                "Contribution",
                help="Net Position x Incidence. Sum of all segments = W2 Overall Position."
            ),
        }
    )

    if w2_overall < 0:
        st.error(f"Week 2 blended position: **\u00a3{w2_overall:.2f}** per player. "
                 f"The model is losing money in Week 2 at these settings.")
    else:
        st.success(f"Week 2 blended position: **\u00a3{w2_overall:.2f}** per player. "
                   f"The model is profitable in Week 2 at these settings.")

    # Week 2 Stress Test
    st.markdown("---")
    st.subheader("Week 2 Stress Test")
    st.caption("Week 2 is sensitive to repurchase rate and cashout threshold because of carryover wallets. "
               "What happens at different repurchase rates?")

    def w2_stress_test(w2_results, w1_results, params, repurchase_override):
        stress_params = {**params, "w2_repurchase_rate": repurchase_override}
        _, stress_overall, stress_rtp = compute_w2_economics(w2_results, w1_results, stress_params)
        return stress_overall, stress_rtp

    w2_stress_scenarios = [
        (f"Current ({int(w2_repurchase_rate*100)}%)", w2_repurchase_rate),
        ("50% repurchase", 0.50),
        ("60% repurchase", 0.60),
        ("80% repurchase", 0.80),
    ]

    w2_stress_cols = st.columns(len(w2_stress_scenarios))
    for col, (label, rep_rate) in zip(w2_stress_cols, w2_stress_scenarios):
        s_pos, s_rtp = w2_stress_test(w2_results, results, params, rep_rate)
        with col:
            st.metric(
                label,
                f"\u00a3{s_pos:.2f}",
                delta="Profit" if s_pos >= 0 else "Loss",
                delta_color="normal" if s_pos >= 0 else "inverse",
            )
            st.caption(f"RTP: {s_rtp:.0f}%")


# ===================================================================
# TAB 3: COMBINED
# ===================================================================
with tab_combined:
    st.subheader("Combined Week 1 + Week 2 Economics")
    st.caption("Overview of both weeks and their combined P&L position.")

    # Week 1 summary
    st.markdown("#### Week 1 Summary")
    comb_w1_cols = st.columns(3)
    with comb_w1_cols[0]:
        st.metric("W1 Overall Position", f"\u00a3{overall_position:.2f}",
                  help="Week 1 blended profit/loss per player.")
    with comb_w1_cols[1]:
        st.metric("W1 RTP", f"{calculated_rtp:.0f}%",
                  help="Week 1 actual Return to Player.")
    with comb_w1_cols[2]:
        st.metric("W1 Pass Price", f"\u00a3{price_point:.2f}",
                  help="Week 1 premium pass price.")

    # Week 2 summary
    st.markdown("#### Week 2 Summary")
    comb_w2_cols = st.columns(3)
    with comb_w2_cols[0]:
        st.metric("W2 Overall Position", f"\u00a3{w2_overall:.2f}",
                  help="Week 2 blended profit/loss per player.")
    with comb_w2_cols[1]:
        w2_rtp_display = f"{w2_rtp:.0f}%" if w2_rtp > 0 else "N/A"
        st.metric("W2 RTP", w2_rtp_display,
                  help="Week 2 actual Return to Player (based on paid segments only).")
    with comb_w2_cols[2]:
        st.metric("W2 Pass Price", f"\u00a3{w2_price_point:.2f}",
                  help="Week 2 premium pass price.")

    # Combined
    combined_position = overall_position + w2_overall
    st.markdown("#### Combined Position")
    comb_total_cols = st.columns(3)
    with comb_total_cols[0]:
        st.metric(
            "Combined Overall Position",
            f"\u00a3{combined_position:.2f}",
            delta="Profit" if combined_position >= 0 else "Loss",
            delta_color="normal" if combined_position >= 0 else "inverse",
            help="Sum of Week 1 and Week 2 overall positions. Total profit/loss per player across both weeks."
        )
    with comb_total_cols[1]:
        st.metric("W1 Contribution", f"\u00a3{overall_position:.2f}",
                  help="Week 1's share of the combined position.")
    with comb_total_cols[2]:
        st.metric("W2 Contribution", f"\u00a3{w2_overall:.2f}",
                  help="Week 2's share of the combined position.")

    if combined_position < 0:
        st.error(f"Combined position: **\u00a3{combined_position:.2f}** per player across both weeks. The model is losing money.")
    else:
        st.success(f"Combined position: **\u00a3{combined_position:.2f}** per player across both weeks. The model is profitable.")

    # ===================================================================
    # MULTI-WEEK CARRYOVER ANALYSIS (Real Retention Curve)
    # ===================================================================
    st.markdown("---")
    st.info(
        "The combined position above reflects one Week 1 pass + one Week 2 pass without retention decay. "
        "The multi-week simulation below models what happens over multiple seasons with real retention, "
        "wallet carryover, and cashout timing."
    )
    st.subheader("Multi-Week Carryover & Breakage Analysis")
    st.caption(
        f"Wallet balances carry over across {pass_duration_weeks}-week seasons (tickets reset, balance doesn't). "
        f"Players must reach **\u00a3{cashout_threshold:.0f}** to cash out. "
        f"Season 1 uses Week 1 data, Season 2+ uses Week 2 data. "
        f"Retention is interpolated daily between milestone data points."
    )

    # --- Retention curve inputs (editable defaults) ---
    max_seasons = 4 if pass_duration_weeks == 1 else 2  # cap at ~28 days either way
    num_seasons = st.slider("Seasons to simulate", min_value=1, max_value=max_seasons, value=max_seasons, step=1,
                             help=f"Number of {pass_duration_weeks}-week battle pass seasons to model.",
                             key="combined_num_seasons")

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
        milestones_ret = [(1, d1), (7, d7), (14, d14), (30, d30)]
        daily = {0: 1.0}  # Day 0 = 100% (install day)

        for i in range(len(milestones_ret) - 1):
            day_start, ret_start = milestones_ret[i]
            day_end, ret_end = milestones_ret[i + 1]

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

    def simulate_multi_week_real(w1_results, w2_results, params, num_seasons, daily_ret_free, daily_ret_paid, cashout_threshold):
        """Simulate multi-season wallet carryover using real daily retention data.

        Uses 4 segments matching Week 2 economics:
        1. Free → Stays Free: free prizes both weeks, free retention, no income
        2. Free → Converts W2: free prizes W1, paid prizes W2+, income in W2+
        3. Paid → Repurchase: paid prizes both weeks, paid retention, income both weeks
        4. Paid → Lapses: paid prizes W1, free prizes W2+, no income in W2+

        Each segment tracks its own wallet, with step-by-step cashout simulation.
        """
        season_days = params["pass_duration_days"]
        free_pct = params["free_pct"] / 100
        paid_pct = params["paid_conversion_pct"] / 100
        repurchase_rate = params["w2_repurchase_rate"]
        w2_free_conv = params["w2_free_conversion"]

        w1_net_income = params["price_point"] * (1 - params["platform_take"]) - params["paypal_fee"]
        w2_net_income = params["w2_price_point"] * (1 - params["platform_take"]) - params["paypal_fee"]

        # 4 segments with per-season behavior
        # Each has: w1_wallet_key, w2_wallet_key, w1_income, w2_income, incidence, w1_ret_curve, w2_ret_curve
        segments = [
            {"name": "Free \u2192 Stays Free",
             "w1_wallet_key": "w_fe", "w2_wallet_key": "w_fe",
             "w1_income": 0.0, "w2_income": 0.0,
             "incidence": free_pct * (1 - w2_free_conv),
             "w1_ret_curve": daily_ret_free, "w2_ret_curve": daily_ret_free},
            {"name": "Free \u2192 Converts W2",
             "w1_wallet_key": "w_fe", "w2_wallet_key": "w_pe",
             "w1_income": 0.0, "w2_income": w2_net_income,
             "incidence": free_pct * w2_free_conv,
             "w1_ret_curve": daily_ret_free, "w2_ret_curve": daily_ret_paid},
            {"name": "Paid \u2192 Repurchase",
             "w1_wallet_key": "w_pe", "w2_wallet_key": "w_pe",
             "w1_income": w1_net_income, "w2_income": w2_net_income,
             "incidence": paid_pct * repurchase_rate,
             "w1_ret_curve": daily_ret_paid, "w2_ret_curve": daily_ret_paid},
            {"name": "Paid \u2192 Lapses",
             "w1_wallet_key": "w_pe", "w2_wallet_key": "w_fe",
             "w1_income": w1_net_income, "w2_income": 0.0,
             "incidence": paid_pct * (1 - repurchase_rate),
             "w1_ret_curve": daily_ret_paid, "w2_ret_curve": daily_ret_free},
        ]

        snapshots = []

        for seg in segments:
            balance = 0.0
            cumulative_income = 0.0
            cumulative_payout = 0.0
            cumulative_prizes_won = 0.0

            for season in range(1, num_seasons + 1):
                end_day = season * season_days

                if season == 1:
                    season_results = w1_results
                    season_income_per = seg["w1_income"]
                    wallet_key = seg["w1_wallet_key"]
                    ret_curve = seg["w1_ret_curve"]
                else:
                    season_results = w2_results
                    season_income_per = seg["w2_income"]
                    wallet_key = seg["w2_wallet_key"]
                    ret_curve = seg["w2_ret_curve"]

                surviving = ret_curve.get(end_day, ret_curve[max(ret_curve.keys())])

                season_income = season_income_per * surviving
                cumulative_income += season_income

                # Step-by-step simulation
                ev_key = "ev_free" if wallet_key == "w_fe" else "ev_paid"
                season_cashout = 0.0
                season_ev_total = 0.0
                for r in season_results:
                    step_ev = r[ev_key]
                    season_ev_total += step_ev
                    balance += step_ev
                    if balance >= cashout_threshold:
                        season_cashout += balance * surviving
                        balance = 0.0

                cumulative_prizes_won += season_ev_total * surviving
                cumulative_payout += season_cashout
                cashout_happened = season_cashout > 0

                snapshots.append({
                    "Season": season,
                    "Day": end_day,
                    "Segment": seg["name"],
                    "Data Source": "Week 1" if season == 1 else "Week 2",
                    "Retention": f"{surviving*100:.1f}%",
                    "Season Income": season_income,
                    "Balance": balance,
                    "Cashout": "Yes" if cashout_happened else "No",
                    "Season Payout": season_cashout,
                    "Cum. Income": cumulative_income,
                    "Cum. Payout": cumulative_payout,
                    "Cum. Position": cumulative_income - cumulative_payout,
                    "Cum. Prizes Won": cumulative_prizes_won,
                    "Incidence": seg["incidence"],
                })

        return snapshots

    multi_week_data = simulate_multi_week_real(results, w2_results, params, num_seasons, daily_retention_free, daily_retention_paid, cashout_threshold)
    mw_df = pd.DataFrame(multi_week_data)

    # Summary table: final season position by segment
    final_week_rows = [r for r in multi_week_data if r["Season"] == num_seasons]
    overall_multi_week = 0.0
    mw_summary = []
    for row in final_week_rows:
        seg_name = row["Segment"]
        incidence = row["Incidence"]
        contribution = row["Cum. Position"] * incidence
        overall_multi_week += contribution
        mw_summary.append({
            "Segment": seg_name,
            f"Balance (S{num_seasons})": f"\u00a3{row['Balance']:.2f}",
            "Cum. Income": f"\u00a3{row['Cum. Income']:.2f}",
            "Cum. Payout": f"\u00a3{row['Cum. Payout']:.2f}",
            "Net Position": f"\u00a3{row['Cum. Position']:.2f}",
            "Incidence": f"{incidence*100:.1f}%",
            "Contribution": f"\u00a3{contribution:.2f}",
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
        st.error(f"Blended position: **\u00a3{overall_multi_week:.2f}** per player over {num_seasons} season{'s' if num_seasons > 1 else ''} ({total_days} days).")
    else:
        st.success(f"Blended position: **\u00a3{overall_multi_week:.2f}** per player over {num_seasons} season{'s' if num_seasons > 1 else ''} ({total_days} days).")

    # Breakage analysis
    st.markdown("---")
    st.subheader("Breakage Analysis")
    total_prizes_won = 0.0
    total_paid_out = 0.0
    total_unredeemed = 0.0
    for row in final_week_rows:
        incidence = row["Incidence"]
        total_prizes_won += row["Cum. Prizes Won"] * incidence
        total_paid_out += row["Cum. Payout"] * incidence
        total_unredeemed += row["Balance"] * incidence

    breakage_rate = ((total_prizes_won - total_paid_out) / total_prizes_won * 100) if total_prizes_won > 0 else 0.0

    br_c1, br_c2, br_c3 = st.columns(3)
    with br_c1:
        st.metric("Total Prizes Won (blended)", f"\u00a3{total_prizes_won:.2f}",
                  help="Weighted sum of all expected prizes accumulated across segments over the full simulation period.")
    with br_c2:
        st.metric("Total Paid Out (blended)", f"\u00a3{total_paid_out:.2f}",
                  help="Weighted sum of all actual cashouts. Only counts prizes that hit the cashout threshold and were redeemed.")
    with br_c3:
        st.metric("Breakage Rate", f"{breakage_rate:.0f}%",
                  help="% of prizes won that are never cashed out. Higher breakage = more favorable for the house. "
                       "Caused by players churning before hitting the cashout threshold, or balance sitting below the threshold at end of simulation.")

    # Week-by-week detail with segment filter
    with st.expander("Season-by-season detail"):
        all_segments = sorted(set(r["Segment"] for r in multi_week_data))
        selected_segments = st.multiselect(
            "Show segments", all_segments, default=all_segments[:1],
            help="Select one or more segments to view their weekly breakdown.",
            key="combined_segment_filter"
        )
        if selected_segments:
            filtered_df = mw_df[mw_df["Segment"].isin(selected_segments)].copy()
            for col in ["Season Income", "Season Payout", "Cum. Income", "Cum. Payout", "Cum. Position", "Balance"]:
                filtered_df[col] = filtered_df[col].apply(lambda x: f"\u00a3{x:.2f}")
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        else:
            st.info("Select at least one segment above.")

    # Cumulative Breakage Area Chart
    st.markdown("---")
    st.subheader("Cumulative Prizes Won vs. Paid Out")
    st.caption("The gap between the two lines is breakage — prizes won but never cashed out. Watch it grow or shrink over time.")

    # Build cumulative blended values per season
    cum_labels = []
    cum_prizes = []
    cum_paidout = []
    cum_breakage_pct = []

    for season_num in range(1, num_seasons + 1):
        season_rows = [r for r in multi_week_data if r["Season"] == season_num]
        label = f"S{season_num} (D{season_num * pass_duration_days})"
        cum_labels.append(label)

        prizes = 0.0
        paidout = 0.0
        for row in season_rows:
            incidence = row["Incidence"]
            prizes += row["Cum. Prizes Won"] * incidence
            paidout += row["Cum. Payout"] * incidence

        cum_prizes.append(prizes)
        cum_paidout.append(paidout)
        brk = ((prizes - paidout) / prizes * 100) if prizes > 0 else 0
        cum_breakage_pct.append(brk)

    fig_area = go.Figure()
    fig_area.add_trace(go.Scatter(
        x=cum_labels, y=cum_prizes,
        name="Prizes Won",
        mode="lines+markers",
        line=dict(color="#636EFA", width=2),
        fill="tozeroy",
        fillcolor="rgba(99, 110, 250, 0.15)",
    ))
    fig_area.add_trace(go.Scatter(
        x=cum_labels, y=cum_paidout,
        name="Paid Out",
        mode="lines+markers",
        line=dict(color="#EF553B", width=2),
        fill="tozeroy",
        fillcolor="rgba(239, 85, 59, 0.15)",
    ))
    # Annotate breakage % at each season
    for i, label in enumerate(cum_labels):
        gap = cum_prizes[i] - cum_paidout[i]
        midpoint = cum_paidout[i] + gap / 2
        fig_area.add_annotation(
            x=label, y=midpoint,
            text=f"{cum_breakage_pct[i]:.0f}%",
            showarrow=False,
            font=dict(size=12, color="#636EFA"),
            bgcolor="rgba(255,255,255,0.7)",
            borderpad=3,
        )
    fig_area.update_layout(
        xaxis_title="Season",
        yaxis_title="Blended \u00a3 per Player",
        height=400,
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig_area, use_container_width=True)


# ===================================================================
# SAVE LOGIC (after all tabs so W1 and W2 edited data are available)
# ===================================================================

def _clean_df_for_json(df):
    """Convert a DataFrame to a list of dicts with native Python types for JSON serialization."""
    rows = []
    for i in range(len(df)):
        s = df.iloc[i].to_dict()
        clean = {}
        for k, v in s.items():
            if isinstance(v, (np.integer,)):
                clean[k] = int(v)
            elif isinstance(v, (np.floating,)):
                clean[k] = float(v)
            elif pd.isna(v):
                clean[k] = None
            else:
                clean[k] = v
        rows.append(clean)
    return rows

if save_clicked and save_name.strip():
    settings_to_save = {
        "pass_duration_weeks": pass_duration_weeks,
        "price_point": price_point,
        "platform_take_pct": int(platform_take * 100),
        "paypal_fee": paypal_fee,
        "target_rtp_pct": int(target_rtp * 100),
        "retention_free_pct": int(retention_free * 100),
        "retention_paid_pct": int(retention_paid * 100),
        "paid_conversion_pct": paid_conversion_pct,
        "cashout_threshold": cashout_threshold,
        "milestones": milestones,
        "w2_price_point": w2_price_point,
        "w2_repurchase_rate": int(w2_repurchase_rate * 100),
        "w2_free_conversion": int(w2_free_conversion * 100),
    }
    for ms, val in free_completions.items():
        settings_to_save[f"free_step{ms}"] = int(val * 100)
    for ms, val in paid_completions.items():
        settings_to_save[f"paid_step{ms}"] = int(val * 100)
    for ms, val in w2_free_completions.items():
        settings_to_save[f"w2_free_step{ms}"] = int(val * 100)
    for ms, val in w2_paid_completions.items():
        settings_to_save[f"w2_paid_step{ms}"] = int(val * 100)
    if is_revised:
        settings_to_save.update({
            "win_steps": win_steps,
            "no_win_steps": no_win_steps,
            "paid_multiplier": paid_multiplier,
        })

    # Save W1 step data from edited table
    _w1_save = recalc_df if "recalc_df" in dir() else base_df
    step_data = _clean_df_for_json(_w1_save)

    # Save W2 step data from edited table
    _w2_save = w2_recalc_df if "w2_recalc_df" in dir() else base_df
    w2_step_data = _clean_df_for_json(_w2_save)

    st.session_state.saved_models[save_name.strip()] = {
        "settings": settings_to_save,
        "step_data": step_data,
        "w2_step_data": w2_step_data,
    }
    st.toast(f"Saved model: {save_name.strip()}")
    st.rerun()
elif save_clicked and not save_name.strip():
    st.sidebar.warning("Please enter a name for your model")

st.markdown("---")
st.caption("Molly's Cash Battle Pass Model | Built for TXG | v5.0 — Week 2 Pass")
