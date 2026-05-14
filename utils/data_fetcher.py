import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class DataFetcher:
    """Fetches stock data from yfinance"""
    
    def __init__(self, ticker, period="2y"):
        self.ticker = ticker
        self.period = period
        self.stock = yf.Ticker(ticker)
    
    def get_price_data(self):
        """Fetch stock + market benchmark data"""

        try:

        # STOCK DATA
        stock_data = yf.download(
            self.ticker,
            period=self.period,
            progress=False,
            auto_adjust=True
        )

        # NIFTY 50 DATA
        market_data = yf.download(
            "^NSEI",
            period=self.period,
            progress=False,
            auto_adjust=True
        )

        if stock_data is None or stock_data.empty:
            return None

        if market_data is None or market_data.empty:
            return None

        # Flatten MultiIndex columns
        if isinstance(stock_data.columns, pd.MultiIndex):
            stock_data.columns = stock_data.columns.get_level_values(0)

        if isinstance(market_data.columns, pd.MultiIndex):
            market_data.columns = market_data.columns.get_level_values(0)

        return {
            "stock_data": stock_data,
            "market_data": market_data
        }

    except Exception as e:
        print(f"Error fetching price data: {e}")
        return None
    
    def get_stock_info(self):
        """Fetch fundamental and financial data"""
        try:
            info = self.stock.info
            return info
        except Exception as e:
            print(f"Error fetching stock info: {e}")
            return {}
    
    def get_earnings_dates(self):
        """Fetch earnings report dates"""
        try:
            earnings = self.stock.quarterly_financials
            return earnings
        except Exception as e:
            print(f"Error fetching earnings: {e}")
            return None
    
    def get_historical_pe(self, lookback_years=5):
        """Calculate historical average P/E ratio"""
        try:
            # Get historical quarterly earnings
            financials = self.stock.quarterly_financials
            if financials is None or financials.empty:
                return None
            
            # Get quarterly prices
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_years*365)
            price_data = yf.download(self.ticker, start=start_date, end=end_date, progress=False)
            
            if price_data is None or price_data.empty:
                return None
            
            # Calculate average quarterly PE (simplified)
            try:
                net_income = financials.loc['Net Income']
                shares_outstanding = self.stock.info.get('sharesOutstanding', 1)
                
                eps = net_income / shares_outstanding
                quarterly_prices = price_data['Close'].resample('Q').last()
                
                pe_ratios = quarterly_prices / eps
                return pe_ratios.mean()
            except:
                return None
        
        except Exception as e:
            print(f"Error calculating historical PE: {e}")
            return None
    
    def get_sector_info(self):
        """Get sector and industry information"""
        try:
            sector = self.stock.info.get('sector', 'Unknown')
            industry = self.stock.info.get('industry', 'Unknown')
            return {'sector': sector, 'industry': industry}
        except Exception as e:
            print(f"Error fetching sector info: {e}")
            return {'sector': 'Unknown', 'industry': 'Unknown'}
    
    def get_quarterly_financials(self):
        """Fetch quarterly financial statements"""
        try:
            return self.stock.quarterly_financials
        except Exception as e:
            print(f"Error fetching quarterly financials: {e}")
            return None
    
    def get_dividend_history(self):
        """Fetch dividend history"""
        try:
            return self.stock.dividends
        except Exception as e:
            print(f"Error fetching dividend history: {e}")
            return None
