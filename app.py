import streamlit as st
import pandas as pd
import plotly.express as px
from millify import millify
import plotly.figure_factory as ff
import warnings

warnings.filterwarnings('ignore')

# Page setup
st.set_page_config(page_title='E-commerce Dashboard', page_icon=":bar_chart:", layout='wide')
st.title(":bar_chart: E-COMMERCE DASHBOARD")
st.markdown('<style>div.block-container{padding-top :2rem;}</style>', unsafe_allow_html=True)

# File upload
f1 = st.file_uploader(':file_folder: Upload a file', type=['csv', 'txt', 'xlsx', 'xls'])

if f1 is None:
    st.info("Upload a file to continue.")
    st.stop()

# File reading with fallback
try:
    df = pd.read_csv(f1, encoding='ISO-8859-1')
except Exception as e:
    st.error(f"Error reading the file: {e}")
    st.stop()

# Parse date column
if 'Order Date' not in df.columns:
    st.error("The file must contain an 'Order Date' column.")
    st.stop()

df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce', dayfirst=True)
df.dropna(subset=['Order Date'], inplace=True)

# Date range filter
col1, col2 = st.columns(2)
startDate = df['Order Date'].min()
endDate = df['Order Date'].max()

with col1:
    date1 = st.date_input("Start Date", startDate)
with col2:
    date2 = st.date_input("End Date", endDate)

df = df[(df['Order Date'] >= pd.to_datetime(date1)) & (df['Order Date'] <= pd.to_datetime(date2))]

# Sidebar filters
st.sidebar.header("Choose your Filter:")
region = st.sidebar.multiselect("Pick your Region", df['Region'].dropna().unique())
df2 = df[df['Region'].isin(region)] if region else df.copy()

state = st.sidebar.multiselect("Pick your State", df2['State'].dropna().unique())
df3 = df2[df2['State'].isin(state)] if state else df2.copy()

city = st.sidebar.multiselect("Pick your City", df3['City'].dropna().unique())
filtered_df = df3[df3['City'].isin(city)] if city else df3.copy()

# Metrics
metric1, metric2, metric3 = st.columns(3)
with metric1:
    st.metric("Total Quantity", int(filtered_df["Quantity"].sum()))

with metric2:
    total_sales = filtered_df["Sales"].sum()
    st.metric("Gross Revenue", millify(total_sales))

with metric3:
    gross_profit = filtered_df["Profit"].sum()
    st.metric("Gross Profit", millify(gross_profit))

# Category sales bar chart
col1, col2 = st.columns(2)
category_df = filtered_df.groupby("Category", as_index=False)["Sales"].sum()

with col1:
    st.subheader("Category wise Sales")
    fig = px.bar(category_df, x='Category', y='Sales', text_auto='.2s', template="seaborn")
    st.plotly_chart(fig, use_container_width=True)

# Region pie chart
with col2:
    st.subheader("Region wise Sales")
    region_df = filtered_df.groupby("Region", as_index=False)["Sales"].sum()
    fig = px.pie(region_df, values='Sales', names="Region", hole=0.5)
    st.plotly_chart(fig, use_container_width=True)

# Download category and region data
cl1, cl2 = st.columns(2)
with cl1:
    with st.expander("Category View Data"):
        st.dataframe(category_df)
        st.download_button("Download Category CSV", category_df.to_csv(index=False).encode("utf-8"), "Category.csv", "text/csv")

with cl2:
    with st.expander("Region View Data"):
        st.dataframe(region_df)
        st.download_button("Download Region CSV", region_df.to_csv(index=False).encode("utf-8"), "Region.csv", "text/csv")

# Time series line chart
st.subheader("Time Series Analysis")
filtered_df['month_year'] = filtered_df['Order Date'].dt.to_period('M').astype(str)
linechart = filtered_df.groupby("month_year")["Sales"].sum().reset_index()
fig2 = px.line(linechart, x="month_year", y="Sales", labels={"Sales": "Amount"}, template="gridon")
st.plotly_chart(fig2, use_container_width=True)

with st.expander("Time Series View Data"):
    st.dataframe(linechart)
    st.download_button("Download Time Series", linechart.to_csv(index=False).encode("utf-8"), "TimeSeries.csv", "text/csv")

# Treemap
st.subheader("Hierarchical Sales Treemap")
fig3 = px.treemap(filtered_df, path=["Region", "Category", "Sub-Category"], values="Sales", color="Sub-Category")
st.plotly_chart(fig3, use_container_width=True)

# Segment & Category Pie Charts
chart1, chart2 = st.columns(2)

with chart1:
    st.subheader("Segment Wise Sales")
    segment_df = filtered_df.groupby("Segment", as_index=False)["Sales"].sum()
    fig = px.pie(segment_df, values="Sales", names="Segment", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    st.subheader("Category Wise Sales")
    fig = px.pie(category_df, values="Sales", names="Category", template="gridon")
    st.plotly_chart(fig, use_container_width=True)

# Table & pivot summary
st.subheader("Month-wise Sub-Category Sales Summary")
with st.expander("Summary Table"):
    df_sample = df.head(5)[["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]]
    fig_table = ff.create_table(df_sample)
    st.plotly_chart(fig_table, use_container_width=True)

    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    pivot_table = pd.pivot_table(filtered_df, values="Sales", index="Sub-Category", columns="month", aggfunc='sum')
    st.dataframe(pivot_table)

# Scatter plot
for col in ["Sales", "Profit", "Quantity"]:
    filtered_df[col] = pd.to_numeric(filtered_df[col], errors='coerce')

st.subheader("Scatter Plot: Sales vs Profit")
scatter_fig = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity", title="Relationship between Sales and Profit")
st.plotly_chart(scatter_fig, use_container_width=True)

# View and download filtered data
with st.expander("View Filtered Data"):
    st.dataframe(filtered_df.head(50))

csv = df.to_csv(index=False).encode("utf-8")
st.download_button("Download Original Dataset", data=csv, file_name="Data.csv", mime="text/csv")





#SHARING DOWNLOADED DATA 
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import streamlit as st

# Email sending function
def send_email(to_email, subject, body, file_path=None):
    sender_email = "okyerevansjohn@gmail.com"  # Replace with your email
    sender_password = "rmjb pmyh kght kkmq"  # Replace with your email's app password (not your regular password)

    try:
        # Setting up the SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)

        # Creating the email
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Adding attachment
        if file_path:
            try:
                attachment = open(file_path, "rb")
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={file_path.split('/')[-1]}",
                )
                msg.attach(part)
                attachment.close()
            except Exception as e:
                return f"An error occurred while attaching the file: {str(e)}"

        # Send the email
        server.sendmail(sender_email, to_email, msg.as_string())
        server.close()

        return "Email sent successfully!"
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Email form in Streamlit
st.subheader("📧 Share this Dashboard via Email")
with st.form(key="email_form"):
    to_email = st.text_input("Recipient Email Address", placeholder="Enter email address")
    email_subject = st.text_input("Email Subject", value="")
    email_body = st.text_area("Email Message", value="")
    file_upload = st.file_uploader("Attach File", type=["py", "csv", "txt", "xlsx", "pdf"])  # Limit types as needed
    send_email_button = st.form_submit_button("Send Email")

    if send_email_button:
        if to_email and email_subject and email_body:
            # Save the uploaded file temporarily
            if file_upload:
                file_path = f"./{file_upload.name}"
                with open(file_path, "wb") as f:
                    f.write(file_upload.read())
            else:
                file_path = None

            response = send_email(to_email, email_subject, email_body, file_path)

            # Cleanup temporary file
            if file_upload:
                import os
                os.remove(file_path)

            st.success(response)
        else:
            st.error("Please fill out all fields before sending the email.")
