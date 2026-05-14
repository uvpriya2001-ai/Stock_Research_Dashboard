import pandas as pd
import numpy as np

class FundamentalAnalyzer:
    """Analyzes fundamental metrics from stock info"""
    
    def __init__(self, stock_info):
        self.info = stock_info
    
    def get_pe_ratio(self):
        """Get P/E Ratio"""
        return self.info.get('trailingPE', None)
    
    def get_forward_pe(self):
        """Get Forward P/E Ratio"""
        return self.info.get('forwardPE', None)
    
    def get_pb_ratio(self):
        """Get Price-to-Book Ratio"""
        return self.info.get('priceToBook', None)
    
    def get_ps_ratio(self):
        """Get Price-to-Sales Ratio"""
        return self.info.get('priceToSalesTrailing12Months', None)
    
    def get_peg_ratio(self):
        """Get PEG Ratio (P/E to Growth)"""
        return self.info.get('pegRatio', None)
    
    def get_dividend_yield(self):
        """Get Dividend Yield"""
        div_yield = self.info.get('dividendYield', 0)
        return (div_yield) if div_yield else 0
    
    def get_earnings_growth(self):
        """Get Earnings Growth Rate"""
        return self.info.get('earningsGrowth', 0) * 100 if self.info.get('earningsGrowth') else 0
    
    def get_revenue_growth(self):
        """Get Revenue Growth Rate"""
        return self.info.get('revenueGrowth', 0) * 100 if self.info.get('revenueGrowth') else 0
    
    def get_gross_margins(self):
        """Get Gross Profit Margin"""
        return self.info.get('grossMargins', 0) * 100 if self.info.get('grossMargins') else 0
    
    def get_operating_margins(self):
        """Get Operating Margin"""
        return self.info.get('operatingMargins', 0) * 100 if self.info.get('operatingMargins') else 0
    
    def get_profit_margin(self):
        """Get Net Profit Margin"""
        return self.info.get('profitMargins', 0) * 100 if self.info.get('profitMargins') else 0
    
    def get_roe(self):
        """Get Return on Equity"""
        roe = self.info.get('returnOnEquity', 0)
        return (roe * 100) if roe else 0
    
    def get_roa(self):
        """Get Return on Assets"""
        roa = self.info.get('returnOnAssets', 0)
        return (roa * 100) if roa else 0
    
    def get_debt_to_equity(self):
        """Get Debt to Equity Ratio"""
        return self.info.get('debtToEquity', None)
    
    def get_current_ratio(self):
        """Get Current Ratio (Liquidity)"""
        return self.info.get('currentRatio', None)
    
    def get_quick_ratio(self):
        """Get Quick Ratio"""
        return self.info.get('quickRatio', None)
    
    def get_beta(self, stock_data, market_data):
        """Calculate Beta using covariance method"""

    try:

        stock_close = (
            stock_data['Close']
            .astype(float)
            .to_numpy()
            .flatten()
        )

        market_close = (
            market_data['Close']
            .astype(float)
            .to_numpy()
            .flatten()
        )

        # Ensure equal lengths
        min_len = min(len(stock_close), len(market_close))

        stock_close = stock_close[-min_len:]
        market_close = market_close[-min_len:]

        # Daily returns
        stock_returns = pd.Series(stock_close).pct_change().dropna()

        market_returns = pd.Series(market_close).pct_change().dropna()

        # Covariance matrix
        covariance_matrix = np.cov(
            stock_returns,
            market_returns
        )

        covariance = covariance_matrix[0][1]

        market_variance = np.var(market_returns)

        if market_variance == 0:
            return None

        beta = covariance / market_variance

        return round(beta, 3)

    except Exception as e:
        print(f"Beta calculation error: {e}")
        return None
    
    def get_market_cap(self):
        """Get Market Capitalization"""
        return self.info.get('marketCap', None)
    
    def get_enterprise_value(self):
        """Get Enterprise Value"""
        return self.info.get('enterpriseValue', None)
    
    def get_book_value(self):
        """Get Book Value Per Share"""
        return self.info.get('bookValue', None)
    
    def get_trailing_eps(self):
        """Get Trailing EPS"""
        return self.info.get('trailingEps', None)
    
    def get_forward_eps(self):
        """Get Forward EPS"""
        return self.info.get('forwardEps', None)
    
    def get_52_week_high(self):
        """Get 52-Week High"""
        return self.info.get('fiftyTwoWeekHigh', None)
    
    def get_52_week_low(self):
        """Get 52-Week Low"""
        return self.info.get('fiftyTwoWeekLow', None)
    
    def get_shares_outstanding(self):
        """Get Shares Outstanding"""
        return self.info.get('sharesOutstanding', None)
    
    def get_shares_float(self):
        """Get Float Shares"""
        return self.info.get('floatShares', None)
    
    def get_sector(self):
        """Get Sector"""
        return self.info.get('sector', 'Unknown')
    
    def get_industry(self):
        """Get Industry"""
        return self.info.get('industry', 'Unknown')
    
    def get_free_cash_flow(self):
        """Get Free Cash Flow"""
        return self.info.get('freeCashflow', None)
    
    def get_operating_cash_flow(self):
        """Get Operating Cash Flow"""
        return self.info.get('operatingCashflow', None)
    
    def get_cash_per_share(self):
        """Get Cash Per Share"""
        return self.info.get('cashPerShare', None)
    
    def get_analyst_target_price(self):
        """Get Analyst Target Price"""
        return self.info.get('targetMeanPrice', None)
    
    def get_number_of_analysts(self):
        """Get Number of Analysts"""
        return self.info.get('numberOfAnalysts', None)
    
    def get_recommendation(self):
        """Get Recommendation Rating"""
        return self.info.get('recommendationKey', 'None')
    
    def is_dividend_payer(self):
        """Check if stock pays dividends"""
        return self.info.get('dividendRate', 0) > 0
    
    def get_payout_ratio(self):
        """Get Dividend Payout Ratio"""
        return self.info.get('payoutRatio', 0) * 100 if self.info.get('payoutRatio') else 0
    
    def get_summary_profile(self):
        """Get company summary"""
        return {
            'name': self.info.get('longName', 'N/A'),
            'sector': self.get_sector(),
            'industry': self.get_industry(),
            'description': self.info.get('longBusinessSummary', 'N/A'),
            'website': self.info.get('website', 'N/A'),
            'employees': self.info.get('fullTimeEmployees', 'N/A')
        }