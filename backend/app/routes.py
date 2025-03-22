import base64
import os

import weaviate
import tempfile
from flask import Blueprint, request, jsonify, render_template, Flask, send_from_directory, abort
from werkzeug.security import safe_join

#from app.services.geo import search_nearby, create_map, initialize_database, save_map
#from app.services.file_service import insert_file_into_collection
from app.services.chat_service import retrieve_media, generate_response_multimodal_ollama, file_to_base64
from flask_cors import CORS

from app.services.new_geo_map import create_geo_map, save_geo_map, create_empty_map
from app.services.new_file_service import insert_file
from app.services.new_geo import new_search_nearby

app = Flask(__name__)
api_bp = Blueprint('api', __name__)
CORS(api_bp)
'''
@api_bp.route('/upload', methods=['POST'])
def upload():
    try:
        file = request.files.get('file')
        if not file:
            return jsonify({"status": "error", "message": "No file part in the request"}), 400

        collection_name = request.form.get('collection_name')
        if not collection_name:
            return jsonify({"status": "error", "message": "No collection name provided"}), 400

        insert_file_into_collection(file, collection_name)

        return jsonify({
            "status": "success",
            "message": f"File '{file.filename}' successfully inserted into collection '{collection_name}'."
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
'''
# @api_bp.route('/chat', methods=['POST'])
# def chat():
#     data = request.get_json()
#     query = data.get('query')
#     collection_name = data.get('collection_name', None)
#
#     if not query:
#         return jsonify({"error": "Please provide a query."}), 400
#
#     try:
#         files = retrieve_media(query, collection_name)
#         response = generate_response_multimodal_ollama(query, files)
#         images = []
#
#         for file in files:
#             if file.get('mediaType') == "image":
#                 if 'image' in file and file['image']:  # Base64 形式
#                     images.append(f"data:image/jpeg;base64,{file['image']}")
#
#         return jsonify({"response": response, "images": images}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# chat_histories = {}
# @api_bp.route('/chat', methods=['POST'])
# def chat():
#
#     data = request.get_json()
#
#     query = data.get('query')
#     collection_name = data.get('collection_name', None)
#     retrieve = data.get('retrieve', False)
#     session_id = data.get('session_id', 'default')
#
#     if not query:
#         return jsonify({"error": "Please provide a query."}), 400
#
#     if session_id not in chat_histories:
#         chat_histories[session_id] = []
#
#     try:
#         files = retrieve_media(query, collection_name) if retrieve else []
#
#         chat_histories[session_id].append({"role": "user", "content": query})
#         response = generate_response_multimodal_ollama(query, files, chat_histories[session_id])
#
#         chat_histories[session_id].append({"role": "assistant", "content": response})
#
#         images = [
#             f"data:image/jpeg;base64,{file['image']}"
#             for file in files if file.get('mediaType') == "image" and 'image' in file and file['image']
#         ]
#
#         return jsonify({
#             "response": response,
#             "images": images,
#             "session_id": session_id
#         }), 200
#
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

chat_histories = {}
import whisper
# 使用 Whisper 模型进行音频转录
def transcribe_audio(base64_audio):
    # 将 base64 字符串解码并写入临时文件
    audio_bytes = base64.b64decode(base64_audio)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(audio_bytes)
        temp_filename = temp_audio.name

    # 加载模型并转录（这里只演示使用 "small" 模型）
    model = whisper.load_model("small")
    options = dict(task="translate", best_of=1, language='en')
    result = model.transcribe(temp_filename, **options)
    transcript = result.get("text", "").strip()

    # 删除临时文件
    os.remove(temp_filename)
    print("Audio Transcript:",transcript)
    return transcript

@api_bp.route('/chat', methods=['POST'])
def chat():
    # data = request.get_json()
    # query = data.get('query')
    # collection_name = data.get('collection_name', None)
    # retrieve = data.get('retrieve', False)
    # session_id = data.get('session_id', 'default')
    query = request.form.get('query')
    collection_name = request.form.get('collection_name')
    retrieve = request.form.get('retrieve')
    session_id = request.form.get('session_id', 'default')
    # 新增：接收上传的文件（例如通过 multipart/form-data 时可通过 request.files 获取）
    uploaded_file = None
    if 'uploaded_file' in request.files:
        uploaded_file = request.files['uploaded_file']

    if not query:
        return jsonify({"error": "Please provide a query."}), 400

    if session_id not in chat_histories:
        chat_histories[session_id] = []

    try:
        files = retrieve_media(query, uploaded_file, collection_name) if retrieve=='true' else []

        # # 针对检索到的文件进行预处理
        # # 若存在 audio 类型文件，则利用 whisper 转录，并将 transcript 加入 query（标明为音频转录）
        # audio_transcripts = []
        # for file in files:
        #     if file.get("mediaType") == "audio" and file.get("audio"):
        #         transcript = transcribe_audio(file["audio"])
        #         if transcript:
        #             audio_transcripts.append(transcript)

        # 处理 audio 文件，获取原始音频和转录文本
        audios = []
        audio_transcripts = []
        for file in files:
            if file.get("mediaType") == "audio":
                # 尝试直接使用 file 中已有的 audio 字段，否则从文件路径读取
                audio_data = file.get("audio")
                if not audio_data and file.get("path") and os.path.exists(file["path"]):
                    audio_data = file_to_base64(file["path"])
                if audio_data:
                    transcript = transcribe_audio(audio_data)
                    if transcript:
                        audio_transcripts.append(transcript)
                    audios.append({
                        "audio": "data:audio/wav;base64," + audio_data,
                        "transcript": transcript if transcript else ""
                    })

        # 若有音频转录结果，将其追加到原始 query 中
        if audio_transcripts:
            query += "\n\n[Audio transcript(s): " + " ".join(audio_transcripts) + "]"

        # 更新对话历史，加入用户输入（后续传给 ollama 的 chat 会包含历史信息）
        chat_histories[session_id].append({"role": "user", "content": query})

        response = generate_response_multimodal_ollama(query, files, chat_histories[session_id])
        chat_histories[session_id].append({"role": "assistant", "content": response})

        # 对 image 类型的文件构造返回的图片数据
        images = [
            f"data:image/jpeg;base64,{file['image']}"
            for file in files if file.get('mediaType') == "image" and file.get('image')
        ]

        return jsonify({
            "response": response,
            "images": images,
            "audios": audios,
            "session_id": session_id
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

'''
@api_bp.route('/geo_search', methods=['GET'])
def geo_search():
    initialize_database()
    try:
        address = request.args.get('address')
        radius = float(request.args.get('radius', 2))  # 默认半径为 2 公里
        keyword = request.args.get('keyword', None)

        if not address:
            return jsonify({"error": "Please provide an address."}), 400

        # 搜索附近数据
        results = search_nearby(keyword, address=address, radius_km=radius)

        # 创建交互式地图
        map_obj = create_map(address=address, radius_km=radius, results=results)

        # 保存地图
        save_map(map_obj)

        # 返回 HTML 地图
        return render_template("interactive_map.html")
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
'''

@api_bp.route('/collections', methods=['GET'])
def get_collections():
    client = weaviate.connect_to_local()
    try:
        collections = client.collections.list_all()
        collection_names = list(collections.keys())
        client.close()
        return jsonify({"collections": collection_names}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/new_upload', methods=['POST'])
def new_upload():
    try:
        file = request.files.get('file')
        if not file:
            return jsonify({"status": "error", "message": "No file part in the request"}), 400

        collection_name = request.form.get('collection_name')
        if not collection_name:
            return jsonify({"status": "error", "message": "No collection name provided"}), 400

        description = request.form.get('description')
        address = request.form.get('address', None)
        latitude = request.form.get('latitude', None)
        longitude = request.form.get('longitude', None)

        if latitude and longitude:
            latitude = float(latitude)
            longitude = float(longitude)

        insert_file(file, collection_name, description, address, latitude, longitude)

        return jsonify({
            "status": "success",
            "message": f"File '{file.filename}' successfully inserted into collection '{collection_name}'."
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

# 搜索附近数据接口
@api_bp.route('/new_geo_search', methods=['GET'])
def new_geo_search():
    collection_name = request.args.get('collection_name')
    address = request.args.get('address', None)
    radius = float(request.args.get('radius'))
    keyword = request.args.get('keyword', None)
    latitude = request.args.get('latitude', None)
    longitude = request.args.get('longitude', None)

    if not collection_name:
        return jsonify({"error": "Please provide a collection name."}), 400

    if latitude and longitude:
        latitude = float(latitude)
        longitude = float(longitude)

    results = new_search_nearby(collection_name, keyword, latitude, longitude, address, radius)

    if "error" in results:
        return jsonify({"error": results["error"]}), 400

    return jsonify({"results": results["results"]}), 200


@api_bp.route('/geo_map', methods=['GET'])
def geo_map():
    collection_name = request.args.get('collection_name')
    address = request.args.get('address', None)
    radius = float(request.args.get('radius', 2))
    keyword = request.args.get('keyword', None)
    latitude = request.args.get('latitude', None)
    longitude = request.args.get('longitude', None)

    if not collection_name:
        return jsonify({"error": "Please provide a collection name."}), 400

    if latitude and longitude:
        latitude = float(latitude)
        longitude = float(longitude)

    # 获取搜索结果
    results_data = new_search_nearby(collection_name, keyword, latitude, longitude, address, radius)

    if "error" in results_data:
        return jsonify({"error": results_data["error"]}), 400

    results = results_data["results"]

    # 生成地图，即使没有找到数据，也要显示一个空白地图
    if not results:
        print("🔍 No results found. Generating empty map...")  # Debug Log
        map_obj = create_empty_map(latitude, longitude, address, radius)
    else:
        print(f"📍 Found {len(results)} results. Generating map...")  # Debug Log
        map_obj = create_geo_map(results, latitude, longitude, address, radius_km=radius)

    map_file = save_geo_map(map_obj)

    # 返回 HTML 地图
    return render_template("geo_map.html")


UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')

@api_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    file_path = safe_join(UPLOAD_FOLDER, filename)
    if not os.path.isfile(file_path):
        abort(404)
    return send_from_directory(UPLOAD_FOLDER, filename)

