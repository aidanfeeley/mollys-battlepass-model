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
    {"step": 1,  "level": 1,   "tickets": 50,     "sess_med": 1,    "sess_eng": 1,  "type": "Instant Win",  "win_chance": 1.00,  "free_prize": 0.25,  "paid_prize": 0.50},
    {"step": 2,  "level": 11,  "tickets": 550,    "sess_med": 1,    "sess_eng": 1,  "type": "Instant Win",  "win_chance": 0.01,  "free_prize": 0.50,  "paid_prize": 1.00},
    {"step": 3,  "level": 21,  "tickets": 1155,   "sess_med": 1,    "sess_eng": 1,  "type": "Instant Win",  "win_chance": 1.00,  "free_prize": 0.25,  "paid_prize": 0.50},
    {"step": 4,  "level": 31,  "tickets": 1805,   "sess_med": 2,    "sess_eng": 1,  "type": "Instant Win",  "win_chance": 0.01,  "free_prize": 1.50,  "paid_prize": 3.00},
    {"step": 5,  "level": 41,  "tickets": 2455,   "sess_med": 3,    "sess_eng": 1,  "type": "Instant Win",  "win_chance": 1.00,  "free_prize": 0.25,  "paid_prize": 0.50},
    {"step": 6,  "level": 51,  "tickets": 3105,   "sess_med": 3,    "sess_eng": 1,  "type": "Sweepstakes",  "win_chance": 0.00,  "free_prize": 0.00,  "paid_prize": 0.00,  "sweep_amt": 100},
    {"step": 7,  "level": 61,  "tickets": 3755,   "sess_med": 4,    "sess_eng": 2,  "type": "Instant Win",  "win_chance": 0.01,  "free_prize": 1.50,  "paid_prize": 3.00},
    {"step": 8,  "level": 72,  "tickets": 4470,   "sess_med": 5,    "sess_eng": 2,  "type": "Instant Win",  "win_chance": 1.00,  "free_prize": 0.25,  "paid_prize": 0.50},
    {"step": 9,  "level": 83,  "tickets": 5185,   "sess_med": 6,    "sess_eng": 2,  "type": "Instant Win",  "win_chance": 0.01,  "free_prize": 0.50,  "paid_prize": 1.00},
    {"step": 10, "level": 94,  "tickets": 5900,   "sess_med": 7,    "sess_eng": 3,  "type": "Instant Win",  "win_chance": 1.00,  "free_prize": 0.25,  "paid_prize": 0.50},
    {"step": 11, "level": 105, "tickets": 6615,   "sess_med": 8,    "sess_eng": 4,  "type": "Sweepstakes",  "win_chance": 0.00,  "free_prize": 0.00,  "paid_prize": 0.00,  "sweep_amt": 1000},
    {"step": 12, "level": 116, "tickets": 7330,   "sess_med": 9,    "sess_eng": 4,  "type": "Instant Win",  "win_chance": 0.01,  "free_prize": 0.50,  "paid_prize": 1.00},
    {"step": 13, "level": 127, "tickets": 8045,   "sess_med": 10,   "sess_eng": 4,  "type": "Instant Win",  "win_chance": 0.01,  "free_prize": 1.50,  "paid_prize": 3.00},
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
        # Track whether we've already processed this exact file to avoid re-importing on every rerun
        file_hash = hash(uploaded.name + str(uploaded.size))
        if st.session_state.get("_last_import_hash") != file_hash:
            try:
                raw = uploaded.read()
                imported = json.loads(raw)
                if imported and isinstance(imported, dict):
                    st.session_state.saved_models.update(imported)  # Overwrite existing models with same name
                    st.session_state["_last_import_hash"] = file_hash
                    st.rerun()  # Safe to rerun here — hash guard prevents infinite loop
            except (json.JSONDecodeError, Exception) as e:
                st.sidebar.error(f"Invalid JSON file: {e}")

st.sidebar.markdown("---")
st.sidebar.header("Economics")

# Get defaults: from saved model if loading, otherwise from mode
def get_default(key, revised_val, current_val):
    if is_saved and key in saved.get("settings", {}):
        return saved["settings"][key]
    return revised_val if model_mode == "Revised Model" else current_val

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
st.sidebar.header("Player Segments")

free_median_pct = st.sidebar.slider("Free Median %", 0, 100,
    get_default("free_median_pct", 50, 50), 5)
free_engaged_pct = st.sidebar.slider("Free Engaged %", 0, 100,
    get_default("free_engaged_pct", 30, 30), 5)
paid_median_pct = st.sidebar.slider("Paid Median %", 0, 100,
    get_default("paid_median_pct", 5, 5), 1)
paid_engaged_pct = st.sidebar.slider("Paid Engaged %", 0, 100,
    get_default("paid_engaged_pct", 15, 15), 1)

total_pct = free_median_pct + free_engaged_pct + paid_median_pct + paid_engaged_pct
if total_pct != 100:
    st.sidebar.warning(f"Segments sum to {total_pct}%, should be 100%")

st.sidebar.markdown("---")
st.sidebar.header("D7 Retention (Cashout Rate)")

retention_free = st.sidebar.slider(
    "Free Tier D7 Retention %", min_value=0, max_value=100,
    value=get_default("retention_free_pct", 15, 15), step=5,
    help="% of free players still active at D7 who collect winnings"
) / 100

retention_paid = st.sidebar.slider(
    "Paid Tier D7 Retention %", min_value=0, max_value=100,
    value=get_default("retention_paid_pct", 30, 30), step=5,
    help="% of paid players still active at D7 who collect winnings"
) / 100

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
    "retention_free": retention_free,
    "retention_paid": retention_paid,
    "free_median_pct": free_median_pct,
    "free_engaged_pct": free_engaged_pct,
    "paid_median_pct": paid_median_pct,
    "paid_engaged_pct": paid_engaged_pct,
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
    SMALL_FLOOR, SMALL_CEIL = 1.50, 2.00
    PUNCH_FLOOR, PUNCH_CEIL = 3.00, 5.00
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
econ_rows, overall_position, prize_available, calculated_rtp = compute_economics(results, params)


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
_editor_key_parts = [model_mode, str(price_point), str(int(platform_take*100))]
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
        "Step": st.column_config.NumberColumn("Step", width="small"),
        "Level": st.column_config.NumberColumn("Level", width="small"),
        "Tickets": st.column_config.NumberColumn("Tickets", format="%d"),
        "Win % (input)": st.column_config.NumberColumn("Win %", min_value=0, max_value=100, step=0.5, format="%.1f%%",
            help="Set your desired win chance per step."),
        "Free Prize": st.column_config.NumberColumn("Free Prize", min_value=0, max_value=100, step=0.25, format="\u00a3%.2f"),
        "Paid Prize": st.column_config.NumberColumn("Paid Prize", min_value=0, max_value=200, step=0.25, format="\u00a3%.2f"),
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
econ_rows, overall_position, prize_available, calculated_rtp = compute_economics(results, params)

# Key metrics row (placed AFTER recalculation so it reflects table edits)
st.markdown("---")
c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
    st.metric("Pass Price", f"\u00a3{price_point:.2f}")
with c2:
    st.metric("Net Rev / Paid User", f"\u00a3{net_rev:.2f}",
              help="Pass Price minus platform take and PayPal fee. This is the max you can pay out per paid player before losing money. Shown as the green dashed line on the wallet chart.")
with c3:
    st.metric("RTP (Target)", f"{target_rtp*100:.0f}%")
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
        "price_point": price_point,
        "platform_take_pct": int(platform_take * 100),
        "paypal_fee": paypal_fee,
        "target_rtp_pct": int(target_rtp * 100),
        "retention_free_pct": int(retention_free * 100),
        "retention_paid_pct": int(retention_paid * 100),
        "free_median_pct": free_median_pct,
        "free_engaged_pct": free_engaged_pct,
        "paid_median_pct": paid_median_pct,
        "paid_engaged_pct": paid_engaged_pct,
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
    "Wallet (Free Eng)": f"\u00a3{r['w_fe']:.2f}",
    "Wallet (Paid Eng)": f"\u00a3{r['w_pe']:.2f}",
} for r in results])
st.dataframe(recalc_display, use_container_width=True, hide_index=True)

# Economics table
st.markdown("---")
st.subheader("Economic Summary by Segment")
st.dataframe(
    pd.DataFrame(econ_rows),
    use_container_width=True,
    hide_index=True,
    column_config={
        "Segment": st.column_config.TextColumn(
            "Segment",
            help="Player segment. Free = didn't buy the pass. Paid = bought the pass. Median = stops playing at the FTUE boundary. Engaged = plays through all 28 steps."
        ),
        "Exp. Wallet": st.column_config.TextColumn(
            "Exp. Wallet",
            help="Total expected prize value accumulated across all steps for this segment. This is the sum of (Prize x Win Chance) at each step the player reaches."
        ),
        "Income": st.column_config.TextColumn(
            "Income",
            help="Gross revenue from this segment. Free players = £0. Paid players = the pass price. This is gross before platform fees."
        ),
        "D7 Retention": st.column_config.TextColumn(
            "D7 Retention",
            help="Estimated % of players in this segment who actually cash out their winnings. Higher = more payouts. Set in the sidebar under D7 Retention."
        ),
        "Expected Payout": st.column_config.TextColumn(
            "Expected Payout",
            help="What the house actually pays out. Calculated as: Expected Wallet x D7 Retention. The rest is breakage (won but never collected)."
        ),
        "Net Position": st.column_config.TextColumn(
            "Net Position",
            help="Profit or loss per player in this segment. Calculated as: Income - Expected Payout. Negative means the house loses money on this segment."
        ),
        "Incidence": st.column_config.TextColumn(
            "Incidence",
            help="What % of the total player base falls in this segment. Set in the sidebar under Player Segments. All four should sum to 100%."
        ),
        "Contribution": st.column_config.TextColumn(
            "Contribution",
            help="This segment's weighted impact on overall profit. Calculated as: Net Position x Incidence. The sum of all four contributions = Overall Position."
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
st.caption("How does profitability hold up if more paid players cash out? Fengxing recommends stress-testing at 40-50%.")

def stress_test_economics(results, params, paid_ret_override):
    """Run economics with a different paid retention rate."""
    stress_params = {**params, "retention_paid": paid_ret_override}
    _, stress_overall, _, stress_rtp = compute_economics(results, stress_params)
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
st.caption("Molly's Cash Battle Pass Model | Built for TXG | v3.0")
