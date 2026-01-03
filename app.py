from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

# 從環境變數取得資料庫連線資訊
DB_HOST = os.environ.get("dpg-d5cegqbe5dus738dau7g-a")
DB_NAME = os.environ.get("final_database_xnad")
DB_USER = os.environ.get("final_database_xnad_user")
DB_PASSWORD = os.environ.get("BMojjUkwDRZeQNs2rVdYdV479542lLrV")
DB_PORT = int(os.environ.get("DB_PORT", 5432))

# 建立資料庫連線
def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    return conn

# 建立資料表（如果還沒建立過）
def create_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id SERIAL PRIMARY KEY,
            temperature FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

# 啟動時建表
create_table()

# 測試服務是否正常
@app.route("/", methods=["GET"])
def home():
    return "API is running"

# 上傳資料 API
@app.route("/upload", methods=["POST"])
def upload():
    data = request.json
    temperature = data.get("temperature")

    if temperature is None:
        return jsonify({"error": "temperature is required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO sensor_data (temperature) VALUES (%s);",
        (temperature,)
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"status": "success"})

# 查詢資料 API
@app.route("/data", methods=["GET"])
def get_data():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, temperature, created_at FROM sensor_data ORDER BY id DESC;"
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "temperature": r[1],
            "time": r[2].strftime("%Y-%m-%d %H:%M:%S")
        })

    return jsonify(result)

if __name__ == "__main__":
    # Render 上部署時使用 gunicorn，不需要這行
    app.run(host="0.0.0.0", port=5000)
