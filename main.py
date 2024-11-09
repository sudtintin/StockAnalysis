
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px 
import streamlit as st 
import yfinance as yf
import datetime as datetime



st.set_page_config(
    page_title="Anbu-Sudhakar Analysis",
    page_icon=":beetle:",
    layout="wide",
)

#Side Bar

currentDate= datetime.date.today()
beforeOneMonth = datetime.date(currentDate.year, currentDate.month - 2, 1)

ticker = st.sidebar.text_input('Ticker','AAPL')
startDt = st.sidebar.date_input('Start Date',beforeOneMonth)
endDt= st.sidebar.date_input('End Date')
daysBetween = endDt-startDt

st.sidebar.title(" Stock Dashboard")

st.title(ticker + " Stock Dashboard")


#periodList = ['','Minutes','Hours','Days','Quartly','Half Yearly','YEarly']
#periodListSelected = st.sidebar.selectbox("Select your Period ", periodList)

tickerData = yf.Ticker(ticker) 

# Download historical price data for a specific stock
data = yf.download(ticker,start=startDt,end=endDt,rounding=True) 
priceData , fundamentalData , Analysis , News = st.tabs(["Pricing", "Fundamental","Analysis","News"])

st.session_state['ticker'] = ticker
st.session_state['tickerData'] = tickerData
st.session_state['startDt'] = startDt
st.session_state['endDt'] = endDt


with priceData:
    st.header("Price Movement")
    
    data2=data
    data2['Change'] = data["Adj Close"] / data["Adj Close"].shift(1)  - 1
    data2.dropna(inplace=True)
    st.write(data2)
    annualReturn = data2['Change'].mean()*daysBetween.days*100
    st.write(daysBetween," Return is : ", annualReturn,'%')

with fundamentalData:
    balanceSheetTab , incomeStatementTab , cashFlowTab ,Earnings , Dividend, Calendar,major_holders,institutional_holders = st.tabs(["Balance Sheet", "Income Statement","Cash Flow","Earnings","Dividend","Calendar","major_holders","institutional_holders"])
    with balanceSheetTab:
        balanceSheet = tickerData.quarterly_balance_sheet
        col1,col2 =st.columns(2)

        with col1:
            st.write("Quartly")
            st.write(balanceSheet) 

        with col2:
            balanceSheet = tickerData.balance_sheet
            st.write("Annually")
            st.write(balanceSheet)    

    with incomeStatementTab:
        incomeStatement = tickerData.quarterly_financials

        col1,col2 =st.columns(2)

        with col1:
            st.write("Quartly")
            st.write(incomeStatement)  

        with col2:
            incomeStatement = tickerData.financials
            st.write("Annually")        
            st.write(incomeStatement)  

    with cashFlowTab:
        cashFlow = tickerData.quarterly_cashflow

        col1,col2 =st.columns(2)

        with col1:        
            st.write("Quartly") 
            st.write(cashFlow)          

        with col2:
            cashFlow = tickerData.cashflow
            st.write("Annually") 
            st.write(cashFlow)          

        with Dividend:

            col1,col2 =st.columns(2)

            with col1: 
                dividend = tickerData.dividends
                st.write("Dividend")
                st.write(dividend)

            with col2:
                action = tickerData.actions
                st.write("Split")
                st.write(action)

    with Earnings:
        earnings = tickerData.earnings
        st.write("Earnings")
        st.write(earnings)


    with Calendar:
        calendar = tickerData.calendar
        st.write("Calendar")
        st.write(calendar)
        
    with major_holders:
        major_holders = tickerData.major_holders
        st.write("major_holders")
        st.write(major_holders)
        
    with institutional_holders:
        institutional_holders = tickerData.institutional_holders
        st.write("institutional_holders")
        st.write(institutional_holders)

with Analysis:
    
    DuPontAnalysis , ZScore , HeatMap = st.tabs(["DuPontAnalysis", "Z-Score","Heat Map"])

    with DuPontAnalysis:
        # Fetch financial data from yfinance
        def fetch_financial_data(ticker):
            stock = tickerData
            
            # Fundamental data
            financials = stock.financials
            balance_sheet = stock.balance_sheet
            
            # Get latest available values
            try:
                revenue = financials.loc['Total Revenue'].iloc[0]
                net_income = financials.loc['Net Income'].iloc[0]
                total_assets = balance_sheet.loc['Total Assets'].iloc[0]
                total_equity = balance_sheet.loc['Stockholders Equity'].iloc[0]
            except KeyError as e:
                print(f"Data missing for {ticker}: {e}")
                return None

            return {
                'Revenue': revenue,
                'Net Income': net_income,
                'Total Assets': total_assets,
                'Total Equity': total_equity
            }

        # Perform DuPont ROE calculation
        def calculate_dupont_roe(financials):
            if not financials:
                return None

            # DuPont ROE Components
            revenue = financials['Revenue']
            net_income = financials['Net Income']
            total_assets = financials['Total Assets']
            total_equity = financials['Total Equity']

            # Calculate DuPont components
            net_profit_margin = net_income / revenue
            asset_turnover = revenue / total_assets
            equity_multiplier = total_assets / total_equity
            
            # Calculate ROE using DuPont formula
            roe = net_profit_margin * asset_turnover * equity_multiplier
            return {
                'Net Profit Margin': net_profit_margin,
                'Asset Turnover': asset_turnover,
                'Equity Multiplier': equity_multiplier,
                'ROE': roe
            }

        # Collect and calculate ROE for each company
        results = {}
        companies="1"
        for company in companies:
            financials = fetch_financial_data(company)
            dupont_roe = calculate_dupont_roe(financials)
            if dupont_roe:
                results[company] = dupont_roe

        # Create a DataFrame for easy comparison and ranking
        df = pd.DataFrame(results).T
        df = df.sort_values(by='ROE', ascending=False)

        # Display the ranking and detailed DuPont analysis
        st.write("DuPont ROE Analysis and Ranking:")
        st.write(df)
        # df.to_csv("DuPontAnalysis.csv")
    with ZScore:
  
        # Function to calculate the Z-Score for stock prices
        def z_score(chunk):
            return (chunk[-1] - chunk.mean()) / chunk.std()

        rolled_zscore = data.Close.rolling(window=30).apply(z_score)
        # rolled_zscore.to_csv ('TATA_Rolled_ZScore.csv')


        rolled_zscore.plot()

        fig =plt.gcf()  
        
        plt.figure(figsize=(1,1))
        st.pyplot(fig)

        # rolled_zscore.hist(bins=20)
        # plt.show()

        # rolled.min()
        # print(rolled.min)
    with HeatMap:

        def calculate_monthly_returns(stock_data):
            """Calculate monthly returns from daily stock data."""
            monthly_data = stock_data.resample('ME').last()  # Use last close price of each month
            monthly_returns = monthly_data.pct_change().dropna()  # Calculate percentage change
            return monthly_returns

        def plot_monthly_returns_heatmap(monthly_returns, symbol):
            """Plot a heatmap of monthly returns."""
            # Convert index to a DataFrame with 'Year' and 'Month' columns for pivot table
            returns_df = monthly_returns
            returns_df['Returns'] = monthly_returns
            returns_df['Year'] = returns_df.index.year
            returns_df['Month'] = returns_df.index.month
            
            # Pivot data for heatmap
            heatmap_data = returns_df.pivot(index="Year", columns="Month", values="Returns")
            
            # Plot heatmap
            plt.figure(figsize=(12, 10))
            sns.heatmap(heatmap_data, annot=True, fmt=".2%", cmap="RdYlGn", cbar_kws={'label': 'Monthly Return'}, linewidths=1.5, linecolor='black')
            plt.title(f"Monthly Returns Heatmap for {symbol}")
            plt.xlabel("Month")
            plt.ylabel("Year")
            plt.xticks(ticks=np.arange(12)+0.5, labels=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], rotation=45)
            plt.yticks(rotation=0)
            

            fig = plt.plot()
            st.pyplot(fig)

        stock_data = data['Close']
        monthly_returns = calculate_monthly_returns(stock_data)
        plot_monthly_returns_heatmap(monthly_returns, ticker)
