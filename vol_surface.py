import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from utils import black_scholes_price
from scipy.optimize import brentq

class VolSurface:
    def __init__ (self, data): 
        self.data = data
    
    def implied_volatility(self, S, K, T, r, option_price, option_type): 
        def objective(sigma): 
            return black_scholes_price(S, K, T, r, sigma, option_type) - option_price
        try:
            return brentq(objective, 1e-6, 5.0)
        except ValueError:
            return np.nan
    
    def compute_surface(self, r=0.01):
        ivs = []
        for _, row in self.data.iterrows():
            T = (
                pd.to_datetime(row['expiration'], dayfirst=True) -
                pd.to_datetime(row['date'], dayfirst=True)
            ).days / 365
            if T <= 0:
                ivs.append(np.nan)
                continue
            iv = self.implied_volatility(
                S = row['underlying_price'],
                K = row['strike'],
                T = T,
                r = r, 
                option_price = (row['bid'] + row['ask']) / 2,
                option_type = row['type']
            )
            ivs.append(iv)
        self.data['implied_vol'] = ivs        
        print(self.data['implied_vol'].describe())
        print(self.data['implied_vol'].isna().sum(), "NaNs")
    
    def plot_surface(self):
        df = self.data.dropna(subset=['implied_vol'])
        
        # Convert date columns to float days (T)
        df['T'] = (pd.to_datetime(df['expiration'], dayfirst=True) - pd.to_datetime(df['date'], dayfirst=True)).dt.days / 365
        
        strikes = np.sort(df['strike'].unique())
        expiries = np.sort(df['T'].unique())

        X, Y = np.meshgrid(strikes, expiries)
        Z = np.full_like(X, np.nan, dtype=np.float64)

        for i, expiry in enumerate(expiries):
            for j, strike in enumerate(strikes):
                subset = df[(df['strike'] == strike) & (df['T'] == expiry)]
                if not subset.empty:
                    Z[i, j] = subset['implied_vol'].mean()

        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        ax.plot_surface(X, Y, Z, cmap='viridis')
        ax.set_xlabel('Strike')
        ax.set_ylabel('Time to Expiry (Years)')
        ax.set_zlabel('Implied Volatility')
        plt.show()