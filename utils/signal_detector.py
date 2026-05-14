import pandas as pd
import numpy as np

class SignalDetector:
    """Detects trading signals and calculates entry/exit points"""
    
    def __init__(self, price_data, technical_analyzer):
        self.data = price_data
        self.ta = technical_analyzer
        self.current_price = price_data['Close'].iloc[-1]
    
    def detect_ma_crossover_signal(self):
        """Detect MA50/MA200 crossover signals"""
        sma50 = self.ta.sma_50[-1]
        sma200 = self.ta.sma_200[-1]
        price = self.current_price
        
        # Check if we're in uptrend or downtrend
        is_uptrend = sma50 > sma200
        
        signal = 'HOLD'
        description = "No clear crossover signal"
        
        # Golden cross (BUY signal)
        if self.ta.check_golden_cross():
            signal = 'BUY'
            description = "Golden Cross: SMA50 crossed above SMA200. Bullish momentum shift."
        
        # Death cross (SELL signal)
        elif self.ta.check_death_cross():
            signal = 'SELL'
            description = "Death Cross: SMA50 crossed below SMA200. Bearish momentum shift."
        
        # Additional signals based on current position
        elif is_uptrend and price > sma50:
            signal = 'BUY'
            description = f"Price ({price:.2f}) above SMA50 ({sma50:.2f}) in uptrend. Bullish."
        
        elif not is_uptrend and price < sma50:
            signal = 'SELL'
            description = f"Price ({price:.2f}) below SMA50 ({sma50:.2f}) in downtrend. Bearish."
        
        else:
            signal = 'HOLD'
            description = "Price in transition between moving averages."
        
        return {
            'signal': signal,
            'description': description,
            'sma50': sma50,
            'sma200': sma200
        }
    
    def detect_rsi_signal(self):
        """Detect oversold/overbought conditions using RSI"""
        rsi = self.ta.calculate_rsi()
        current_rsi = rsi[-1]
        
        signal = 'HOLD'
        description = ""
        
        if current_rsi < 30:
            signal = 'BUY'
            description = f"RSI {current_rsi:.2f}: Oversold. Potential reversal upward."
        elif current_rsi > 70:
            signal = 'SELL'
            description = f"RSI {current_rsi:.2f}: Overbought. Potential reversal downward."
        else:
            signal = 'HOLD'
            description = f"RSI {current_rsi:.2f}: Neutral zone. No extreme condition."
        
        return {
            'signal': signal,
            'description': description,
            'rsi': current_rsi
        }
    
    def detect_volume_spike_signal(self):
        """Detect unusual volume spikes"""
        vol_analysis = self.ta.detect_unusual_volume()
        
        signal = 'HOLD'
        description = ""
        
        if vol_analysis['is_unusual']:
            # Check price direction with volume spike
            recent_close = self.data['Close'].iloc[-1]
            prev_close = self.data['Close'].iloc[-2] if len(self.data) > 1 else recent_close
            
            if recent_close > prev_close:
                signal = 'BUY'
                description = f"Volume Spike ({vol_analysis['ratio']:.2f}x avg) with price up. Bullish confirmation."
            else:
                signal = 'SELL'
                description = f"Volume Spike ({vol_analysis['ratio']:.2f}x avg) with price down. Bearish confirmation."
        else:
            signal = 'HOLD'
            description = f"Normal volume levels. No unusual activity."
        
        return {
            'signal': signal,
            'description': description,
            'volume_ratio': vol_analysis['ratio']
        }
    
    def detect_bollinger_bands_signal(self):
        """Detect signals based on Bollinger Bands"""
        price = self.current_price
        upper = self.ta.bb_upper[-1]
        lower = self.ta.bb_lower[-1]
        middle = self.ta.bb_middle[-1]
        
        signal = 'HOLD'
        description = ""
        
        if price > upper:
            signal = 'SELL'
            description = f"Price ({price:.2f}) above upper Bollinger Band ({upper:.2f}). Potential pullback."
        elif price < lower:
            signal = 'BUY'
            description = f"Price ({price:.2f}) below lower Bollinger Band ({lower:.2f}). Potential bounce."
        else:
            if price > middle:
                signal = 'BUY'
                description = f"Price ({price:.2f}) between middle and upper band. Mild bullish."
            else:
                signal = 'SELL'
                description = f"Price ({price:.2f}) between lower and middle band. Mild bearish."
        
        return {
            'signal': signal,
            'description': description,
            'upper_band': upper,
            'lower_band': lower,
            'middle_band': middle
        }
    
    def detect_macd_signal(self):
        """Detect MACD crossover signals"""
        macd = self.ta.calculate_macd()
        
        macd_line = macd['MACD'][-1]
        signal_line = macd['Signal'][-1]
        histogram = macd['Histogram'][-1]
        
        signal = 'HOLD'
        description = ""
        
        if histogram > 0 and histogram > macd['Histogram'][-2]:
            signal = 'BUY'
            description = f"MACD above signal line with increasing histogram. Bullish momentum."
        elif histogram < 0 and histogram < macd['Histogram'][-2]:
            signal = 'SELL'
            description = f"MACD below signal line with decreasing histogram. Bearish momentum."
        else:
            signal = 'HOLD'
            description = f"MACD histogram neutral or flattening."
        
        return {
            'signal': signal,
            'description': description,
            'macd': macd_line,
            'signal_line': signal_line
        }
    
    def detect_all_signals(self):
        """Aggregate all signals"""
        return {
            'ma_crossover': self.detect_ma_crossover_signal(),
            'rsi': self.detect_rsi_signal(),
            'volume_spike': self.detect_volume_spike_signal(),
            'bollinger_bands': self.detect_bollinger_bands_signal(),
            'macd': self.detect_macd_signal()
        }
    
    def get_entry_exit_points(self):
        """Calculate suggested entry, exit, and stop loss points"""
        current_price = self.current_price
        atr = self.ta.atr[-1] if len(self.ta.atr) > 0 else current_price * 0.02
        
        # Support and Resistance
        support_resistance = self.ta.find_support_resistance()
        
        # Calculate entry point (support level or dip)
        entry_point = support_resistance['S1']
        
        # Calculate exit points
        exit_point_profit = support_resistance['R1']  # First resistance
        exit_point_max = support_resistance['R2']     # Second resistance
        
        # Stop loss
        stop_loss = support_resistance['S2']
        
        # Calculate percentages
        if entry_point > 0:
            profit_potential = ((exit_point_profit - entry_point) / entry_point) * 100
            profit_target = ((exit_point_profit - current_price) / current_price) * 100
            max_profit = ((exit_point_max - entry_point) / entry_point) * 100
        else:
            profit_potential = 0
            profit_target = 0
            max_profit = 0
        
        if stop_loss > 0:
            max_loss_pct = abs(((stop_loss - current_price) / current_price) * 100)
        else:
            max_loss_pct = 0
        
        # Risk level assessment
        risk_reward_ratio = profit_potential / max_loss_pct if max_loss_pct > 0 else 0
        
        if risk_reward_ratio > 2:
            risk_level = "Low Risk, High Reward"
        elif risk_reward_ratio > 1:
            risk_level = "Moderate Risk/Reward"
        else:
            risk_level = "High Risk"
        
        return {
            'entry_point': entry_point,
            'exit_point_profit': exit_point_profit,
            'exit_point_max': exit_point_max,
            'stop_loss': stop_loss,
            'profit_potential': profit_potential,
            'profit_target': profit_target,
            'max_profit': max_profit,
            'max_loss_pct': max_loss_pct,
            'risk_level': risk_level,
            'risk_reward_ratio': risk_reward_ratio
        }
    
    def get_signal_summary(self):
        """Get overall signal sentiment (Bullish, Bearish, Neutral)"""
        signals = self.detect_all_signals()
        
        buy_count = sum(1 for s in signals.values() if s['signal'] == 'BUY')
        sell_count = sum(1 for s in signals.values() if s['signal'] == 'SELL')
        hold_count = sum(1 for s in signals.values() if s['signal'] == 'HOLD')
        
        if buy_count > sell_count:
            return 'BULLISH'
        elif sell_count > buy_count:
            return 'BEARISH'
        else:
            return 'NEUTRAL'
        