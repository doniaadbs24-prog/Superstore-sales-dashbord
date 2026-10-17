# ==================================================
# 1. SETUP: libraries, page settings, colors, style
# ==================================================
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Superstore Sales Dashboard", layout="wide")
px.defaults.color_discrete_sequence = ["#0F766E"]   # one color for all charts

st.markdown("""
<style>
.note-box {
    background-color: #F0F5F4;
    border-left: 5px solid #0F766E;
    padding: 12px 16px;
    border-radius: 6px;
    margin: 8px 0 24px 0;
    color: #1F2937;
}
.note-box b { color: #0F766E; }
</style>
""", unsafe_allow_html=True)


def insight(title, text):
    """Shows a short note box under a chart."""
    st.markdown(f'<div class="note-box"><b>{title}:</b> {text}</div>', unsafe_allow_html=True)


# ==================================================
# 2. DATA: read the clean file
# ==================================================
df = pd.read_csv("clean_sales.csv", parse_dates=["Order Date", "Ship Date"])


# ==================================================
# 3. HEADER: title and note
# ==================================================
st.title("Superstore Sales Dashboard")
st.caption("Sales analysis, 2015-2018")
st.markdown('<div class="note-box"><b>Note:</b> Sales figures represent revenue, not profit. The dataset has no cost or profit column.</div>', unsafe_allow_html=True)


# ==================================================
# 4. FILTERS (sidebar)
# ==================================================
st.sidebar.header("Filters")
years = st.sidebar.multiselect("Year", sorted(df["Year"].unique()), default=sorted(df["Year"].unique()))
regions = st.sidebar.multiselect("Region", sorted(df["Region"].unique()), default=sorted(df["Region"].unique()))


# ==================================================
# 5. FILTERED DATA: one table used by everything
#    An empty filter means "all values", so nothing disappears
# ==================================================
selected_years = years if years else list(df["Year"].unique())
selected_regions = regions if regions else list(df["Region"].unique())

region_view = df[df["Year"].isin(selected_years) & df["Region"].isin(selected_regions)]


# ==================================================
# 6. KPI CARDS
# ==================================================
col1, col2, col3 = st.columns(3)
col1.metric("Total Sales", f"{region_view['Sales'].sum():,.0f}")
col2.metric("Orders", f"{region_view['Order ID'].nunique():,}")
col3.metric("Customers", f"{region_view['Customer Name'].nunique():,}")


# ==================================================
# 7. SALES BY YEAR and BY CATEGORY
# ==================================================
yearly = region_view.groupby("Year")["Sales"].sum().reset_index()
fig_year = px.line(yearly, x="Year", y="Sales", markers=True, title="Sales by Year")
fig_year.update_xaxes(dtick=1)
st.plotly_chart(fig_year, use_container_width=True)
insight("Growth (all data)", "Sales dipped 4.3% in 2016, then grew 30.6% in 2017 and 20.3% in 2018.")

cat = region_view.groupby("Category")["Sales"].sum().sort_values(ascending=False).reset_index()
cat["Color"] = ["Top" if i == 0 else "Other" for i in range(len(cat))]   # highest = Top
fig_cat = px.bar(cat, x="Category", y="Sales", title="Sales by Category",
                 color="Color",
                 color_discrete_map={"Top": "#0F766E", "Other": "lightgray"})
fig_cat.update_layout(showlegend=False)
st.plotly_chart(fig_cat, use_container_width=True)
insight("Category (all data)", "Technology leads with 36.6% of total sales, but the gap between categories is small.")


# ==================================================
# 8. SALES BY MONTH
# ==================================================
monthly = region_view.groupby("Month")["Sales"].sum().reset_index()
monthly["Color"] = ["Top" if s == monthly["Sales"].max() else "Other" for s in monthly["Sales"]]
fig_month = px.bar(monthly, x="Month", y="Sales", title="Sales by Month",
                   color="Color",
                   color_discrete_map={"Top": "#0F766E", "Other": "lightgray"})
fig_month.update_xaxes(dtick=1)
fig_month.update_layout(showlegend=False)
st.plotly_chart(fig_month, use_container_width=True)
insight("Seasonality (all data)", "September, November, and December generate about 43% of total sales.")


# ==================================================
# 9. REGION CHART AND TABLES
# ==================================================
reg = region_view.groupby("Region")["Sales"].sum().sort_values(ascending=False).reset_index()
reg["Color"] = ["Top" if i == 0 else "Other" for i in range(len(reg))]
fig_reg = px.bar(reg, x="Region", y="Sales", title="Sales by Region",
                 color="Color",
                 color_discrete_map={"Top": "#0F766E", "Other": "lightgray"})
fig_reg.update_layout(showlegend=False)
st.plotly_chart(fig_reg, use_container_width=True)
insight("Region (all data)", "West and East make up about 61% of sales. South is the weakest at 17.2% and grew only 18% since 2015, compared with 70% for West.")

st.subheader("Sales by Region and Year")
region_year = region_view.pivot_table(values="Sales", index="Region", columns="Year", aggfunc="sum").round(0)
st.dataframe(region_year, use_container_width=True)

st.subheader("Sales by Region and Category")
region_cat = region_view.pivot_table(values="Sales", index="Region", columns="Category", aggfunc="sum").round(0)
st.dataframe(region_cat, use_container_width=True)


# ==================================================
# 10. TOP 10 CUSTOMERS and TOP 10 PRODUCTS
# ==================================================
top_cust = region_view.groupby("Customer Name")["Sales"].sum().sort_values(ascending=False).head(10).reset_index()
top_cust["Color"] = ["Top" if i == 0 else "Other" for i in range(len(top_cust))]
fig_cust = px.bar(top_cust.sort_values("Sales"), x="Sales", y="Customer Name",
                  orientation="h", title="Top 10 Customers",
                  color="Color",
                  color_discrete_map={"Top": "#0F766E", "Other": "lightgray"})
fig_cust.update_layout(showlegend=False)
st.plotly_chart(fig_cust, use_container_width=True)
insight("Customers (all data)", "The top 10 of 793 customers generate only 6.8% of sales, so revenue is not concentrated.")

top_prod = region_view.groupby("Product Name")["Sales"].sum().sort_values(ascending=False).head(10).reset_index()
top_prod["Color"] = ["Top" if i == 0 else "Other" for i in range(len(top_prod))]
fig_prod = px.bar(top_prod.sort_values("Sales"), x="Sales", y="Product Name",
                  orientation="h", title="Top 10 Products",
                  color="Color",
                  color_discrete_map={"Top": "#0F766E", "Other": "lightgray"})
fig_prod.update_layout(showlegend=False)
st.plotly_chart(fig_prod, use_container_width=True)
insight("Products (all data)", "The top 10 products generate 10.8% of sales. Some, like Canon (5 orders) and Cisco (1 order), rank high because of a few large orders.")