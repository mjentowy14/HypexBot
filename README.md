# 🚀 AlloraNetwork, HyperLiquid & DeepSeek AI Auto Trade Bot

Welcome to the **AlloraNetwork HyperLiquid Auto Trading Bot**! This project leverages **[AlloraNetwork](https://www.allora.network/) inference** to enable **automatic trading** on the decentralized exchange [HyperLiquid](https://app.hyperliquid.xyz/). The bot utilizes AI-driven predictions from AlloraNetwork, combined with **DeepSeek AI trade validation**, to make informed trading decisions based on customizable strategies. 📈🤖

By default, the bot uses a **volatility-based strategy**, but you can define your own custom strategy to suit your trading preferences.

---

## 🛠️ Prerequisites

Before you get started, make sure you have the following:

1. **HyperLiquid Account**:
   - Create an account on [HyperLiquid](https://app.hyperliquid.xyz/).
   - Set up your **Vault** for trading.
2. **API and Wallet Setup**:
   - Go to **More Options** > **API** in HyperLiquid.
   - Generate your **Private Key** and **Wallet Address**.
   - 🔒 Securely store this information.
3. **Allora API Key**:
   - Obtain an API key from the [Upshot Developer Portal](https://developer.upshot.xyz/).
4. **DeepSeek API Key**:
   - Get your [DeepSeek API](https://deepseek.com/) key for AI-powered trade validation.

<img src="https://github.com/HarbhagwanDhaliwal/Allora_HyperLiquid_AutoTradeBot/blob/5f815d3fb8de1fc98c5c49f6a041dedab476ce07/hyper_api.jpeg" alt="HyperLiquid API Setup" width="500"/>

---

## 🚀 Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/HarbhagwanDhaliwal/Allora_HyperLiquid_AutoTradeBot.git
   ```
2. **Create a Virtual Environment and Activate It**:
   ```bash
   python3 -m venv venv && source venv/bin/activate
   ```
3. **Install Required Packages**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure the Bot**:
   - Rename the `.env.example` file to `.env`:
     ```bash
     mv .env.example .env
     ```
   - Open the `.env` file and update the fields with your details:
     ```bash
     # HyperLiquid Credentials
     HL_SECRET_KEY=        # Enter your HyperLiquid secret key  
     HL_ACCOUNT_ADDRESS=   # Enter your HyperLiquid account address  

     # Vault Configuration  
     HL_VAULT=             # Enter your HyperLiquid vault identifier  

     # Master Address Configuration  
     HL_MASTER_ADDRESS=    # Enter your MetaMask wallet address  

     # Network Selection  
     MAINNET=False  # Set to True for mainnet, False for testnet  

     # API Keys  
     DEEPSEEK_API_KEY=     # Enter your DeepSeek API key  
     ALLORA_UPSHOT_KEY=    # Enter your Allora API key  

     # Trading Parameters  
     PRICE_GAP=0.25                        # Minimum price gap for trades  
     ALLOWED_AMOUNT_PER_TRADE=10            # Maximum amount per trade  
     MAX_LEVERAGE=1                         # Maximum leverage allowed  
     CHECK_FOR_TRADES=300                    # Interval (seconds) to check for trades  
     VOLATILITY_THRESHOLD=0.02               # Volatility threshold for trade execution  

     # Database Configuration  
     DB_PATH=trading_logs.db                # Path to the trading database  

     # Topic IDs (Asset Identifiers)  
     BTC_TOPIC_ID=14                         # Bitcoin topic ID  
     ETH_TOPIC_ID=13                         # Ethereum topic ID  
     ```
   - Save the file (`CTRL+X`, then `Y`, and `Enter`). 💾
5. **Run the Bot**:
   ```bash
   python3 main.py
   ```

---

## ⚙️ Configuration Details

- **PRICE_GAP**: Percentage difference between Allora's prediction and the current price required to trigger a trade.
- **ALLOWED_AMOUNT_PER_TRADE**: 💵 Maximum amount (in USD) for each trade, excluding leverage.
- **MAX_LEVERAGE**: Maximum leverage multiplier (e.g., `1` for 1x leverage).
- **CHECK_FOR_TRADES**: Time interval (in seconds) for the bot to check for trading opportunities.
- **VOLATILITY_THRESHOLD**: Minimum volatility level required before a trade executes.
- **BTC_TOPIC_ID** and **ETH_TOPIC_ID**: Mapping of tradable tokens to their Allora prediction topic IDs.

---

## 🧠 Default Volatility Strategy

By default, the bot employs a **volatility-based strategy** to analyze market conditions and Allora's predictions to execute trades. The strategy is implemented in the `volatility_strategy` module.

---

## 🛠️ Custom Strategy

Modify `custom_strategy.py` to create a personalized trading strategy.

### Example Custom Strategy
```python
def custom_strategy(token, price=None, allora_signal=None, allora_prediction=None):
    """
    Custom strategy that trades against Allora’s predictions in high-volatility conditions.
    """
    if price is None or allora_signal is None or allora_prediction is None:
        return None
    
    return volatility_strategy.execute(token, price, allora_signal, allora_prediction)
```
### How to Use
1. Open `strategy/custom_strategy.py`.
2. Modify `custom_strategy` to implement your own logic.

---

## 🤖 DeepSeek AI Trade Reviewer

The bot integrates **DeepSeek AI** for trade validation. It assesses trade risk, confidence, and reasoning before execution.

### How It Works

1. **Trade Analysis**:
   - Current price vs. Allora prediction
   - Market volatility
   - Trade direction (BUY/SELL)
   - Historical performance

2. **Decision Metrics**:
   - `approval` (true/false): Trade approval status
   - `confidence` (0-100): Confidence level in the trade
   - `reasoning`: Explanation of the trade decision
   - `risk_score` (1-10): Trade risk assessment

3. **Trade Execution Criteria**:
   - Confidence score ≥ 70%
   - DeepSeek AI approval ✅
   - Risk score logged for tracking

### Example Output
```
Trade Review by DeepSeek AI:
  Confidence: 85%
  Reasoning: "Allora prediction aligns with market trends.
              Volatility stable. Historical success rate: 70%."
  Risk Score: 3/10
```

---

## 🔄 Example Workflow

1. **Allora Prediction**: "BUY" signal detected for BTC.
2. **Custom Strategy**: Evaluates trade feasibility.
3. **DeepSeek AI Review**: Validates trade based on risk, confidence, and reasoning.
4. **Bot Action**:
   - ✅ If Allora, Custom Strategy, and DeepSeek AI agree → Trade executed.
   - ❌ If any disagree → Trade rejected.

---

## 💬 Support

For questions, reach out via GitHub. If this project helps you, consider giving it a ⭐!

---

## 🤝 Contribute

This project is open source! Feel free to fork the repo, improve the bot, and submit a pull request. 🌟

---

Happy Trading! 🚀📈

