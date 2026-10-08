import pandas as pd
import psycopg2

CSV_FILE = "gps_data.csv"

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "uav_tracking",
    "user": "postgres",
    "password": "password123"
}


def load_gps_data():
    print("Reading GPS data...")

    df = pd.read_csv(CSV_FILE)

    print(f"Loaded {len(df)} records.")

    # Convert timestamp
    df["recorded_at"] = pd.to_datetime(df["recorded_at"])

    # Remove records with missing coordinates
    df = df.dropna(subset=["latitude", "longitude"])

    # Validate latitude and longitude
    df = df[
        (df["latitude"].between(-90, 90))
        & (df["longitude"].between(-180, 180))
    ]

    print(f"{len(df)} valid GPS records remain.")

    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()

    for _, row in df.iterrows():

        cursor.execute(
            """
            INSERT INTO gps_points
            (
                device_id,
                recorded_at,
                latitude,
                longitude,
                altitude,
                speed,
                geom
            )
            VALUES
            (%s, %s, %s, %s, %s, %s,
             ST_SetSRID(
                 ST_MakePoint(%s, %s),
                 4326
             ))
            """,
            (
                row["device_id"],
                row["recorded_at"],
                row["latitude"],
                row["longitude"],
                row["altitude"],
                row["speed"],
                row["longitude"],
                row["latitude"],
            ),
        )

    connection.commit()

    cursor.close()
    connection.close()

    print("GPS data successfully loaded into PostGIS.")


if __name__ == "__main__":
    load_gps_data()