from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "uav_tracking",
    "user": "postgres",
    "password": "password123"
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


@app.route("/")
def home():
    return jsonify({
        "system": "UAV Field Operations API",
        "status": "online"
    })


@app.route("/api/gps")
def gps_points():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            device_id,
            recorded_at,
            latitude,
            longitude,
            altitude,
            speed
        FROM gps_points
        ORDER BY recorded_at DESC
    """)

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    data = []

    for row in rows:
        data.append({
            "id": row[0],
            "device_id": row[1],
            "recorded_at": row[2].isoformat(),
            "latitude": row[3],
            "longitude": row[4],
            "altitude": row[5],
            "speed": row[6]
        })

    return jsonify(data)


@app.route("/api/stats")
def statistics():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            COUNT(*) AS total_points,
            COUNT(DISTINCT device_id) AS devices,
            MIN(recorded_at) AS first_record,
            MAX(recorded_at) AS last_record
        FROM gps_points
    """)

    row = cursor.fetchone()

    cursor.close()
    connection.close()

    return jsonify({
        "total_points": row[0],
        "devices": row[1],
        "first_record": row[2].isoformat() if row[2] else None,
        "last_record": row[3].isoformat() if row[3] else None
    })


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )