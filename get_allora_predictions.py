import requests
import time
from datetime import datetime
from utils.constants import ALLORA_API_BASE_URL

ALLORA_UPSHOT_KEY = "UP-3951d2e6ffe844bbb53028bd"  # Replace with your key

def get_inference(topic_id):
    url = f'{ALLORA_API_BASE_URL}ethereum-11155111?allora_topic_id={topic_id}'
    headers = {
        'accept': 'application/json',
        'x-api-key': ALLORA_UPSHOT_KEY
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def main():
    topics = {
        "ETH": 13,
        "BTC": 14
    }

    while True:
        print(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)
        
        for token, topic_id in topics.items():
            data = get_inference(topic_id)
            if data:
                inference = data['data']['inference_data']['network_inference_normalized']
                print(f"{token} Prediction: ${float(inference):,.2f}")
                print(f"Raw Response: {data}\n")
        
        print("Waiting 60 seconds...\n")
        time.sleep(60)

if __name__ == "__main__":
    main()