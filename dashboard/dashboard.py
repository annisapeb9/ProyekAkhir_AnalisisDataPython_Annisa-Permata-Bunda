import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import streamlit as st
import urllib
from babel.numbers import format_currency
from streamlit_option_menu import option_menu
sns.set(style='darkgrid')

datetime_cols = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
all_df = pd.read_csv("D:\\A SEMESTER 6 CODING CAMP DBS\\Belajar Dasar Analisis Data Dengan Python\\ProyekAkhir_AnalisisDataPython_Annisa Permata Bunda\\dashboard\\all_data.csv")
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

geolocation = pd.read_csv("D:\A SEMESTER 6 CODING CAMP DBS\Belajar Dasar Analisis Data Dengan Python\ProyekAkhir_AnalisisDataPython_Annisa Permata Bunda\data\geolocation_dataset.csv")
data = geolocation.drop_duplicates(subset='geolocation_zip_code_prefix')

for col in datetime_cols:
    all_df[col] = pd.to_datetime(all_df[col])

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

with st.sidebar:
    st.image("D:\A SEMESTER 6 CODING CAMP DBS\Belajar Dasar Analisis Data Dengan Python\ProyekAkhir_AnalisisDataPython_Annisa Permata Bunda\dashboard\gcl.png", width=200)
    selected = option_menu(
        menu_title="E-Commerce Dashboard",
        options=["Overview", "Customer Spend", "Order Items", "Reviews", "Demographics"],
        icons=["shop", "cash", "box", "star", "globe"],
        menu_icon="menu-button-wide",
        default_index=0,
    )
    start_date, end_date = st.date_input("Select Date Range", [min_date, max_date], min_date, max_date)

main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) & (all_df["order_approved_at"] <= str(end_date))]

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_approved_at').agg({"order_id": "nunique", "payment_value": "sum"})
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={"order_id": "order_count", "payment_value": "revenue"}, inplace=True)
    return daily_orders_df

def create_sum_spend_df(df):
    sum_spend_df = df.resample(rule='D', on='order_approved_at').agg({"payment_value": "sum"})
    sum_spend_df = sum_spend_df.reset_index()
    sum_spend_df.rename(columns={"payment_value": "total_spend"}, inplace=True)
    return sum_spend_df

def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name_english")["product_id"].count().reset_index()
    sum_order_items_df.rename(columns={"product_id": "product_count"}, inplace=True)
    sum_order_items_df = sum_order_items_df.sort_values(by='product_count', ascending=False)
    return sum_order_items_df

def review_score_df(df):
    review_scores = df['review_score'].value_counts().sort_values(ascending=False)
    most_common_score = review_scores.idxmax()
    return review_scores, most_common_score

def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={"customer_id": "customer_count"}, inplace=True)
    most_common_state = bystate_df.loc[bystate_df['customer_count'].idxmax(), 'customer_state']
    bystate_df = bystate_df.sort_values(by='customer_count', ascending=False)
    return bystate_df, most_common_state

def create_order_status(df):
    order_status_df = df["order_status"].value_counts().sort_values(ascending=False)
    most_common_status = order_status_df.idxmax()
    return order_status_df, most_common_status

def plot_brazil_map(data):
    brazil = mpimg.imread(urllib.request.urlopen(
        'https://i.pinimg.com/originals/3a/0c/e1/3a0ce18b3c842748c255bc0aa445ad41.jpg'), 'jpg')
    fig, ax = plt.subplots(figsize=(10, 10))  
    data.plot(kind="scatter", x="geolocation_lng", y="geolocation_lat",
              alpha=0.3, s=0.3, c='maroon', ax=ax)  
    ax.axis('off')
    ax.imshow(brazil, extent=[-73.98283055, -33.8, -33.75116944, 5.4])  

    st.pyplot(fig)  

daily_orders_df = create_daily_orders_df(main_df)
sum_spend_df = create_sum_spend_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
review_score, common_score = review_score_df(main_df)
state, most_common_state = create_bystate_df(main_df)
order_status, common_status = create_order_status(main_df)

st.title("📊 E-Commerce Dashboard")
st.markdown("---")

if selected == "Overview":
    st.header("📅 Daily Orders")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total Orders", value=daily_orders_df["order_count"].sum())
    with col2:
        st.metric(label="Total Revenue", value=format_currency(daily_orders_df["revenue"].sum(), "IDR", locale="id_ID"))
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(daily_orders_df["order_approved_at"], daily_orders_df["order_count"], marker="o", linewidth=2, color="#90CAF9")
    st.pyplot(fig)

elif selected == "Customer Spend":
    st.header("💰 Customer Spend Money")
    st.metric(label="Total Spend", value=format_currency(sum_spend_df["total_spend"].sum(), "IDR", locale="id_ID"))
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(sum_spend_df["order_approved_at"], sum_spend_df["total_spend"], marker="o", linewidth=2, color="#90CAF9")
    st.pyplot(fig)

elif selected == "Demographics":
    st.header("🌍 Customer Demographics")
    plot_brazil_map(data)
    st.metric(label="Most Common State", value=most_common_state)

st.caption('📌 Copyright (C) Annisa Permata Bunda')