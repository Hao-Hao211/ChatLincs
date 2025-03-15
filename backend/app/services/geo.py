import os
import sqlite3
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import folium
from folium.plugins import MarkerCluster

# 初始化数据库
def initialize_database():
    conn = sqlite3.connect('../multimedia_data.db')
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

# 添加数据
def add_media(file_path, description, address=None, latitude=None, longitude=None):
    static_dir = "../static/"
    os.makedirs(static_dir, exist_ok=True)
    static_file_path = os.path.join(static_dir, os.path.basename(file_path))
    if not os.path.exists(static_file_path):
        with open(file_path, "rb") as src, open(static_file_path, "wb") as dst:
            dst.write(src.read())

    geolocator = Nominatim(user_agent="geo_app")
    if address:
        location = geolocator.geocode(address)
        if location:
            latitude, longitude = location.latitude, location.longitude
            print(f"地址解析成功: {address} -> 纬度: {latitude}, 经度: {longitude}")
        else:
            print(f"地址解析失败: {address}")
            raise ValueError(f"无法找到地址: {address}")

    conn = sqlite3.connect('../multimedia_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO media (file_path, description, address, latitude, longitude)
        VALUES (?, ?, ?, ?, ?)
    ''', (static_file_path, description, address, latitude, longitude))
    conn.commit()
    conn.close()

# 搜索范围内的数据
def search_nearby(keyword=None, latitude=None, longitude=None, address=None, radius_km=2):
    geolocator = Nominatim(user_agent="geo_app")
    if address:
        location = geolocator.geocode(address)
        if location:
            latitude, longitude = location.latitude, location.longitude
            print(f"搜索地址解析成功: {address} -> 纬度: {latitude}, 经度: {longitude}")
        else:
            print(f"搜索地址解析失败: {address}")
            raise ValueError(f"无法找到地址: {address}")

    conn = sqlite3.connect('../multimedia_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM media')
    results = []
    for row in cursor.fetchall():
        file_id, file_path, description, address, lat, lon = row
        if lat is None or lon is None:
            print(f"跳过数据: 缺少坐标 -> {description}")
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
    print(f"检索结果: {len(results)} 条记录符合条件")
    return results

# 创建交互式地图并保存
def create_map(center_lat=None, center_lon=None, address=None, radius_km=2, results=[]):
    geolocator = Nominatim(user_agent="geo_app")
    if address:
        location = geolocator.geocode(address)
        if location:
            center_lat, center_lon = location.latitude, location.longitude
        else:
            raise ValueError(f"无法找到地址: {address}")

    m = folium.Map(location=[center_lat, center_lon], zoom_start=14)

    # 添加搜索范围圆圈
    folium.Circle(
        radius=radius_km * 1000,  # 半径转换为米
        location=[center_lat, center_lon],
        color="blue",
        fill=True,
        fill_opacity=0.1,
        popup=f"Search radius：{radius_km} km"
    ).add_to(m)

    # 添加数据点标记
    marker_cluster = MarkerCluster().add_to(m)
    for data in results:
        popup_content = f"""
        <b>Description：</b> {data['description']}<br>
        <b>Address：</b> {data['address']}<br>
        <b>File Path：</b> {data['file_path']}<br>
        <b>Distance：</b> {data['distance_km']:.2f} km
        """
        if data['file_path'].lower().endswith(('jpg', 'jpeg', 'png')):
            popup_content += f'<br><img src="{data["file_path"]}" width="100">'
        elif data['file_path'].lower().endswith(('mp4', 'webm', 'ogg')):
            popup_content += f'<br><video controls width="200"><source src="{data["file_path"]}" type="video/mp4">您的浏览器不支持视频播放。</video>'
        elif data['file_path'].lower().endswith(('mp3', 'wav', 'ogg')):
            popup_content += f'<br><audio controls><source src="{data["file_path"]}" type="audio/mpeg">您的浏览器不支持音频播放。</audio>'
        folium.Marker(
            location=[data['latitude'], data['longitude']],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=f"Click for details ({data['distance_km']:.2f} km)"
        ).add_to(marker_cluster)

    return m

def save_map(map_obj, filename="interactive_map.html"):
    from flask import current_app
    map_path = os.path.join(current_app.root_path, "templates", filename)
    os.makedirs(os.path.dirname(map_path), exist_ok=True)
    map_obj.save(map_path)
    return map_path

# 主程序入口
if __name__ == '__main__':
    initialize_database()

    # 示例：添加数据
    try:
        add_media("/Users/hao/Desktop/COMP0016/multimodal_v2/app/source/image/cat1.jpg", "A cute white cat", "The Regent's Park")
        add_media("/Users/hao/Desktop/COMP0016/multimodal_v2/app/source/image/meerkat1.jpg", "A meerkat","The Regent's Park")
        add_media("/Users/hao/Desktop/COMP0016/multimodal_v2/app/source/video/dog-high-five.mp4", "A video of dog high five", "University College London")
        add_media("/Users/hao/Desktop/COMP0016/multimodal_v2/app/source/audio/dog_audio.wav", "A sound of dogs", "Holborn")
    except ValueError as e:
        print(e)

    # 示例：搜索附近数据
    address = "Tottenham Court Road"  # 搜索地址
    radius = 3  # 搜索半径为2公里
    keyword = "dog"
    results = search_nearby(keyword, address=address, radius_km=radius)

    # 创建并保存地图
    map_obj = create_map(address=address, radius_km=radius, results=results)
    map_file = "../templates/interactive_map.html"
    map_obj.save(map_file)
    print("地图已保存为 interactive_map.html，可在浏览器中查看。")


