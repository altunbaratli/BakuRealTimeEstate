from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import (
    StreamTableEnvironment, EnvironmentSettings, DataTypes,
)

def main():
    # 1. Flink environment
    env = StreamExecutionEnvironment.get_execution_environment()
    settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
    t_env = StreamTableEnvironment.create(env, environment_settings=settings)

    # 2. Set Kafka properties
    kafka_props = {
        "bootstrap.servers": "kafka:9092",
        "group.id": "flink-stream-processor"
    }

    # 3. Define source table: real_estate_listings
    t_env.execute_sql(f"""
        CREATE TABLE listings (
            listing_id STRING,
            district STRING,
            rooms INT,
            area_sqm DOUBLE,
            price_azn DOUBLE,
            price_per_sqm_azn DOUBLE
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'real_estate_listings',
            'properties.bootstrap.servers' = '{kafka_props["bootstrap.servers"]}',
            'format' = 'json',
            'scan.startup.mode' = 'earliest-offset'
        )
    """)

    # 4. Define source table: currency_fx_rate
    t_env.execute_sql(f"""
        CREATE TABLE fx_rate (
            currency_pair STRING,
            rate DOUBLE,
            PRIMARY KEY (currency_pair) NOT ENFORCED
        ) WITH (
            'connector' = 'upsert-kafka',
            'topic' = 'currency_fx_rate',
            'properties.bootstrap.servers' = '{kafka_props["bootstrap.servers"]}',
            'key.format' = 'raw',
            'value.format' = 'json'
        )
    """)

    # 5. Define sink table
    t_env.execute_sql(f"""
        CREATE TABLE enriched_listings (
            listing_id STRING,
            district STRING,
            rooms INT,
            area_sqm DOUBLE,
            price_azn DOUBLE,
            rate DOUBLE,
            price_usd_per_sqm DOUBLE,
            PRIMARY KEY (listing_id) NOT ENFORCED
        ) WITH (
            'connector' = 'upsert-kafka',
            'topic' = 'analytics_price_usd_per_sqm',
            'properties.bootstrap.servers' = '{kafka_props["bootstrap.servers"]}',
            'key.format' = 'json',
            'value.format' = 'json'
        )
    """)

    # 6. Join and insert into sink
    t_env.execute_sql("""
        INSERT INTO enriched_listings
        SELECT 
            l.listing_id,
            l.district,
            l.rooms,
            l.area_sqm,
            l.price_azn,
            r.rate,
            ROUND(l.price_azn / l.area_sqm / r.rate, 2) AS price_usd_per_sqm
        FROM listings l
        LEFT JOIN fx_rate r
        ON r.currency_pair = 'USD/AZN'
    """)

    print("Submitting job...")

if __name__ == "__main__":
    main()