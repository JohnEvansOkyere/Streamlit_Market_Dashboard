import streamlit as st
import plotly.express as px
import pandas as pd
from millify import millify
import os
import warnings
warnings.filterwarnings('ignore')

#Page set up
st.set_page_config(page_title='SAMPLE', page_icon=":bar_chart:", layout='wide')

#Title
st.title(":bar_chart: SAMPLE DASHBOARD")
st.markdown('<style>div.block-container{padding-top :2rem;}</style>', unsafe_allow_html=True) #TITLE SPACING


#DOWNLOADING NEW DATA SET
f1 = st.file_uploader(':file_folder: Upload a file', type=['csv','txt','xlsx', 'xls'])  

#Check if file is not empty
if f1 is not None:
    filename = f1.name
    st.write(filename)

    df = pd.read_csv(f1, encoding="ISO-8859-1")
else:
    st.info(":top: Upload a file!")
    st.stop()
    df = pd.read_csv( )

col1, col2 = st.columns((2))
df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)

#Getting Min and Max Date 
startDate = pd.to_datetime(df['Order Date']).min()
endDate = pd.to_datetime(df['Order Date']).max()

#Setting up date columns
with col1:
    date1 = pd.to_datetime(st.date_input('startDate', startDate))

with col2:
    date2 = pd.to_datetime(st.date_input('endDate', endDate))

df = df[(df['Order Date'] >= date1) & (df['Order Date'] <=date2)].copy()


#Creating a Filter Side Bar

#SIDE BAR FOR REGION
st.sidebar.header("Choose your Filter: ")
region = st.sidebar.multiselect("Pick your Region", df['Region'].unique())

if not region:
    df2 = df.copy()
else:
    df2 = df[df['Region'].isin(region)]


#SIDEBAR FOR STATE
state = st.sidebar.multiselect("Pick your State", df2['State'].unique())

if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2['State'].isin(state)]


#SIDEBAR FOR CITY
city = st.sidebar.multiselect("Pick your City", df3['City'].unique())


#Filter the data base on Region, State and City
if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df['Region'].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df = df3[df["State"].isin(state) & df3["City"].isin(city)]
elif region and city:
    filtered_df = df3[df["Region"].isin(region) & df3["City"].isin(city)]
elif region and state:
    filtered_df = df3[df['Region'].isin(region) & df3["State"].isin(state)]
elif city:
    filtered_df = df3[df3['City'].isin(city)]
else:
    filtered_df = df3[df3['Region'].isin(region) & df3['State'].isin(state) & df3["City"].isin(city)]


#CALCULATING FOR THE METRICS DATA


metric1,metric2, metric3 = st.columns((3))
with metric1:
    st.subheader("Total Quantity")
    total_quatity = filtered_df["Quantity"].sum()
    st.metric(label="Total Quantity", value=total_quatity,delta_color="normal",help="This is the total Sales", label_visibility="visible" )


with metric2:
    st.subheader(":dollar: Gross Revenue")
    total_sales = filtered_df["Sales"].sum()
    formatted_sales = millify(total_sales)
    st.metric(label="Gross Revenue", value=formatted_sales,delta_color="normal",help="This is the total Sales", label_visibility="visible" )

with metric3:
    st.subheader(":smile: Gross Profit")
    total_sales = filtered_df["Profit"].sum()
    formatted_sales = millify(total_sales)
    st.metric(label="Gross Profit", value=formatted_sales,delta_color="normal",help="This is the total Sales", label_visibility="visible" )



#CREATING A PLOT FOR CATEGORICAL DATA
category_df = filtered_df.groupby(by = ["Category"], as_index = False)['Sales'].sum()

with col1:
    st.subheader("Category wise Sales")
    fig = px.bar(category_df, x='Category', y='Sales', text=["Ghs{:,.2f}".format(x) for x in category_df['Sales']], template="seaborn")
    st.plotly_chart(fig,use_container_width=True, height=200)

#CREATING A PLOT FOR REGION
with col2:
    st.subheader(":earth_americas: Region wise Sales")
    fig = px.pie(filtered_df, values='Sales', names="Region", hole= 0.5)
    fig.update_traces(text = filtered_df["Region"], textposition = "outside")
    st.plotly_chart(fig, use_container_width=True)

#CREATING AND DOWNLOADING THE FILTERED DATA
#DOWNLOAD FILTERED DATA FOR CATEGORY SALES
# Category Sales
cl1, cl2 = st.columns((2))

with cl1:
    with st.expander("Category_ViewData"):
        if not category_df.empty:
            st.write(category_df.style.background_gradient(cmap="Blues"))
            csv = category_df.to_csv(index=False).encode("utf-8")
            st.download_button("Download Data", data=csv, file_name="Category.csv", mime="text/csv", help="Click here to download the data as CSV file")
        else:
            st.write("No data available to download for Category.")

# Region Sales
with cl2:
    with st.expander("Region_ViewData"):
        region = filtered_df.groupby(by='Region', as_index=False)['Sales'].sum()
        if not region.empty:
            st.write(region.style.background_gradient(cmap="Oranges"))
            csv = region.to_csv(index=False).encode("utf-8")
            st.download_button("Download Data", data=csv, file_name="Region.csv", mime="text/csv", help="Click here to download the data as CSV file")
        else:
            st.write("No data available to download for Region.")


#FILTERED USING TIME SERIES
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader('Time Series Analysis')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x="month_year", y="Sales", labels={"Sales": "Amount"}, height=500, width=1000, template="gridon")
st.plotly_chart(fig2, use_container_width=True)

#DOWNLOAD TIME SERIES DATA
with st.expander("Time Series ViewData"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button("Download Data", data=csv, file_name="TimeSeries.csv", mime="text/csv", help="Click here to download the data as csv file")

#CREATE A TREE MAP BASE ON REGION, CATEGORY AND SUB-CATEGORY
st.subheader("Hierachical view of Sales using Treemap")
fig3 = px.treemap(filtered_df, path=["Region", "Category", "Sub-Category"], values="Sales", hover_data=["Sales"], color = "Sub-Category")
fig3.update_layout(width = 800, height=650)
st.plotly_chart(fig3, use_container_width=True)

#SEGMENT WISE AND CATEGORY BY SALES

#SEGMENT WISE
chart1, chart2 = st.columns((2))
with chart1:
    st.subheader("Segment Wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Segment", template="plotly_dark")
    fig.update_traces(text = filtered_df["Category"], textposition= "inside")
    st.plotly_chart(fig,use_container_width=True)

#CATEGORY WISE
with chart2:
    st.subheader("Category Wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Category", template="gridon")
    fig.update_traces(text = filtered_df["Category"], textposition= "inside")
    st.plotly_chart(fig,use_container_width=True)

#CREATING TABLES
import plotly.figure_factory as ff
st.subheader(":point_right: Month wise Sub-Category Sales Summary")
with st.expander("Summary_Table"):
    df_sample = df[0:5][["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]]
    fig = ff.create_table(df_sample, colorscale="cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month wise Sub-Category Table")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_year = pd.pivot_table(data=filtered_df, values="Sales", index=["Sub-Category"], columns="month")
    st.write(sub_category_year.style.background_gradient(cmap="Blues"))

    # #CREATING SCATTER PLOT

for col in filtered_df.columns:
    if filtered_df[col].dtype == 'object':
        try:
            filtered_df[col] = pd.to_numeric(filtered_df[col], errors='coerce')
        except Exception:
            pass

# Create the scatter plot
data1 = px.scatter(
    filtered_df,
    x="Sales",
    y="Profit",
    size="Quantity",
    title="Relationship between Sales and Profit using Scatter Plot"
)

# Update layout for better visuals
data1.update_layout(
    title=dict(font=dict(size=20)),
    xaxis=dict(title="Sales", titlefont=dict(size=20)),
    yaxis=dict(title="Profit", titlefont=dict(size=20))
)

# Display the scatter plot
st.plotly_chart(data1, use_container_width=True)


#DOWNLOADING SOME TOP ROWS, eg. TOP 5 ROWS
with st.expander("View Data"):
    st.write(filtered_df.iloc[:50,1:20:2].style.background_gradient(cmap="Oranges"))

#DOWNLOADING THE ORIGINAL DATASET
csv = df.to_csv(index = False).encode("utf-8")
st.download_button("Download Original Dataset", data=csv, file_name="Data.csv", mime='text/csv')






# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart

# # Email sending function
# def send_email(to_email, subject, body):
#     sender_email = "okyerevansjohn@gmail.com"  # Replace with your email
#     sender_password = "rmjb pmyh kght kkmq"     # Replace with your email's app password (not your regular password)

#     try:
#         # Setting up the SMTP server
#         server = smtplib.SMTP("smtp.gmail.com", 587)
#         server.starttls()
#         server.login(sender_email, sender_password)

#         # Creating the email
#         msg = MIMEMultipart()
#         msg["From"] = sender_email
#         msg["To"] = to_email
#         msg["Subject"] = subject
#         msg.attach(MIMEText(body, "plain"))

#         # Send the email
#         server.sendmail(sender_email, to_email, msg.as_string())
#         server.close()

#         return "Email sent successfully!"
#     except Exception as e:
#         return f"An error occurred: {str(e)}"

# # Email form in Streamlit
# st.subheader("📧 Share this Dashboard via Email")
# with st.form(key="email_form"):
#     to_email = st.text_input("Recipient Email Address", placeholder="Enter email address")
#     email_subject = st.text_input("Email Subject", value="Check out this awesome dashboard!")
#     email_body = st.text_area("Email Message", value="Hi there! I thought you might find this dashboard interesting.")
#     send_email_button = st.form_submit_button("Send Email")

#     if send_email_button:
#         if to_email and email_subject and email_body:
#             response = send_email(to_email, email_subject, email_body)
#             st.success(response)
#         else:
#             st.error("Please fill out all fields before sending the email.")


#SHARING DOWNLOADED DATA WITH CO-WORKERS OR FRIENDS
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
