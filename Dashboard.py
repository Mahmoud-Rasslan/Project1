
## Import the required Library:
import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import pyxlsb as pl
st.set_page_config(layout='wide')

# ******************************************************************************************************************************************************

## Import and prepare the data frame:
df = pd.read_excel("Data For Mid-Project.xlsb" , engine='pyxlsb')

# ******************************************************************************************************************************************************

## Create the needed Column:

# Create the States Column
df['State'] = df['Region'].apply(lambda x: 'Northern Egypt' if x in ['ALEXANDRIA' , 'DELTA'] else x)
df['State'] = df['State'].apply(lambda x: 'Mid of Egypt' if x in ['CAIRO' , 'CANAL', 'GUIZA'] else x)
# Create the Business_Type Column
df['Business_Type'] = df['Sector'].apply(lambda x: 'Governmental' if x in ['ED / TREAT / UNIV','MOH / NHO'] else 'Private')
# Create the Business_Type Column
df['Sales_Type'] = df['Sector'].apply(lambda x: 'Retail Sales' if x == 'PHARMACIES*' else 'Bulk Sales' if x == 'STORES' else 'Institution Sales')
# Create the product type when the 2 column are matched
df['Product_Type'] = df['Corporation'] == df['Manufacturer']
df['Product_Type'] = df['Product_Type'].apply(lambda x: 'In House' if x == True else 'Toll')
# Create Form Column from the NFC1 column using String Method extract
df['Form'] = df['NFC1'].str.extract(r'(?<=\s)(\S+)(?=\s|$)')
# Craete Price Column using the Value and Units Column
df['Price'] = (df['Value'] / df['Units']).round(1)
# Convert Year column into object column
df['Year'] = df['Year'].apply(lambda x: str(x) if type(x) == int else x)
# Drop unused column:
df = df.drop(columns=['NFC1', 'NFC2', 'NFC3'])

# ******************************************************************************************************************************************************

# Dashboard Tiltle
st.markdown(
    """
    <h1 style="color:blue; font-weight:italic; text-decoration:underline; text-align : center;">
        Egyptian Pharmaceutical Market
    </h1>
    """,
    unsafe_allow_html=True)

# ******************************************************************************************************************************************************

## Create the sidebar

# Aggregation method
Aggreg = st.sidebar.selectbox('Select Aggregation method' , options=['SUM' , 'AVG'] , index=0)
Aggreg_method = 'sum' if Aggreg == 'SUM' else 'avg'

# For Chart Titles:
Aggregate = 'Total' if Aggreg == 'SUM' else 'Average'

# Measurement Seletion:
Third_Option = 'Price' if Aggreg == 'AVG' else ''
measure = st.sidebar.radio('Select Measure' , options=['EGP' , 'PACK' , Third_Option])

# Store the Output in Varible to be used in the fig below.
val_Col = 'Value' if measure == 'EGP' else 'Price' if measure == 'Price' else 'Units'

# Select Year
Year = st.sidebar.selectbox('Select Year', options=['ALL'] + df['Year'].unique().tolist(), index=0)

# Selcet the Top N:
N = st.sidebar.number_input('Top' , min_value=5 , max_value=100 , value=10 ,  step=1)


# Product Type Filter
product_type = st.sidebar.selectbox('Select Product Type', options=['ALL'] + df['Product_Type'].unique().tolist(), index=0)

# Sales Type Filter
sales_type = st.sidebar.selectbox('Select Sales Type', options=['ALL'] + df['Sales_Type'].unique().tolist(), index=0)

# Business Type Filter
business_type = st.sidebar.selectbox('Select Business Type', options=['ALL'] + df['Business_Type'].unique().tolist(), index=0)

# State Filter
state = st.sidebar.selectbox('Select State', options=['ALL'] + df['State'].unique().tolist(), index=0)

# Corporation Filter
corpor = st.sidebar.selectbox('Select Company', options=['ALL'] + df['Corporation'].unique().tolist(), index=0)

# ******************************************************************************************************************************************************

## Creating the MSKs

# Product Type Filter enable:
pr_ty_filter = df['Product_Type'].unique().tolist() if product_type == 'ALL' else [product_type]

# Apply Product Type Filter
sub_df1 = df[df['Product_Type'].isin(pr_ty_filter)]

# Sales Type Filter enable:
sa_ty_filter = sub_df1['Sales_Type'].unique().tolist() if sales_type == 'ALL' else [sales_type]

# Apply Sales Type Filter
sub_df2 = sub_df1[sub_df1['Sales_Type'].isin(sa_ty_filter)]

# Business Type Filter enable:
bu_ty_filter = sub_df2['Business_Type'].unique().tolist() if business_type == 'ALL' else [business_type]

# Apply Business Type Filter
sub_df3 = sub_df2[sub_df2['Business_Type'].isin(bu_ty_filter)]

# State Filter enable:
state_filter = sub_df3['State'].unique().tolist() if state == 'ALL' else [state]

# Apply State Filter
sub_df4 = sub_df3[sub_df3['State'].isin(state_filter)]

# Corporation Filter enable:
corpor_filter = sub_df4['Corporation'].unique().tolist() if corpor == 'ALL'  else [corpor]

# Apply Corporation Filter
sub_df5 = sub_df4[sub_df4['Corporation'].isin(corpor_filter)]

# Year Filter enable:
y_filter = sub_df5['Year'].unique().tolist() if Year == 'ALL' else [Year]

# Apply Year Filter
sub_df6 = sub_df5[sub_df5['Year'].isin(y_filter)]

# ******************************************************************************************************************************************************

##Function to convert Numbers:
def format_number(num):
    if num >= 1_000_000_000: 
        return f"{num / 1_000_000_000:.2f}B"
    elif num >= 1_000_000:  
        return f"{num / 1_000_000:.2f}M"
    elif num >= 1_000:  
        return f"{num / 1_000:.2f}K"
    else: 
        return f"{num:.2f}"

# ******************************************************************************************************************************************************

## Cards Data Calculator
fur1 = format_number(sub_df6['Units'].sum().round(0) if Aggreg == 'SUM' else sub_df6['Units'].mean().round(0))
fur2 = format_number(sub_df6['Value'].sum().round(0) if Aggreg == 'SUM' else sub_df6['Value'].mean().round(0))
fur3 = format_number(sub_df6['Product'].nunique())

# ******************************************************************************************************************************************************

## Creating the Columns:


col1 , col2, col3 = st.columns(3)

with col1:
#No. of Products Card
    st.markdown(
    f"""
    <div style="
        border: 2px solid #4CAF50;
        border-radius: 5px;
        padding: 5px;
        text-align: center;
        width: 180px;
        background-color: #f9f9f9;">
        <h5 style="margin: 0; color: #0000FF;">Product No.</h5>
        <p style="font-size: 25px; margin: 0; font-weight: bold;">{fur3}</p>
        <p style="margin: 0; color: gray;">Product</p>
    </div>
    """,
    unsafe_allow_html=True)

# ******************************************************************************************************************************************************

# Sector Pie Chart
    aggregated_df1 = sub_df6.groupby('Sector', as_index=False)[val_Col].sum() if Aggreg == 'SUM' else sub_df6.groupby('Sector', as_index=False)[val_Col].mean()
    fig1 = px.pie(data_frame=aggregated_df1 , names= 'Sector' , values= val_Col , title= f'{Aggregate} Sales {val_Col} per Sector', width= 500 , height= 500)
# Update the legend position
    fig1.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
# Display the chart in Streamlit
    st.plotly_chart(fig1)

# ******************************************************************************************************************************************************
    
#(# Annual Sales Trend
    #fig = px.histogram(data_frame=sub_df5 , x= 'Year' , y= val_Col , text_auto= True , histfunc= Aggreg_method , title= f'{Aggregate} Sales {val_Col} Yearly Trend')
# add space between the columns in the figure
   # fig.update_layout(bargap=0.2)
# Display the chart in Streamlit
  #  st.plotly_chart(fig))


    sub_df5['Year'] = sub_df5['Year'].astype(str)
    aggregated_df8 = sub_df5.groupby('Year', as_index=False)[val_Col].sum() if Aggreg == 'SUM' else sub_df5.groupby('Year', as_index=False)[val_Col].mean()
# Annual Sales Trend as Line Chart
    fig = px.line(data_frame=aggregated_df8, x='Year', y=val_Col, title=f'{Aggregate} Sales {val_Col} Yearly Trend', markers=True)

# Customize the layout
    fig.update_layout( title={'x': 0}, xaxis_title="Year", yaxis_title=val_Col)

# Display the chart in Streamlit
    st.plotly_chart(fig)


# ******************************************************************************************************************************************************

with col2:
#Units Card
    st.markdown(
    f"""
    <div style="
        border: 2px solid #4CAF50;
        border-radius: 5px;
        padding: 5px;
        text-align: center;
        width: 180px;
        background-color: #f9f9f9;">
        <h5 style="margin: 0; color: #0000FF;">{Aggregate} Units</h5>
        <p style="font-size: 25px; margin: 0; font-weight: bold;">{fur1}</p>
        <p style="margin: 0; color: gray;">Packs</p>
    </div>
    """,
    unsafe_allow_html=True)

# ******************************************************************************************************************************************************

# Region Pie Chart
    aggregated_df2 = sub_df6.groupby('Region', as_index=False)[val_Col].sum() if Aggreg == 'SUM' else sub_df6.groupby('Region', as_index=False)[val_Col].mean()
    fig2 = px.pie(data_frame=aggregated_df2 , names= 'Region' , values= val_Col , title= f'{Aggregate} Sales {val_Col} per Region', width= 500 , height= 500)
# Update the legend position
    fig2.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
# Display the chart in Streamlit
    st.plotly_chart(fig2)
    
# ******************************************************************************************************************************************************
# Top 10 Companies 
    Top_10_Cor_V = sub_df6.groupby(['Corporation'])[val_Col].sum().sort_values(ascending=False).head(N).reset_index() if Aggreg == 'SUM' else sub_df6.groupby(['Corporation'])[val_Col].mean().sort_values(ascending=False).head(10).reset_index()
    fig5 = px.histogram(data_frame=Top_10_Cor_V , x= val_Col , y= 'Corporation' , text_auto= True , title= f'Top {N} Companies ({Aggregate} {val_Col})', height= 500)  
# Sort the companies Descending
    fig5.update_yaxes(categoryorder='total ascending')
# Display the chart in Streamlit
    st.plotly_chart(fig5)

# ******************************************************************************************************************************************************    

with col3:
#Value Card
    st.markdown(
    f"""
    <div style="
        border: 2px solid #4CAF50;
        border-radius: 5px;
        padding: 5px;
        text-align: center;
        width: 180px;
        background-color: #f9f9f9;">
        <h5 style="margin: 0; color: #0000FF;">{Aggregate} Values</h5>
        <p style="font-size: 25px; margin: 0; font-weight: bold;">{fur2}</p>
        <p style="margin: 0; color: gray;">EGP</p>
    </div>
    """,
    unsafe_allow_html=True)
    
# ******************************************************************************************************************************************************

# Form Pie Chart
    aggregated_df3 = sub_df6.groupby('Form', as_index=False)[val_Col].sum() if Aggreg == 'SUM' else sub_df6.groupby('Form', as_index=False)[val_Col].mean()
    fig3 = px.pie(data_frame=aggregated_df3 , names= 'Form' , values= val_Col , title= f'{Aggregate} Sales {val_Col} per Form', width= 500 , height= 500)
# Update the legend position
    fig3.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5))
# Display the chart in Streamlit
    st.plotly_chart(fig3)

# ******************************************************************************************************************************************************

# Top 10 Products 
    Top_10_pro = sub_df6.groupby(['Product'])[val_Col].sum().sort_values(ascending=False).head(N).reset_index() if Aggreg == 'SUM' else sub_df6.groupby(['Product'])[val_Col].mean().sort_values(ascending=False).head(10).reset_index()
    fig6 = px.histogram(data_frame=Top_10_pro , x= 'Product'  , y= val_Col , text_auto= True , title= f'Top {N} Products ({Aggregate} {val_Col})', height= 500)  
# Sort the companies Descending
    fig6.update_yaxes(categoryorder='total ascending')
# Display the chart in Streamlit
    st.plotly_chart(fig6)

# ******************************************************************************************************************************************************
    
# ATC1 Bar Chart
fig4 = px.histogram(data_frame=sub_df6 , x= val_Col , y= 'ATC1' , text_auto= True , histfunc= Aggreg_method , title= f'{Aggregate} Sales {val_Col} per ATC1', height= 500, width=1000)
# Sort the ATC Descending 
fig4.update_yaxes(categoryorder='total ascending')
# Display the chart in Streamlit
st.plotly_chart(fig4, use_container_width=True)

