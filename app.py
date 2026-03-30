import streamlit as st
import pandas as pd

st.set_page_config(page_title="ARNET Commission Calculator", layout="centered")
st.title("ARNET Commission Calculator")
st.caption("Commission calculator for CAPEX Build / Infra Build, IRU Arrangement, and Fiber Lease")


def money(x: float) -> str:
    return f"{x:,.2f}"


def pct(x: float) -> str:
    return f"{x:.2f}%"


currency = st.selectbox("Currency", ["RM", "USD"])
commission_type = st.selectbox(
    "Commission Type",
    [
        "CAPEX Build / Infra Build",
        "IRU Arrangement",
        "Fiber Lease",
    ],
)

st.divider()

# =========================================================
# 1) CAPEX BUILD / INFRA BUILD
# =========================================================
if commission_type == "CAPEX Build / Infra Build":
    st.subheader("CAPEX Build / Infra Build Commission")
    st.caption("Payout structure: 100% at RFS")

    project_name = st.text_input("Project Name")
    revenue = st.number_input(
        f"Project Revenue ({currency})",
        min_value=0.0,
        value=0.0,
        step=1000.0,
    )
    cost = st.number_input(
        f"Project Cost ({currency})",
        min_value=0.0,
        value=0.0,
        step=1000.0,
    )

    gp = revenue - cost
    margin = (gp / revenue * 100) if revenue > 0 else 0.0

    st.markdown("### Project Result")
    c1, c2 = st.columns(2)
    c1.metric("Net Project Gross Profit", f"{money(gp)} {currency}")
    c2.metric("GP Margin", pct(margin))

    commission_rate = 0.0
    if 20 <= margin <= 30:
        commission_rate = 5.0
    elif 30 < margin <= 40:
        commission_rate = 7.0
    elif margin > 40:
        commission_rate = 10.0

    if margin < 20:
        total_commission = 0.0
        st.warning("Commission only triggers when GP margin is at least 20%.")
    else:
        total_commission = gp * (commission_rate / 100)
        st.success(f"Commission triggered at {commission_rate:.2f}% of GP.")

    st.markdown("### Commission Pool")
    st.write(f"**Project Name:** {project_name if project_name else '-'}")
    st.write(f"**Total Commission Pool:** {money(total_commission)} {currency}")
    st.write("**Payout Structure:** 100% at RFS")

    split_df = pd.DataFrame(
        [
            ["Design team", 5.0, total_commission * 0.05],
            ["Delivery team", 13.5, total_commission * 0.135],
            ["Procurement team", 10.0, total_commission * 0.10],
            ["Finance team + Audit team", 1.5, total_commission * 0.015],
            ["Sales team", 70.0, total_commission * 0.70],
        ],
        columns=["Team", "Share %", f"Amount ({currency})"],
    )
    st.dataframe(split_df, use_container_width=True, hide_index=True)

# =========================================================
# 2) IRU ARRANGEMENT
# =========================================================
elif commission_type == "IRU Arrangement":
    st.subheader("IRU Arrangement Commission")

    project_name = st.text_input("Project Name")
    years = st.slider("IRU Term (Years)", min_value=5, max_value=15, value=5, step=1)
    collection_amount = st.number_input(
        f"Total Payment Collection Amount ({currency})",
        min_value=0.0,
        value=0.0,
        step=1000.0,
    )

    # Linear rate from 1.50% at 5 years to 2.60% at 15 years
    commission_rate = 1.50 + ((years - 5) / 10) * (2.60 - 1.50)
    commission_rate = round(commission_rate, 2)

    total_commission = collection_amount * (commission_rate / 100)
    collection_payout = total_commission * 0.667
    month13_payout = total_commission * 0.333

    st.markdown("### IRU Reference")
    st.caption("Commission rate increases from 1.50% at 5 years to 2.60% at 15 years, rounded to 2 decimal places.")

    ref_df = pd.DataFrame(
        [
            [5, 1.50],
            [6, 1.61],
            [7, 1.72],
            [8, 1.83],
            [9, 1.94],
            [10, 2.05],
            [11, 2.16],
            [12, 2.27],
            [13, 2.38],
            [14, 2.49],
            [15, 2.60],
        ],
        columns=["Years", "Commission %"],
    )
    st.dataframe(ref_df, use_container_width=True, hide_index=True)

    st.markdown("### IRU Result")
    c1, c2 = st.columns(2)
    c1.metric("Total Collection Amount", f"{money(collection_amount)} {currency}")
    c2.metric("Commission Rate", pct(commission_rate))

    st.write(f"**Project Name:** {project_name if project_name else '-'}")
    st.write(f"**Total Commission:** {money(total_commission)} {currency}")
    st.write(f"**Upon payment collection (66.7%):** {money(collection_payout)} {currency}")
    st.write(f"**After 13th month (33.3%):** {money(month13_payout)} {currency}")

    st.markdown("### Team Sharing")
    st.caption("Sales person = 70%, balance 30% shared equally among Design, Delivery and Procurement.")

    split_df = pd.DataFrame(
        [
            ["Sales team", 70.0, total_commission * 0.70],
            ["Design team", 10.0, total_commission * 0.10],
            ["Delivery team", 10.0, total_commission * 0.10],
            ["Procurement team", 10.0, total_commission * 0.10],
        ],
        columns=["Team", "Share %", f"Amount ({currency})"],
    )
    st.dataframe(split_df, use_container_width=True, hide_index=True)

# =========================================================
# 3) FIBER LEASE
# =========================================================
else:
    st.subheader("Fiber Lease Commission")

    lease_type = st.selectbox(
        "Resource Type",
        ["Offnet", "Onnet"],
        help=(
            "Offnet = resources sourced from external or third-party network.\n"
            "Onnet = resources delivered through ARNET own network or directly controlled network."
        ),
    )

    with st.expander("What Offnet / Onnet means", expanded=True):
        st.write("**Offnet**: resources sourced from external or third-party network coverage.")
        st.write("**Onnet**: resources delivered through ARNET own or directly controlled network coverage.")

    project_name = st.text_input("Project Name")
    first_month_revenue = st.number_input(
        f"First Month Revenue ({currency})",
        min_value=0.0,
        value=0.0,
        step=1000.0,
    )
    first_month_cost = st.number_input(
        f"First Month Cost ({currency})",
        min_value=0.0,
        value=0.0,
        step=1000.0,
    )

    first_month_gp = first_month_revenue - first_month_cost
    annualised_first_month_gp = first_month_gp * 12

    sales_amount = annualised_first_month_gp * 0.50
    support_amount = annualised_first_month_gp * 0.10
    total_commission = sales_amount + support_amount

    st.markdown("### Fiber Lease Result")
    c1, c2 = st.columns(2)
    c1.metric("First Month GP", f"{money(first_month_gp)} {currency}")
    c2.metric("Annualised First Month GP", f"{money(annualised_first_month_gp)} {currency}")

    st.write(f"**Project Name:** {project_name if project_name else '-'}")
    st.write(f"**Total Sales Commission:** {money(sales_amount)} {currency}")
    st.write(f"**Total Support Team Commission:** {money(support_amount)} {currency}")
    st.write(f"**Total Commission Payout:** {money(total_commission)} {currency}")

    if lease_type == "Offnet":
        support_group = "Procurement team + PM + Presales team"
    else:
        support_group = "PM + Presales team + Design team"

    split_df = pd.DataFrame(
        [
            ["Sales team", "50% of Annualised First Month GP", sales_amount],
            [support_group, "10% of Annualised First Month GP", support_amount],
        ],
        columns=["Team / Group", "Rule", f"Amount ({currency})"],
    )
    st.dataframe(split_df, use_container_width=True, hide_index=True)

    st.info(
        "Fiber Lease commission is based on annualised first month GP. "
        "Sales receives 50%, and the support team grouping receives 10%."
    )
