import base64
import os
import time
from pathlib import Path

import weaviate
import tempfile
from flask import Blueprint, request, jsonify, render_template, Flask, send_from_directory, abort
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough
from moviepy import VideoFileClip
from werkzeug.security import safe_join
from os import path as osp
import lancedb

#from app.services.geo import search_nearby, create_map, initialize_database, save_map
#from app.services.file_service import insert_file_into_collection
from app.services.chat_service import retrieve_media, generate_response_multimodal_ollama, file_to_base64
from flask_cors import CORS

from app.services.new_geo_map import create_geo_map, save_geo_map, create_empty_map
from app.services.new_file_service import insert_file
from app.services.new_geo import new_search_nearby

from app.services.video import video_service

from app.services.video.video_service import getSubs

from app.services.video.video_service import extract_and_save_frames_and_metadata

from app.services.video.video_service import extract_and_save_frames_and_metadata_with_fps

from app.services.video.video_service import load_json_file

from app.services.video.video_rag.embeddings.bridgetower_embeddings import BridgeTowerEmbeddings
from app.services.video.video_rag.vectorstores.multimodal_lancedb import MultimodalLanceDB

from app.services.video.video_service import get_youtube_title

from app.services.video.video_service import clean_table_name

from app.services.video.video_service import prompt_processing

from app.services.video.video_rag.MLM.client import LocalLLMClient

from app.services.video.video_rag.MLM.lvlm import LVLM

from app.services.video.video_service import encode_image_to_base64

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

        insert_file(file, collection_name)

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

def transcribe_audio(base64_audio):

    audio_bytes = base64.b64decode(base64_audio)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(audio_bytes)
        temp_filename = temp_audio.name

    model = whisper.load_model("small")
    options = dict(task="translate", best_of=1, language='en')
    result = model.transcribe(temp_filename, **options)
    transcript = result.get("text", "").strip()

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

    uploaded_file = None
    if 'uploaded_file' in request.files:
        uploaded_file = request.files['uploaded_file']

    if not query:
        return jsonify({"error": "Please provide a query."}), 400

    if session_id not in chat_histories:
        chat_histories[session_id] = []

    try:
        files = retrieve_media(query, uploaded_file, collection_name) if retrieve=='true' else []
        # audio_transcripts = []
        # for file in files:
        #     if file.get("mediaType") == "audio" and file.get("audio"):
        #         transcript = transcribe_audio(file["audio"])
        #         if transcript:
        #             audio_transcripts.append(transcript)
        audios = []
        audio_transcripts = []
        for file in files:
            if file.get("mediaType") == "audio":
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

        if audio_transcripts:
            query += "\n\n[Audio transcript(s): " + " ".join(audio_transcripts) + "]"

        chat_histories[session_id].append({"role": "user", "content": query})

        response = generate_response_multimodal_ollama(query, files, chat_histories[session_id])
        chat_histories[session_id].append({"role": "assistant", "content": response})

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

        results = search_nearby(keyword, address=address, radius_km=radius)

        map_obj = create_map(address=address, radius_km=radius, results=results)

        save_map(map_obj)

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
'''

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

    results_data = new_search_nearby(collection_name, keyword, latitude, longitude, address, radius)

    if "error" in results_data:
        return jsonify({"error": results_data["error"]}), 400

    results = results_data["results"]

    if not results:
        print("🔍 No results found. Generating empty map...")  # Debug Log
        map_obj = create_empty_map(latitude, longitude, address, radius)
    else:
        print(f"📍 Found {len(results)} results. Generating map...")  # Debug Log
        map_obj = create_geo_map(results, latitude, longitude, address, radius_km=radius)

    map_file = save_geo_map(map_obj)

    return render_template("geo_map.html")


UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')

@api_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    file_path = safe_join(UPLOAD_FOLDER, filename)
    if not os.path.isfile(file_path):
        abort(404)
    return send_from_directory(UPLOAD_FOLDER, filename)


@api_bp.route('/upload_video', methods=['POST'])
def upload_video():
    video_without_language_sound = request.form.get('video_without_language_sound', "false")
    video_url = request.form.get('video_url')
    video_title = get_youtube_title(video_url)
    video_dir = f'./shared_data/videos/{clean_table_name(video_title)}'

    video_filepath = video_service.download_video(video_url, video_dir)
    video_transcript_filepath = video_service.get_transcript_vtt(video_url, video_dir)

    if video_without_language_sound == "true":
        print("=================A==============")
        extracted_frames_path = osp.join(video_dir, 'extracted_frame')
        metadatas_path = video_dir
        Path(extracted_frames_path).mkdir(parents=True, exist_ok=True)
        Path(metadatas_path).mkdir(parents=True, exist_ok=True)
        metadatas = extract_and_save_frames_and_metadata_with_fps(
            video_filepath,
            extracted_frames_path,
            metadatas_path,
            num_of_extracted_frames_per_second=1
        )

    elif video_transcript_filepath is not None:
        print("=================B==============")
        extracted_frames_path = osp.join(video_dir, 'extracted_frame')
        metadatas_path = video_dir
        Path(extracted_frames_path).mkdir(parents=True, exist_ok=True)
        Path(metadatas_path).mkdir(parents=True, exist_ok=True)
        # call the function to extract frames and metadatas
        metadatas = extract_and_save_frames_and_metadata(
            video_filepath,
            video_transcript_filepath,
            extracted_frames_path,
            metadatas_path,
        )

    else:
        print("=================C==============")
        video_no_transcript = video_filepath
        extracted_audio_file = os.path.join(video_dir, 'audio.mp3')
        clip = VideoFileClip(video_no_transcript)
        clip.audio.write_audiofile(extracted_audio_file)
        model = whisper.load_model("small")
        options = dict(task="translate", best_of=1, language='en')
        results = model.transcribe(extracted_audio_file, **options)
        vtt = getSubs(results["segments"], "vtt")
        generated_trans = osp.join(video_dir, 'generated_transcript.vtt')
        with open(generated_trans, 'w') as f:
            f.write(vtt)
        extracted_frames_path = osp.join(video_dir, 'extracted_frame')
        metadatas_path = video_dir
        Path(extracted_frames_path).mkdir(parents=True, exist_ok=True)
        Path(metadatas_path).mkdir(parents=True, exist_ok=True)
        # call the function to extract frames and metadatas
        metadatas = extract_and_save_frames_and_metadata(
            video_filepath,
            generated_trans,
            extracted_frames_path,
            metadatas_path,
        )

    # declare host file
    LANCEDB_HOST_FILE = "./shared_data/.lancedb"
    # declare table name
    TBL_NAME = f"tbl_{clean_table_name(video_title)}"
    # initialize vectorstore
    db = lancedb.connect(LANCEDB_HOST_FILE)

    video_metadata_path = f'{video_dir}/metadatas.json'

    video_metadata = load_json_file(video_metadata_path)
    video_trans = [vid['transcript'] for vid in video_metadata]
    video_img_path = [vid['extracted_frame_path'] for vid in video_metadata]

    # Transcript Augmentation (n is number of neighboring frames)
    """
    - It is advised that we should pick an individual n for each video such that the updated transcripts say one or two meaningful facts.
    - Changing the transcriptions which will be ingested into vector store along with their corresponding frames will affect directly the performance. It is advised that one needs to do diligent to experiment with one's data to get the best performance.
    """
    n = int(request.form.get('n',6))
    updated_video_trans = [
        ' '.join(video_trans[i - int(n / 2): i + int(n / 2)]) if i - int(n / 2) >= 0 else
        ' '.join(video_trans[0: i + int(n / 2)]) for i in range(len(video_trans))
    ]
    # also need to update the updated transcripts in metadata
    for i in range(len(updated_video_trans)):
        video_metadata[i]['transcript'] = updated_video_trans[i]
    # Ingest data into lanceDB
    # initialize an BridgeTower embedder
    embedder = BridgeTowerEmbeddings()

    _ = MultimodalLanceDB.from_text_image_pairs(
        texts=updated_video_trans,
        image_paths=video_img_path,
        embedding=embedder,
        metadatas=video_metadata,
        connection=db,
        table_name=TBL_NAME,
        mode="overwrite",
    )

    return jsonify({"status": "success", "video_path": video_filepath})

@api_bp.route('/all_uploaded_videos', methods=['GET'])
def all_uploaded_videos():
    LANCEDB_HOST_FILE = "./shared_data/.lancedb"
    db = lancedb.connect(LANCEDB_HOST_FILE)

    table_names = db.table_names()
    video_titles = []

    for tbl in table_names:
        if tbl.startswith("tbl_"):
            raw_title = tbl[4:].replace('_', ' ')
            video_titles.append(raw_title)

    return jsonify({"video_titles": video_titles})

@api_bp.route('/chat_with_video', methods=['POST'])
def chat_with_video():
    video_title = request.form.get('video_title')
    query = request.form.get('query')

    if not query or not video_title:
        return jsonify({"error": "Missing 'query' or 'video_title'"}), 400

    LANCEDB_HOST_FILE = "./shared_data/.lancedb"
    TBL_NAME = f"tbl_{clean_table_name(video_title)}"

    # initialize an BridgeTower embedder
    embedder = BridgeTowerEmbeddings()
    prompt_processing_module = RunnableLambda(prompt_processing)

    ## Creating a LanceDB vector store
    vectorstore = MultimodalLanceDB(
        uri=LANCEDB_HOST_FILE,
        embedding=embedder,
        table_name=TBL_NAME
    )

    ### Creating a retriever for the vector store
    retriever_module = vectorstore.as_retriever(
        search_type='similarity',
        search_kwargs={"k": 1}
    )

    client = LocalLLMClient()
    lvlm_inference_module = LVLM(client=client)

    # the output of this new chain is a dictionary
    video_rag_chain_with_retrieved_image = (
            RunnableParallel({
                "retrieved_results": retriever_module,
                "user_query": RunnablePassthrough()
            })
            | prompt_processing_module
            | RunnableParallel({
        'final_text_output': lvlm_inference_module,
        'input_to_lvlm': RunnablePassthrough()
    })
    )

    response = video_rag_chain_with_retrieved_image.invoke(query)
    image_path = response['input_to_lvlm'].get('image')
    image_base64 = encode_image_to_base64(image_path)

    return jsonify({"response": response['final_text_output'], "image": response['input_to_lvlm']['image'], "image_base64": image_base64})