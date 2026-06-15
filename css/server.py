#!/usr/bin/env python3
"""
北京交通大学智慧食堂实时监测系统 - 后端服务
使用 Python Flask + SQLite 实现
"""

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import random
import sqlite3
from datetime import datetime
from pathlib import Path

app = Flask(__name__)
CORS(app)

# 数据库文件名
BASE_DIR = Path(__file__).resolve().parent
DB_NAME = BASE_DIR / 'canteen.db'

SIMULATION_SETTINGS = {
    "queueMin": 1,
    "queueMax": 15,
    "closedRate": 10,
    "occupancyRate": 60,
    "maintenanceRate": 2,
    "tableCount": 80,
    "refreshInterval": 3,
}

SETTING_LIMITS = {
    "queueMin": (0, 50),
    "queueMax": (0, 80),
    "closedRate": (0, 100),
    "occupancyRate": (0, 100),
    "maintenanceRate": (0, 100),
    "tableCount": (10, 160),
    "refreshInterval": (1, 15),
}

def clamp_number(value, key):
    """将用户输入限制在合理范围内，避免仿真参数失控。"""
    minimum, maximum = SETTING_LIMITS[key]
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = SIMULATION_SETTINGS[key]
    return max(minimum, min(maximum, number))

def get_random_queue():
    """根据当前仿真参数生成随机排队人数。"""
    low = min(SIMULATION_SETTINGS["queueMin"], SIMULATION_SETTINGS["queueMax"])
    high = max(SIMULATION_SETTINGS["queueMin"], SIMULATION_SETTINGS["queueMax"])
    return random.randint(low, high)

def calculate_wait_time(queue_count):
    """计算预计等待时间"""
    if queue_count <= 2:
        return "无需排队"
    elif queue_count <= 5:
        return f"{queue_count * 1.5:.0f}min"
    elif queue_count <= 10:
        return f"{queue_count * 1.2:.0f}min"
    else:
        return f"{queue_count * 1.5:.0f}min"

def row_to_window(row):
    """将数据库窗口记录转换为前端使用的 JSON 字段。"""
    return {
        "id": row[0],
        "name": row[1],
        "category": row[2],
        "queueCount": row[3],
        "waitTime": row[4],
        "status": row[5]
    }

def ensure_table_count(cursor):
    """根据用户设置增减数据库中的餐桌数量。"""
    target_count = SIMULATION_SETTINGS["tableCount"]
    cursor.execute('SELECT COUNT(*) FROM tables')
    current_count = cursor.fetchone()[0]

    if current_count < target_count:
        cursor.execute('SELECT COALESCE(MAX(id), 0) FROM tables')
        next_id = cursor.fetchone()[0] + 1
        for table_id in range(next_id, next_id + target_count - current_count):
            cursor.execute(
                'INSERT INTO tables VALUES (?,?,?,?,?)',
                (table_id, 0, 4, 0, datetime.now().isoformat())
            )
    elif current_count > target_count:
        cursor.execute(
            'DELETE FROM tables WHERE id IN (SELECT id FROM tables ORDER BY id DESC LIMIT ?)',
            (current_count - target_count,)
        )

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """获取当前仿真参数。"""
    return jsonify(SIMULATION_SETTINGS)

@app.route('/api/settings', methods=['PUT'])
def update_settings():
    """更新仿真参数。"""
    data = request.get_json(silent=True) or {}
    for key in SIMULATION_SETTINGS:
        if key in data:
            SIMULATION_SETTINGS[key] = clamp_number(data[key], key)

    if SIMULATION_SETTINGS["queueMin"] > SIMULATION_SETTINGS["queueMax"]:
        SIMULATION_SETTINGS["queueMin"], SIMULATION_SETTINGS["queueMax"] = (
            SIMULATION_SETTINGS["queueMax"],
            SIMULATION_SETTINGS["queueMin"],
        )

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    ensure_table_count(c)
    conn.commit()
    conn.close()
    return jsonify(SIMULATION_SETTINGS)

@app.route('/api/windows', methods=['GET'])
def get_windows():
    """获取窗口实时数据（从数据库读取并更新）"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 更新数据
    c.execute('SELECT id FROM windows')
    window_ids = [row[0] for row in c.fetchall()]
    
    for wid in window_ids:
        queue_count = get_random_queue()
        wait_time = calculate_wait_time(queue_count)
        status = 'closed' if random.randint(1, 100) <= SIMULATION_SETTINGS["closedRate"] else 'open'
        c.execute('''
            UPDATE windows SET queue_count=?, wait_time=?, status=?, last_update=? WHERE id=?
        ''', (queue_count, wait_time, status, datetime.now().isoformat(), wid))
    
    # 查询数据
    c.execute('SELECT id, name, category, queue_count, wait_time, status FROM windows ORDER BY id')
    windows = [row_to_window(row) for row in c.fetchall()]
    
    conn.commit()
    conn.close()
    return jsonify(windows)

@app.route('/api/windows', methods=['POST'])
def create_window():
    """新增食堂窗口。"""
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    category = (data.get('category') or '').strip()

    if not name:
        return jsonify({"error": "窗口名称不能为空"}), 400
    if not category:
        category = "综合"

    queue_count = get_random_queue()
    wait_time = calculate_wait_time(queue_count)
    now = datetime.now().isoformat()

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        '''
        INSERT INTO windows (name, category, queue_count, wait_time, status, last_update)
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
        (name, category, queue_count, wait_time, 'open', now)
    )
    new_id = c.lastrowid
    conn.commit()

    c.execute('SELECT id, name, category, queue_count, wait_time, status FROM windows WHERE id=?', (new_id,))
    window = row_to_window(c.fetchone())
    conn.close()
    return jsonify(window), 201

@app.route('/api/windows/<int:window_id>', methods=['DELETE'])
def delete_window(window_id):
    """删除指定食堂窗口。"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM windows WHERE id=?', (window_id,))
    deleted = c.rowcount
    conn.commit()
    conn.close()

    if deleted == 0:
        return jsonify({"error": "窗口不存在"}), 404
    return jsonify({"message": "删除成功", "id": window_id})

@app.route('/api/tables', methods=['GET'])
def get_tables():
    """获取餐桌实时数据（从数据库读取并更新）"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    ensure_table_count(c)
    
    # 更新数据
    c.execute('SELECT id FROM tables')
    table_ids = [row[0] for row in c.fetchall()]
    
    for tid in table_ids:
        is_occupied = 1 if random.randint(1, 100) <= SIMULATION_SETTINGS["occupancyRate"] else 0
        current_people = random.randint(1, 4) if is_occupied else 0
        c.execute('''
            UPDATE tables SET is_occupied=?, current_people=?, last_update=? WHERE id=?
        ''', (is_occupied, current_people, datetime.now().isoformat(), tid))
    
    # 查询数据
    c.execute('SELECT id, is_occupied, capacity, current_people FROM tables')
    tables = []
    for row in c.fetchall():
        is_maintenance = random.randint(1, 100) <= SIMULATION_SETTINGS["maintenanceRate"]
        tables.append({
            "id": row[0],
            "isOccupied": bool(row[1]),
            "isMaintenance": is_maintenance,
            "capacity": row[2],
            "currentPeople": row[3],
            "lastUpdate": datetime.now().isoformat()
        })
    
    conn.commit()
    conn.close()
    return jsonify(tables)

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """获取食堂统计数据"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    ensure_table_count(c)
    
    c.execute('SELECT COUNT(*) FROM tables')
    total_tables = c.fetchone()[0]

    c.execute('SELECT COUNT(*) FROM tables WHERE is_occupied=1')
    occupied_tables = c.fetchone()[0]
    
    c.execute('SELECT SUM(current_people) FROM tables')
    total_people = c.fetchone()[0] or 0
    
    c.execute('SELECT AVG(queue_count) FROM windows WHERE status="open"')
    avg_queue = c.fetchone()[0] or 0

    c.execute('SELECT COUNT(*) FROM windows WHERE status="open"')
    open_windows = c.fetchone()[0]

    c.execute('SELECT COUNT(*) FROM windows')
    total_windows = c.fetchone()[0]
    
    conn.commit()
    conn.close()
    
    return jsonify({
        "totalTables": total_tables,
        "occupiedTables": occupied_tables,
        "emptyTables": total_tables - occupied_tables,
        "totalPeople": total_people,
        "avgWaitTime": int(avg_queue * 1.2),
        "openWindows": open_windows,
        "totalWindows": total_windows,
        "peakTime": "12:00-12:30",
        "updateTime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "settings": SIMULATION_SETTINGS
    })

@app.route('/api/menu', methods=['GET'])
def get_menu():
    """获取今日菜单"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 更新销量
    c.execute('SELECT id, sold FROM menu')
    for row in c.fetchall():
        new_sold = max(0, row[1] + random.randint(-5, 10))
        c.execute('UPDATE menu SET sold=? WHERE id=?', (new_sold, row[0]))
    
    # 查询菜单
    c.execute('SELECT id, name, price, rating, sold FROM menu')
    menu = []
    for row in c.fetchall():
        menu.append({
            "id": row[0],
            "name": row[1],
            "price": row[2],
            "rating": row[3],
            "sold": row[4]
        })
    
    conn.commit()
    conn.close()
    return jsonify(menu)

@app.route('/')
def index():
    """返回首页"""
    return send_file('index.html')

if __name__ == '__main__':
    # 确保数据库存在
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.close()
    except:
        print("数据库文件不存在，请先运行 init_database.py")
        exit(1)
    
    print("Server running on http://localhost:8888")
    print("Database file:", DB_NAME)
    print("API endpoints:")
    print("  GET /api/windows - 窗口排队数据")
    print("  POST /api/windows - 新增窗口")
    print("  DELETE /api/windows/<id> - 删除窗口")
    print("  GET /api/settings - 获取仿真参数")
    print("  PUT /api/settings - 更新仿真参数")
    print("  GET /api/tables - 餐桌占用数据")
    print("  GET /api/statistics - 食堂统计数据")
    print("  GET /api/menu - 今日菜单")
    app.run(host='0.0.0.0', port=8888, debug=True)
