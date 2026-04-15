"""
StockTracker Admin UI
Simple Streamlit interface to manage the stocks table.
"""
import os
from datetime import date

import pandas as pd
import pymysql
import pymysql.cursors
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="StockTracker", page_icon="📈", layout="wide")


# ── DB helpers ────────────────────────────────────────────────────────────────

def get_conn():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


def fetch_stocks(sold: int) -> pd.DataFrame:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, symbol, name, sector, currency, initial_value, "
                "initial_quantity, initial_date, upper_threshold, lower_threshold, "
                "purchase_fee, sell_date "
                "FROM stocks WHERE sold = %s ORDER BY initial_date, id",
                (sold,),
            )
            rows = cur.fetchall()
    return pd.DataFrame(rows) if rows else pd.DataFrame()


# ── Page ──────────────────────────────────────────────────────────────────────

st.title("📈 StockTracker — Configuration")

tab_active, tab_sold, tab_add = st.tabs(["Active Stocks", "Sold Stocks", "Add Stock"])


# ── Active Stocks ─────────────────────────────────────────────────────────────

with tab_active:
    df = fetch_stocks(0)

    if df.empty:
        st.info("No active stocks.")
    else:
        st.markdown(f"**{len(df)} active positions**")

        edited = st.data_editor(
            df.set_index("id"),
            use_container_width=True,
            num_rows="fixed",
            column_config={
                "symbol":           st.column_config.TextColumn("Symbol", disabled=True),
                "name":             st.column_config.TextColumn("Name"),
                "sector":           st.column_config.SelectboxColumn("Sector", options=["PEA", "CTO"]),
                "currency":         st.column_config.SelectboxColumn("Currency", options=["EUR", "USD", "GBP"]),
                "initial_value":    st.column_config.NumberColumn("Buy Price", format="%.4f"),
                "initial_quantity": st.column_config.NumberColumn("Qty", step=1),
                "initial_date":     st.column_config.DateColumn("Buy Date"),
                "upper_threshold":  st.column_config.NumberColumn("Upper Target", format="%.4f"),
                "lower_threshold":  st.column_config.NumberColumn("Lower Stop", format="%.4f"),
                "purchase_fee":     st.column_config.NumberColumn("Fee", format="%.4f"),
                "sell_date":        None,
            },
            key="active_editor",
        )

        if st.button("💾 Save changes", type="primary"):
            original = df.set_index("id")
            try:
                diff = edited.compare(original)
                changed_ids = diff.index.unique().tolist()
            except Exception:
                changed_ids = []

            if not changed_ids:
                st.info("No changes to save.")
            else:
                try:
                    with get_conn() as conn:
                        with conn.cursor() as cur:
                            for row_id in changed_ids:
                                row = edited.loc[row_id]
                                cur.execute(
                                    """
                                    UPDATE stocks SET
                                        name=%s, sector=%s, currency=%s,
                                        initial_value=%s, initial_quantity=%s,
                                        initial_date=%s, upper_threshold=%s,
                                        lower_threshold=%s, purchase_fee=%s
                                    WHERE id=%s
                                    """,
                                    (
                                        row["name"], row["sector"], row["currency"],
                                        float(row["initial_value"]), int(row["initial_quantity"]),
                                        row["initial_date"], float(row["upper_threshold"]),
                                        float(row["lower_threshold"]),
                                        float(row["purchase_fee"]) if pd.notna(row.get("purchase_fee")) else None,
                                        int(row_id),
                                    ),
                                )
                        conn.commit()
                    st.success(f"Saved {len(changed_ids)} row(s).")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving: {e}")

        st.divider()

        col_sell, col_del = st.columns(2)

        with col_sell:
            with st.expander("Mark as Sold"):
                opts = {
                    f"{r['name']} ({r['symbol']}) — {r['initial_date']}": r["id"]
                    for _, r in df.iterrows()
                }
                chosen = st.selectbox("Stock", list(opts.keys()), key="sell_select")
                sell_date = st.date_input("Sell date", value=date.today(), key="sell_date_input")
                if st.button("Mark as Sold", key="mark_sold_btn"):
                    try:
                        with get_conn() as conn:
                            with conn.cursor() as cur:
                                cur.execute(
                                    "UPDATE stocks SET sold=1, sell_date=%s WHERE id=%s",
                                    (sell_date, opts[chosen]),
                                )
                            conn.commit()
                        st.success("Marked as sold.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

        with col_del:
            with st.expander("Delete a stock"):
                opts_del = {
                    f"{r['name']} ({r['symbol']}) — {r['initial_date']}": r["id"]
                    for _, r in df.iterrows()
                }
                chosen_del = st.selectbox("Stock", list(opts_del.keys()), key="del_select")
                if st.button("Delete", type="primary", key="del_btn"):
                    try:
                        with get_conn() as conn:
                            with conn.cursor() as cur:
                                cur.execute("DELETE FROM stocks WHERE id=%s", (opts_del[chosen_del],))
                            conn.commit()
                        st.success("Deleted.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")


# ── Sold Stocks ───────────────────────────────────────────────────────────────

with tab_sold:
    df_sold = fetch_stocks(1)

    if df_sold.empty:
        st.info("No sold stocks.")
    else:
        st.markdown(f"**{len(df_sold)} sold positions**")
        st.dataframe(
            df_sold.drop(columns=["id"]).set_index("symbol"),
            use_container_width=True,
        )


# ── Add Stock ─────────────────────────────────────────────────────────────────

with tab_add:
    with st.form("add_stock"):
        col1, col2 = st.columns(2)

        with col1:
            symbol           = st.text_input("Symbol (ISIN / ticker) *")
            name             = st.text_input("Name *")
            sector           = st.selectbox("Sector", ["PEA", "CTO"])
            currency         = st.selectbox("Currency", ["EUR", "USD", "GBP"])
            initial_date     = st.date_input("Purchase date", value=date.today())

        with col2:
            initial_value    = st.number_input("Purchase price *", min_value=0.0, format="%.4f")
            initial_quantity = st.number_input("Quantity", min_value=0, step=1, value=0)
            upper_threshold  = st.number_input("Upper target  (-1 = disabled)", value=-1.0, format="%.4f")
            lower_threshold  = st.number_input("Lower stop  (-1 = disabled)", value=-1.0, format="%.4f")
            purchase_fee     = st.number_input("Purchase fee  (0 = none)", min_value=0.0, format="%.4f", value=0.0)

        submitted = st.form_submit_button("Add stock", type="primary")

    if submitted:
        if not symbol.strip() or not name.strip() or initial_value <= 0:
            st.error("Symbol, name, and a positive purchase price are required.")
        else:
            try:
                with get_conn() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            INSERT INTO stocks
                                (symbol, name, sector, currency, initial_value,
                                 initial_quantity, initial_date, upper_threshold,
                                 lower_threshold, purchase_fee, sold)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0)
                            """,
                            (
                                symbol.strip(), name.strip(), sector, currency,
                                initial_value, int(initial_quantity), initial_date,
                                upper_threshold, lower_threshold,
                                purchase_fee if purchase_fee > 0 else None,
                            ),
                        )
                    conn.commit()
                st.success(f"Added **{name}** ({symbol}).")
            except Exception as e:
                st.error(f"Error: {e}")
