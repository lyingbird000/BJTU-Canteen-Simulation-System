#!/usr/bin/env python3
"""
数据库初始化脚本 - 创建SQLite数据库和表
"""

import sqlite3

# 创建数据库连接
conn = sqlite3.connect('canteen.db')
c = conn.cursor()

print("正在创建数据库表...")

# 创建窗口表
c.execute('''
    CREATE TABLE IF NOT EXISTS windows (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        queue_count INTEGER DEFAULT 0,
        wait_time TEXT DEFAULT '无需排队',
        status TEXT DEFAULT 'open',
        last_update TEXT
    )
''')

# 创建餐桌表
c.execute('''
    CREATE TABLE IF NOT EXISTS tables (
        id INTEGER PRIMARY KEY,
        is_occupied INTEGER DEFAULT 0,
        capacity INTEGER DEFAULT 4,
        current_people INTEGER DEFAULT 0,
        last_update TEXT
    )
''')

# 创建菜单表
c.execute('''
    CREATE TABLE IF NOT EXISTS menu (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        price INTEGER NOT NULL,
        rating REAL DEFAULT 0,
        sold INTEGER DEFAULT 0
    )
''')

# 创建食堂统计表
c.execute('''
    CREATE TABLE IF NOT EXISTS statistics (
        id INTEGER PRIMARY KEY,
        total_tables INTEGER DEFAULT 80,
        occupied_tables INTEGER DEFAULT 0,
        total_people INTEGER DEFAULT 0,
        avg_wait_time INTEGER DEFAULT 0,
        peak_time TEXT DEFAULT '12:00-12:30',
        update_time TEXT
    )
''')

# 插入窗口初始数据
windows_data = [
    (1, '大众快餐', '快餐', 5, '8min', 'open', '2024-01-01 00:00:00'),
    (2, '特色面食', '面食', 8, '10min', 'open', '2024-01-01 00:00:00'),
    (3, '麻辣烫', '火锅', 12, '15min', 'open', '2024-01-01 00:00:00'),
    (4, '轻食沙拉', '健康', 2, '无需排队', 'open', '2024-01-01 00:00:00'),
    (5, '川菜小炒', '川菜', 6, '9min', 'open', '2024-01-01 00:00:00'),
    (6, '粤菜精选', '粤菜', 4, '6min', 'open', '2024-01-01 00:00:00'),
    (7, '西北风味', '面食', 7, '8min', 'open', '2024-01-01 00:00:00'),
    (8, '清真美食', '清真', 3, '5min', 'open', '2024-01-01 00:00:00')
]

import random
for data in windows_data:
    c.execute('INSERT OR IGNORE INTO windows VALUES (?,?,?,?,?,?,?)', data)

# 插入餐桌初始数据
for i in range(1, 81):
    is_occupied = 1 if random.random() > 0.4 else 0
    current_people = random.randint(1, 4) if is_occupied else 0
    c.execute('INSERT OR IGNORE INTO tables VALUES (?,?,?,?,?)', 
              (i, is_occupied, 4, current_people, '2024-01-01 00:00:00'))

# 插入菜单初始数据
menu_data = [
    (1, '宫保鸡丁', 18, 4.8, 128),
    (2, '鱼香肉丝', 16, 4.6, 96),
    (3, '麻辣香锅', 22, 4.9, 156),
    (4, '番茄炒蛋', 12, 4.5, 89),
    (5, '红烧肉', 28, 4.7, 72),
    (6, '清蒸鲈鱼', 38, 4.8, 45),
    (7, '蒜蓉西兰花', 10, 4.4, 67),
    (8, '酸辣土豆丝', 8, 4.3, 112)
]

for data in menu_data:
    c.execute('INSERT OR IGNORE INTO menu VALUES (?,?,?,?,?)', data)

# 插入统计初始数据
c.execute('INSERT OR IGNORE INTO statistics VALUES (1, 80, 45, 90, 8, "12:00-12:30", "2024-01-01 00:00:00")')

conn.commit()
conn.close()

print("数据库初始化完成！")
print("生成的文件: canteen.db")