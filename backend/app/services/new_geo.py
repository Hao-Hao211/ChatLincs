import os
import sqlite3
from geopy.geocoders import Nominatim
from geopy.distance import geodesic


# 初始化数据库（每个 collection 独立）
def new_initialize_database(collection_name):
    db_path = f'./databases/{collection_name}.db'
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL,
            description TEXT,
            address TEXT,
            latitude REAL,
            longitude REAL
        )
    ''')
    conn.commit()
    conn.close()


# 搜索范围内的数据
def new_search_nearby(collection_name, keyword=None, latitude=None, longitude=None, address=None, radius_km=None):
    db_path = f'./databases/{collection_name}.db'

    if not os.path.exists(db_path):
        return {"error": f"Collection '{collection_name}' does not exist."}

    geolocator = Nominatim(user_agent="geo_app")
    if address:
        location = geolocator.geocode(address)
        if location:
            latitude, longitude = location.latitude, location.longitude
        else:
            return {"error": f"无法找到地址: {address}"}

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM media')
    results = []

    for row in cursor.fetchall():
        file_id, file_path, description, address, lat, lon = row
        if lat is None or lon is None:
            continue

        distance = geodesic((latitude, longitude), (lat, lon)).km
        if distance <= radius_km and (keyword is None or keyword.lower() in description.lower()):
            results.append({
                'id': file_id,
                'file_path': file_path,
                'description': description,
                'address': address,
                'latitude': lat,
                'longitude': lon,
                'distance_km': distance
            })

    conn.close()
    return {"results": results}

if __name__ == "__main__":
    collection_name = "animal_test"  # 你可以更改为其他集合名称
    new_initialize_database(collection_name)  # 初始化数据库
    print(f"数据库 {collection_name} 已初始化。")

    # 直接进行搜索，示例：查找 2km 内的“sunset”相关数据
    result = new_search_nearby(collection_name, keyword="", address="The Regent's Park", radius_km=2)
    print("搜索结果：", result)
