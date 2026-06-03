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

st.info(
    "Sales & Marketing team is treated as one team. "
    "Marketing team will only receive 10% from the original Sales team portion "
    "if Marketing Team Involvement is selected as Yes. "
    "If No, the full original Sales team portion remains with Sales team."
)

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

    marketing_involved = st.radio(
        "Marketing Team Involvement?",
        ["No", "Yes"],
        horizontal=True,
        help=(
            "Select Yes only if the sales is linked to marketing team effort. "
            "If Yes, 10% will be allocated to Marketing team from the original Sales team portion."
        ),
    )

    marketing_linked = marketing_involved == "Yes"

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

    # Original Sales team allocation is 70%
    # If Marketing Team Involvement = Yes:
    # Sales team gets 60%, Marketing team gets 10%
    # If Marketing Team Involvement = No:
    # Sales team gets full 70%, Marketing team gets 0%
    if marketing_linked:
        sales_share = 60.0
        marketing_share = 10.0
    else:
        sales_share = 70.0
        marketing_share = 0.0

    st.markdown("### Commission Pool")

    st.write(f"**Project Name:** {project_name if project_name else '-'}")
    st.write(f"**Total Commission Pool:** {money(total_commission)} {currency}")
    st.write("**Payout Structure:** 100% at RFS")

    if marketing_linked:
        st.info(
            "Marketing Team Involvement: Yes. "
            "Marketing team receives 10% from the original Sales team portion. "
            "Sales team receives the remaining 60%."
        )
    else:
        st.info(
            "Marketing Team Involvement: No. "
            "Marketing team receives 0%. "
            "Sales team receives the full original 70% Sales team portion."
        )

    split_df = pd.DataFrame(
        [
            ["Design team", 5.0, total_commission * 0.05],
            ["Delivery team", 13.5, total_commission * 0.135],
            ["Procurement team", 10.0, total_commission * 0.10],
            ["Finance team + Audit team", 1.5, total_commission * 0.015],
            ["Sales team", sales_share, total_commission * (sales_share / 100)],
            ["Marketing team", marketing_share, total_commission * (marketing_share / 100)],
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

    years = st.slider(
        "IRU Term (Years)",
        min_value=5,
        max_value=15,
        value=5,
        step=1,
    )

    otc_amount = st.number_input(
        f"Total IRU OTC Amount ({currency})",
        min_value=0.0,
        value=0.0,
        step=1000.0,
    )

    marketing_involved = st.radio(
        "Marketing Team Involvement?",
        ["No", "Yes"],
        horizontal=True,
        help=(
            "Select Yes only if the sales is linked to marketing team effort. "
            "If Yes, 10% will be allocated to Marketing team from the original Sales team portion."
        ),
    )

    marketing_linked = marketing_involved == "Yes"

    # Linear rate from 1.50% at 5 years to 2.60% at 15 years
    commission_rate = 1.50 + ((years - 5) / 10) * (2.60 - 1.50)
    commission_rate = round(commission_rate, 2)

    total_commission = otc_amount * (commission_rate / 100)

    collection_payout = total_commission * 0.667
    month13_payout = total_commission * 0.333

    st.markdown("### IRU Reference")

    st.caption(
        "Commission rate increases from 1.50% at 5 years to 2.60% at 15 years, "
        "rounded to 2 decimal places."
    )

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
    c1.metric("Total OTC Amount", f"{money(otc_amount)} {currency}")
    c2.metric("Commission Rate", pct(commission_rate))

    st.write(f"**Project Name:** {project_name if project_name else '-'}")
    st.write(f"**Total Commission:** {money(total_commission)} {currency}")
    st.write(f"**Upon payment collection (66.7%):** {money(collection_payout)} {currency}")
    st.write(f"**After 13th month (33.3%):** {money(month13_payout)} {currency}")

    st.markdown("### Team Sharing")

    st.caption(
        "Sales & Marketing team is one team. "
        "Original Sales team portion is 70%. "
        "If Marketing Team Involvement is Yes, Sales team gets 60% and Marketing team gets 10%. "
        "Balance 30% is shared equally among Design, Delivery and Procurement."
    )

    # Original Sales team allocation is 70%
    # If Marketing Team Involvement = Yes:
    # Sales team gets 60%, Marketing team gets 10%
    # If Marketing Team Involvement = No:
    # Sales team gets full 70%, Marketing team gets 0%
    if marketing_linked:
        sales_share = 0.60
        marketing_share = 0.10
    else:
        sales_share = 0.70
        marketing_share = 0.00

    team_rows = []

    for team, share in [
        ("Sales team", sales_share),
        ("Marketing team", marketing_share),
        ("Design team", 0.10),
        ("Delivery team", 0.10),
        ("Procurement team", 0.10),
    ]:
        team_total = total_commission * share
        team_collection = team_total * 0.667
        team_month13 = team_total * 0.333

        team_rows.append(
            [
                team,
                share * 100,
                team_total,
                team_collection,
                team_month13,
            ]
        )

    split_df = pd.DataFrame(
        team_rows,
        columns=[
            "Team",
            "Share %",
            f"Total ({currency})",
            f"At collection (66.7%) ({currency})",
            f"After 13th month (33.3%) ({currency})",
        ],
    )

    st.dataframe(split_df, use_container_width=True, hide_index=True)

    if marketing_linked:
        st.info(
            "Marketing Team Involvement: Yes. "
            "Marketing team receives 10% from the original Sales team portion. "
            "Sales team receives the remaining 60%."
        )
    else:
        st.info(
            "Marketing Team Involvement: No. "
            "Marketing team receives 0%. "
            "Sales team receives the full original 70% Sales team portion."
        )


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

    lease_mode = st.selectbox(
        "Lease Mode",
        ["New lease", "Renewal lease"],
        help="New lease follows normal commission split. Renewal lease gets 30% of first month GP.",
    )

    project_name = st.text_input("Project Name")

    lease_term = st.slider(
        "Fiber Lease Term (Years)",
        min_value=1,
        max_value=15,
        value=3,
        step=1,
    )

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

    marketing_involved = st.radio(
        "Marketing Team Involvement?",
        ["No", "Yes"],
        horizontal=True,
        help=(
            "Select Yes only if the sales is linked to marketing team effort. "
            "For Fiber Lease New lease, Marketing will receive 10% of first month GP "
            "from the original Sales team portion."
        ),
    )

    marketing_linked = marketing_involved == "Yes"

    first_month_gp = first_month_revenue - first_month_cost

    if lease_term < 3:
        st.warning("Fiber Lease commission is triggered only for term >= 3 years. No commission will be paid.")

        sales_amount = 0.0
        marketing_amount = 0.0
        support_amount = 0.0
        renewal_commission = 0.0
        total_commission = 0.0

    else:
        if lease_mode == "New lease":
            # Original Sales team portion is 50% of First Month GP.
            # If Marketing Team Involvement = Yes:
            # Sales team gets 40%, Marketing team gets 10%
            # If Marketing Team Involvement = No:
            # Sales team gets full 50%, Marketing team gets 0%
            if marketing_linked:
                sales_amount = first_month_gp * 0.40
                marketing_amount = first_month_gp * 0.10
            else:
                sales_amount = first_month_gp * 0.50
                marketing_amount = 0.0

            support_amount = first_month_gp * 0.10
            renewal_commission = 0.0

        else:
            # Renewal lease remains 30% to account owner.
            # Marketing sharing is not applied to renewal lease unless separately approved.
            sales_amount = 0.0
            marketing_amount = 0.0
            support_amount = 0.0
            renewal_commission = first_month_gp * 0.30

        total_commission = (
            sales_amount
            + marketing_amount
            + support_amount
            + renewal_commission
        )

    st.markdown("### Fiber Lease Result")

    c1, c2 = st.columns(2)
    c1.metric("First Month GP", f"{money(first_month_gp)} {currency}")
    c2.metric("Fiber Lease Term", f"{lease_term} years")

    st.write(f"**Project Name:** {project_name if project_name else '-'}")

    if lease_term >= 3:
        if lease_mode == "New lease":
            if marketing_linked:
                st.write(f"**Sales Team Commission (40% of First Month GP):** {money(sales_amount)} {currency}")
                st.write(f"**Marketing Team Commission (10% of First Month GP):** {money(marketing_amount)} {currency}")
            else:
                st.write(f"**Sales Team Commission (50% of First Month GP):** {money(sales_amount)} {currency}")
                st.write(f"**Marketing Team Commission:** {money(marketing_amount)} {currency}")

            st.write(f"**Support Team Commission (10% of First Month GP):** {money(support_amount)} {currency}")

        else:
            st.write(f"**Renewal Commission (30% of First Month GP):** {money(renewal_commission)} {currency}")

    st.write(f"**Total Commission Payout:** {money(total_commission)} {currency}")

    if lease_type == "Offnet":
        support_group = "Procurement team + PM + Presales team"
    else:
        support_group = "PM + Presales team + Design team"

    split_rows = []

    if lease_term >= 3:
        if lease_mode == "New lease":
            if marketing_linked:
                split_rows = [
                    ["Sales team", "40% of First Month GP", sales_amount],
                    ["Marketing team", "10% of First Month GP", marketing_amount],
                    [support_group, "10% of First Month GP", support_amount],
                ]
            else:
                split_rows = [
                    ["Sales team", "50% of First Month GP", sales_amount],
                    ["Marketing team", "0% because Marketing Team Involvement is No", marketing_amount],
                    [support_group, "10% of First Month GP", support_amount],
                ]
        else:
            split_rows = [
                ["Account owner", "30% of First Month GP (Renewal)", renewal_commission]
            ]

    split_df = pd.DataFrame(
        split_rows,
        columns=["Team / Group", "Rule", f"Amount ({currency})"],
    )

    st.dataframe(split_df, use_container_width=True, hide_index=True)

    if lease_mode == "New lease":
        if marketing_linked:
            st.info(
                "Marketing Team Involvement: Yes. "
                "For Fiber Lease New lease, Marketing team receives 10% of First Month GP "
                "from the original Sales team portion. "
                "Sales team receives the remaining 40%. "
                "Support team remains 10%."
            )
        else:
            st.info(
                "Marketing Team Involvement: No. "
                "For Fiber Lease New lease, Marketing team receives 0%. "
                "Sales team receives the full original 50% of First Month GP. "
                "Support team remains 10%."
            )
    else:
        st.info(
            "Fiber Lease renewal commission is based on 30% of First Month GP to the account owner. "
            "Marketing sharing is not applied to renewal lease unless separately approved."
        )
