import pandas as pd
import numpy as np
from utils.data_fetcher import DataFetcher

class ValuationAnalyzer:
    """Analyzes stock valuation relative to sector and historical averages"""
    
    def __init__(self, stock_info, fundamental_analyzer):
        self.info = stock_info
        self.fundamental = fundamental_analyzer
        self.sector = stock_info.get('sector', 'Unknown')
        self.industry = stock_info.get('industry', 'Unknown')
    
    def get_current_pe(self):
        """Get current P/E ratio"""
        pe = self.fundamental.get_pe_ratio()
        return pe if pe else 0
    
    def get_sector_average_pe(self):
        """
        Get average sector P/E ratio
        Note: This is a simplified approach. In production, you'd fetch this from a data source
        """
        sector_pe_dict = {
            'Technology': 25.0,
            'Healthcare': 20.0,
            'Financials': 12.0,
            'Industrials': 15.0,
            'Consumer Discretionary': 18.0,
            'Consumer Staples': 22.0,
            'Energy': 10.0,
            'Materials': 14.0,
            'Utilities': 16.0,
            'Real Estate': 18.0,
            'Communication Services': 21.0
        }
        return sector_pe_dict.get(self.sector, 18.0)
    
    def get_historical_average_pe(self):
        """Get historical average P/E ratio (simplified)"""
        # In production, calculate from historical data
        # For now, use a reasonable estimate
        current_pe = self.get_current_pe()
        if current_pe > 0:
            # Assume historical PE is typically 10-20% different from current
            return current_pe * 0.95
        return 18.0
    
    def is_overpriced(self, threshold_pct=20):
        """
        Check if stock is overpriced compared to sector
        threshold_pct: how much above sector average is considered overpriced
        """
        current_pe = self.get_current_pe()
        sector_pe = self.get_sector_average_pe()
        
        if current_pe <= 0 or sector_pe <= 0:
            return False
        
        premium = ((current_pe - sector_pe) / sector_pe) * 100
        return premium > threshold_pct
    
    def is_underpriced(self, threshold_pct=20):
        """
        Check if stock is underpriced compared to sector
        threshold_pct: how much below sector average is considered underpriced
        """
        current_pe = self.get_current_pe()
        sector_pe = self.get_sector_average_pe()
        
        if current_pe <= 0 or sector_pe <= 0:
            return False
        
        discount = ((sector_pe - current_pe) / sector_pe) * 100
        return discount > threshold_pct
    
    def get_valuation_assessment(self):
        """Get comprehensive valuation assessment"""
        current_pe = self.get_current_pe()
        sector_pe = self.get_sector_average_pe()
        hist_pe = self.get_historical_average_pe()
        
        is_over = self.is_overpriced()
        is_under = self.is_underpriced()
        
        return {
            'current_pe': current_pe,
            'sector_avg_pe': sector_pe,
            'historical_avg_pe': hist_pe,
            'is_overpriced': is_over,
            'is_underpriced': is_under,
            'assessment': 'Overpriced' if is_over else 'Underpriced' if is_under else 'Fairly Valued'
        }
    
    def get_price_to_book_assessment(self):
        """Assess P/B ratio"""
        pb = self.fundamental.get_pb_ratio()
        
        # Generally: PB < 1.0 = undervalued, 1.0-3.0 = fair, > 3.0 = overvalued
        if pb and pb < 1.0:
            return 'Undervalued'
        elif pb and pb > 3.0:
            return 'Overvalued'
        else:
            return 'Fair Value'
    
    def get_peg_assessment(self):
        """Assess PEG ratio"""
        peg = self.fundamental.get_peg_ratio()
        
        # PEG < 1.0 = undervalued relative to growth
        # PEG > 1.0 = overvalued relative to growth
        if peg and peg < 1.0:
            return 'Undervalued (Good Growth)'
        elif peg and peg > 1.5:
            return 'Overvalued (Relative to Growth)'
        else:
            return 'Fair Value'
    
    def compare_to_52week_price(self):
        """Compare current price to 52-week range"""
        current_price = self.info.get('currentPrice', None)
        high_52w = self.fundamental.get_52_week_high()
        low_52w = self.fundamental.get_52_week_low()
        
        if current_price and high_52w and low_52w:
            position = ((current_price - low_52w) / (high_52w - low_52w)) * 100
            return {
                'current_price': current_price,
                'high_52w': high_52w,
                'low_52w': low_52w,
                'position_in_range': position,
                'interpretation': 'Near 52-week high' if position > 80 else 'Near 52-week low' if position < 20 else 'Mid-range'
            }
        return None
    
    def get_earnings_growth(self):
        """Get earnings growth rate"""
        return self.fundamental.get_earnings_growth()
    
    def get_revenue_growth(self):
        """Get revenue growth rate"""
        return self.fundamental.get_revenue_growth()
    
    def get_profit_margin(self):
        """Get profit margin"""
        return self.fundamental.get_profit_margin()
    
    def get_roe(self):
        """Get return on equity"""
        return self.fundamental.get_roe()
    
    def get_debt_assessment(self):
        """Assess company leverage"""
        de_ratio = self.fundamental.get_debt_to_equity()
        
        if de_ratio is None:
            return 'Unknown'
        elif de_ratio < 1.0:
            return 'Conservative (Low Debt)'
        elif de_ratio < 2.0:
            return 'Moderate Debt'
        else:
            return 'High Debt'
    
    def get_liquidity_assessment(self):
        """Assess company liquidity"""
        current_ratio = self.fundamental.get_current_ratio()
        
        if current_ratio is None:
            return 'Unknown'
        elif current_ratio > 2.0:
            return 'Excellent'
        elif current_ratio > 1.0:
            return 'Good'
        else:
            return 'Potentially Concerning'
    
    def get_valuation_score(self):
        """
        Calculate overall valuation score (0-100)
        Higher = more expensive relative to fundamentals
        """
        score = 50  # Start at neutral
        
        # Adjust for P/E
        current_pe = self.get_current_pe()
        sector_pe = self.get_sector_average_pe()
        
        if current_pe > 0 and sector_pe > 0:
            pe_premium = ((current_pe - sector_pe) / sector_pe) * 100
            score += pe_premium * 0.5
        
        # Adjust for PEG
        peg = self.fundamental.get_peg_ratio()
        if peg:
            if peg < 1.0:
                score -= 10
            elif peg > 1.5:
                score += 10
        
        # Adjust for profit margin
        margin = self.get_profit_margin()
        if margin > 20:
            score -= 5
        elif margin < 5:
            score += 5
        
        # Clamp to 0-100
        return max(0, min(100, score))
    
    def get_investment_thesis(self):
        """Generate investment thesis based on valuation metrics"""
        assessment = self.get_valuation_assessment()
        peg_assessment = self.get_peg_assessment()
        pb_assessment = self.get_price_to_book_assessment()
        earnings_growth = self.get_earnings_growth()
        revenue_growth = self.get_revenue_growth()
        
        thesis = []
        
        # Valuation thesis
        thesis.append(f"Valuation: {assessment['assessment']} (P/E: {assessment['current_pe']:.2f} vs Sector: {assessment['sector_avg_pe']:.2f})")
        
        # Growth thesis
        if earnings_growth > 20:
            thesis.append(f"Strong Earnings Growth: {earnings_growth:.2f}%")
        elif earnings_growth > 0:
            thesis.append(f"Moderate Earnings Growth: {earnings_growth:.2f}%")
        else:
            thesis.append("Declining Earnings")
        
        # PEG thesis
        thesis.append(f"Relative Value: {peg_assessment}")
        
        # Risk assessment
        debt_status = self.get_debt_assessment()
        thesis.append(f"Leverage: {debt_status}")
        
        return thesis
    