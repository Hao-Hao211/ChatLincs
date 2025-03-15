import os
import folium
from folium.plugins import MarkerCluster
from flask import current_app, url_for
from geopy import Nominatim


def create_geo_map(results, center_lat=None, center_lon=None, address=None, radius_km=2):
    """
    通过 new_geo_search 结果创建交互式地图
    :param results: 从 new_geo_search 获取的 JSON 数据
    :param center_lat: 中心纬度
    :param center_lon: 中心经度
    :param radius_km: 显示的搜索半径
    :return: folium Map 对象
    """
    if not results:
        raise ValueError("无有效的地图数据")

    geolocator = Nominatim(user_agent="geo_app")
    if address:
        location = geolocator.geocode(address)
        if location:
            center_lat, center_lon = location.latitude, location.longitude
        else:
            raise ValueError(f"无法找到地址: {address}")

    # if center_lat is None or center_lon is None:
    #     center_lat, center_lon = results[0]['latitude'], results[0]['longitude']

    m = folium.Map(location=[center_lat, center_lon], zoom_start=14)

    folium.Circle(
        radius=radius_km * 1000,
        location=[center_lat, center_lon],
        color="blue",
        fill=True,
        fill_opacity=0.1,
        popup=f"Search radius：{radius_km} km"
    ).add_to(m)

    marker_cluster = MarkerCluster().add_to(m)
    for data in results:
        # 修正: 使用 `api.uploaded_file` 生成文件 URL
        file_url = url_for('api.uploaded_file', filename=os.path.basename(data["file_path"]), _external=True)

        popup_content = f"""
        <b>Description：</b> {data['description']}<br>
        <b>Address：</b> {data['address']}<br>
        <b>Distance：</b> {data['distance_km']:.2f} km
        """

        # 根据文件类型添加图片、视频或音频
        if data['file_path'].lower().endswith(('jpg', 'jpeg', 'png')):
            popup_content += f'<br><img src="{file_url}" width="150">'
        elif data['file_path'].lower().endswith(('mp4', 'webm', 'ogg')):
            popup_content += f'<br><video controls width="200"><source src="{file_url}" type="video/mp4"></video>'
        elif data['file_path'].lower().endswith(('mp3', 'wav', 'ogg')):
            popup_content += f'<br><audio controls><source src="{file_url}" type="audio/mpeg"></audio>'

        folium.Marker(
            location=[data['latitude'], data['longitude']],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=f"Click for details ({data['distance_km']:.2f} km)"
        ).add_to(marker_cluster)

    return m

def save_geo_map(map_obj, filename="geo_map.html"):
    """
    保存地图到 templates 目录
    :param map_obj: folium Map 对象
    :param filename: 保存的 HTML 文件名
    :return: 文件路径
    """
    map_path = os.path.join(current_app.root_path, "templates", filename)
    os.makedirs(os.path.dirname(map_path), exist_ok=True)
    map_obj.save(map_path)
    return map_path

def create_empty_map(center_lat=None, center_lon=None, address=None, radius_km=2):

    geolocator = Nominatim(user_agent="geo_app")
    if address:
        location = geolocator.geocode(address)
        if location:
            center_lat, center_lon = location.latitude, location.longitude
        else:
            raise ValueError(f"无法找到地址: {address}")

    m = folium.Map(location=[center_lat, center_lon], zoom_start=14)

    # 画出搜索范围
    folium.Circle(
        radius=radius_km * 1000,
        location=[center_lat, center_lon],
        color="gray",
        fill=True,
        fill_opacity=0.1,
        popup=f"Search radius：{radius_km} km (No data found)"
    ).add_to(m)

    return m

