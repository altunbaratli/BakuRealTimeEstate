import random
import json
import time
from datetime import datetime
from kafka import KafkaProducer

KAFKA_TOPIC = "real_estate_listings"
DISTRICTS = ["Nizami", "Narimanov", "Yasamal", "Sabail", "Khatai"]
ROOM_COUNTS = [1, 2, 3, 4]
PRICE_RANGE = (50000, 500000)
AREA_RANGE = (40, 200)

producer = KafkaProducer(
    bootstrap_servers='localhost:29092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generate_listing():
    price_azn = random.randint(*PRICE_RANGE)
    area = random.randint(*AREA_RANGE)
    return {
        "listing_id": f"listing-{random.randint(100000, 999999)}",
        "district": random.choice(DISTRICTS),
        "rooms": random.choice(ROOM_COUNTS),
        "area_sqm": area,
        "price_azn": price_azn,
        "price_per_sqm_azn": round(price_azn / area, 2)
    }

def main():
    while True:
        listing = generate_listing()
        producer.send(KAFKA_TOPIC, listing)
        print(f"Sent listing: {listing}")
        time.sleep(3)  # Simulate delay between listings

if __name__ == "__main__":
    main()