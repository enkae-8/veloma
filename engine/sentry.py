import requests
import time

class Sentry:
    def __init__(self):
        self.last_price = self.get_live_price()
        self.risk = 10.0 # Starting tension

    def get_live_price(self):
        """Fetches the real-world heart rate of the market."""
        try:
            # No API key needed for this spot price check
            r = requests.get('https://api.coinbase.com/v2/prices/BTC-USD/spot', timeout=2)
            return float(r.json()['data']['amount'])
        except Exception:
            # If the internet/API lags, that is 'Environment Friction'
            return self.last_price if hasattr(self, 'last_price') else 40000.0

    def get_risk(self):
        """Calculates risk based on price volatility (The S3/Compression effect)."""
        current_price = self.get_live_price()
        
        # Calculate the absolute movement
        price_diff = abs(current_price - self.last_price)
        
        # Convert movement into 'Structural Strain'
        # If BTC moves $10, risk increases. If it's still, risk slowly decays.
        market_strain = (price_diff / self.last_price) * 5000 
        
        # Risk update: Market moves + Natural entropy - Passive decay
        self.risk = self.risk + market_strain - 0.2
        
        # Clamp between 0 and 100
        self.risk = max(0, min(100, self.risk))
        
        self.last_price = current_price
        return self.risk

    def update_state(self, hype_input):
        """No longer needed - the world is now the input."""
        pass