import requests
import json
from datetime import datetime
from kafka import KafkaProducer
import time

KAFKA_TOPIC = "currency_fx_rate"

def fetch_usd_azn_rate():
    url = "https://open.er-api.com/v6/latest/USD"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["rates"]["AZN"]
    else:
        print(f"Failed to fetch FX rate. Status: {response.status_code}")
        return None

def main():
    producer = KafkaProducer(
        bootstrap_servers='localhost:29092',
        key_serializer=lambda k: k.encode('utf-8'),
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    while True:
        rate = fetch_usd_azn_rate()
        if rate:
            key = "USD/AZN"
            message = {
                "currency_pair": key,
                "rate": rate
            }
            producer.send(KAFKA_TOPIC, key=key, value=message)
            print(f"Sent FX rate to Kafka: {message}")
        else:
            print("Failed to fetch FX rate.")

        time.sleep(60)

if __name__ == "__main__":
    main()