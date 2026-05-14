import pandas as pd
import numpy as np
import talib
import warnings

warnings.filterwarnings('ignore')


class TechnicalAnalyzer:
    """Performs technical analysis on stock price data"""

    def __init__(self, price_data):

        self.data = price_data.copy()

        # Flatten MultiIndex columns from yfinance
        if isinstance(self.data.columns, pd.MultiIndex):
            self.data.columns = self.data.columns.get_level_values(0)

        # Ensure dataframe
        if not isinstance(self.data, pd.DataFrame):
            raise ValueError("price_data must be a pandas DataFrame")

        required_cols = ['Close', 'High', 'Low', 'Volume']

        for col in required_cols:
            if col not in self.data.columns:
                raise ValueError(f"Missing required column: {col}")

        # Convert to clean 1D float64 numpy arrays
        self.close = (
            self.data['Close']
            .astype('float64')
            .to_numpy()
            .flatten()
        )

        self.high = (
            self.data['High']
            .astype('float64')
            .to_numpy()
            .flatten()
        )

        self.low = (
            self.data['Low']
            .astype('float64')
            .to_numpy()
            .flatten()
        )

        self.volume = (
            self.data['Volume']
            .astype('float64')
            .to_numpy()
            .flatten()
        )

        # Remove NaN rows if any
        valid_mask = (
            ~np.isnan(self.close) &
            ~np.isnan(self.high) &
            ~np.isnan(self.low) &
            ~np.isnan(self.volume)
        )

        self.close = self.close[valid_mask]
        self.high = self.high[valid_mask]
        self.low = self.low[valid_mask]
        self.volume = self.volume[valid_mask]

        # Debug
        print("Close shape:", self.close.shape)
        print("Close dtype:", self.close.dtype)

        # Indicators
        self.sma_50 = self._calculate_sma(50)
        self.sma_200 = self._calculate_sma(200)

        self.bb_upper, self.bb_middle, self.bb_lower = (
            self._calculate_bollinger_bands()
        )

        self.atr = self._calculate_atr()

    def _calculate_sma(self, period):
        """Calculate Simple Moving Average"""
        return talib.SMA(self.close, timeperiod=period)

    def _calculate_ema(self, period):
        """Calculate Exponential Moving Average"""
        return talib.EMA(self.close, timeperiod=period)

    def _calculate_bollinger_bands(self, period=20, num_std=2):
        """Calculate Bollinger Bands"""

        upper, middle, lower = talib.BBANDS(
            self.close,
            timeperiod=period,
            nbdevup=num_std,
            nbdevdn=num_std,
            matype=0
        )

        return upper, middle, lower

    def _calculate_atr(self, period=14):
        """Calculate Average True Range"""

        return talib.ATR(
            self.high,
            self.low,
            self.close,
            timeperiod=period
        )

    def calculate_rsi(self, period=14):
        """Calculate RSI"""

        return talib.RSI(
            self.close,
            timeperiod=period
        )

    def calculate_macd(self, fast=12, slow=26, signal=9):
        """Calculate MACD"""

        macd, signal_line, histogram = talib.MACD(
            self.close,
            fastperiod=fast,
            slowperiod=slow,
            signalperiod=signal
        )

        return {
            'MACD': macd,
            'Signal': signal_line,
            'Histogram': histogram
        }

    def calculate_stochastic(self, period=14, smooth_k=3, smooth_d=3):
        """Calculate Stochastic Oscillator"""

        slowk, slowd = talib.STOCH(
            self.high,
            self.low,
            self.close,
            fastk_period=period,
            slowk_period=smooth_k,
            slowd_period=smooth_d
        )

        return {
            'K': slowk,
            'D': slowd
        }

    def calculate_adx(self, period=14):
        """Calculate ADX"""

        return talib.ADX(
            self.high,
            self.low,
            self.close,
            timeperiod=period
        )

    def calculate_obv(self):
        """Calculate OBV"""

        return talib.OBV(
            self.close,
            self.volume
        )

    def calculate_vpt(self):
        """Calculate Volume Price Trend"""

        pct_change = np.zeros_like(self.close)

        pct_change[1:] = (
            (self.close[1:] - self.close[:-1]) /
            self.close[:-1]
        )

        vpt = np.cumsum(self.volume * pct_change)

        return vpt

    def detect_unusual_volume(self, period=20, threshold=1.5):
        """Detect unusual volume"""

        avg_volume = (
            pd.Series(self.volume)
            .rolling(window=period)
            .mean()
        )

        volume_ratio = self.volume / avg_volume

        return {
            'is_unusual': bool(volume_ratio.iloc[-1] > threshold),
            'ratio': float(volume_ratio.iloc[-1]),
            'current_volume': float(self.volume[-1]),
            'average_volume': float(avg_volume.iloc[-1])
        }

    def calculate_yearly_returns(self):
        """Calculate yearly returns"""

        data_copy = self.data.copy()

        if not isinstance(data_copy.index, pd.DatetimeIndex):
            try:
                data_copy.index = pd.to_datetime(data_copy.index)
            except:
                return pd.Series(dtype=float)

        data_copy['Year'] = data_copy.index.year

        yearly_returns = {}

        for year in sorted(data_copy['Year'].unique()):

            year_data = data_copy[data_copy['Year'] == year]

            if len(year_data) > 0:

                opening = year_data['Close'].iloc[0]
                closing = year_data['Close'].iloc[-1]

                yearly_return = (
                    (closing - opening) / opening
                )

                yearly_returns[year] = yearly_return

        return pd.Series(yearly_returns)

    def find_support_resistance(self, lookback=60):
        """Find support and resistance"""

        high = self.data['High'].iloc[-lookback:]
        low = self.data['Low'].iloc[-lookback:]
        close = self.data['Close'].iloc[-lookback:]

        pivot = (
            high.iloc[-1] +
            low.iloc[-1] +
            close.iloc[-1]
        ) / 3

        r1 = (2 * pivot) - low.iloc[-1]
        s1 = (2 * pivot) - high.iloc[-1]

        r2 = pivot + (high.iloc[-1] - low.iloc[-1])
        s2 = pivot - (high.iloc[-1] - low.iloc[-1])

        return {
            'PP': pivot,
            'R1': r1,
            'R2': r2,
            'S1': s1,
            'S2': s2
        }

    def check_golden_cross(self):

        if len(self.sma_50) < 2 or len(self.sma_200) < 2:
            return False

        return (
            self.sma_50[-1] > self.sma_200[-1]
            and
            self.sma_50[-2] <= self.sma_200[-2]
        )

    def check_death_cross(self):

        if len(self.sma_50) < 2 or len(self.sma_200) < 2:
            return False

        return (
            self.sma_50[-1] < self.sma_200[-1]
            and
            self.sma_50[-2] >= self.sma_200[-2]
        )

    def get_trend_strength(self):

        if len(self.sma_50) < 1 or len(self.sma_200) < 1:
            return 'Unknown'

        price = self.close[-1]
        sma50 = self.sma_50[-1]
        sma200 = self.sma_200[-1]

        if price > sma50 > sma200:
            return 'Strong Uptrend'

        elif price > sma200 and sma50 > sma200:
            return 'Uptrend'

        elif price < sma50 < sma200:
            return 'Strong Downtrend'

        elif price < sma200 and sma50 < sma200:
            return 'Downtrend'

        return 'Neutral'

    def calculate_momentum(self, period=10):

        if len(self.close) < period:
            return np.array([0])

        momentum = np.zeros_like(self.close)

        momentum[period:] = (
            self.close[period:] - self.close[:-period]
        )

        return momentum