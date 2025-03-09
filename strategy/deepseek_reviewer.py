import requests
from typing import Dict, Optional
import json


class DeepSeekReviewer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def review_trade(self, trade_data: Dict) -> Optional[Dict]:
        prompt = self._create_review_prompt(trade_data)

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3
                }
            )
            response.raise_for_status()
            analysis = response.json()["choices"][0]["message"]["content"]
            return self._parse_analysis(analysis)
        except Exception as e:
            print(f"DeepSeek review failed: {str(e)}")
            return None

    def _create_review_prompt(self, trade_data: Dict) -> str:
        return f"""
        As an AI trading expert, review this potential trade:
        
        Token: {trade_data['token']}
        Current Price: ${trade_data['current_price']:,.2f}
        Allora Prediction: ${trade_data['allora_prediction']:,.2f}
        Prediction Difference: {trade_data['prediction_diff']:.2f}%
        Direction: {trade_data['direction']}
        Market Condition: {trade_data['market_condition']}
        
        Please analyze this trade and respond in JSON format with:
        1. approval (true/false)
        2. confidence (0-100)
        3. reasoning (string)
        4. risk_score (1-10)
        """

    def _parse_analysis(self, analysis: str) -> Dict:
        try:
            # Find JSON block in the response
            start = analysis.find('{')
            end = analysis.rfind('}')

            # Ensure valid JSON bounds
            if start == -1 or end == -1:
                raise ValueError("No valid JSON found in the response")

            json_str = analysis[start:end + 1]  # Extract JSON substring
            return json.loads(json_str)  # Convert to dict
        except json.JSONDecodeError as e:
            print(f"JSON decoding error: {e}")
        except Exception as e:
            print(f"Error parsing analysis: {e}")

        return None  # Return None on failure
