import base64

import requests
import os
from dotenv import load_dotenv, find_dotenv
import weaviate

from app.utils.helpers import json_print

# client = weaviate.connect_to_local()

# load_dotenv()
#
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

import json
import weaviate.classes.query as wq

# Helper function - get base64 representation from a local file
def file_to_base64(path):
    with open(path, 'rb') as file:
        return base64.b64encode(file.read()).decode('utf-8')

# def retrieve_media(query, collection_name=None):
#     """
#     Retrieve media from the Weaviate database based on the query.
#
#     Parameters:
#         query (str): The query string, URL, or path to the query media.
#         collection_name (str): Optional. Target a specific collection. If None, search all collections.
#
#     Returns:
#         List of dictionaries with retrieved media items and their collection names.
#     """
#     client = weaviate.connect_to_local()
#     # Determine query type and prepare the query
#     if isinstance(query, str):
#         if query.startswith('http'):  # URL-based media
#             query_base64 = url_to_base64(query)
#             query_type = "near_image"
#         elif query.endswith(('.jpg', '.jpeg', '.png')):  # File-based image
#             query_base64 = file_to_base64(query)
#             query_type = "near_image"
#         elif query.endswith(('.mp4', '.avi', '.mov')):  # File-based video
#             query_base64 = file_to_base64(query)
#             query_type = "near_media"
#             media_type = "VIDEO"
#         elif query.endswith(('.wav', '.mp3', '.aac')):  # File-based audio
#             query_base64 = file_to_base64(query)
#             query_type = "near_media"
#             media_type = "AUDIO"
#         else:  # Text query
#             query_base64 = None
#             query_type = "near_text"
#     else:
#         raise ValueError("Unsupported query type. Provide a valid text, file path, or URL.")
#
#     # Get collections to search in
#     if collection_name:
#         collections = [(collection_name, client.collections.get(collection_name))]
#     else:
#         collections = [(name, client.collections.get(name)) for name in client.collections.list_all()]
#
#     results = []
#
#     # Query each collection
#     for collection_name, collection in collections:
#
#         schema = client.collections.export_config(collection_name)
#         available_properties = [prop.name for prop in schema.properties]
#         return_properties = [prop for prop in ['name', 'path', 'mediaType', 'collection', 'image', 'audio', 'video'] if prop in available_properties]
#
#         if query_type == "near_text":
#             response = collection.query.near_text(
#                 query=query,
#                 return_properties=return_properties,
#                 limit=1
#             )
#         elif query_type == "near_image":
#             response = collection.query.near_image(
#                 near_image=query_base64,
#                 return_properties=return_properties,
#                 limit=1
#             )
#         elif query_type == "near_media":
#             response = collection.query.near_media(
#                 media=query_base64,
#                 media_type=getattr(wq.NearMediaType, media_type),
#                 return_properties=return_properties,
#                 limit=1
#             )
#         else:
#             continue
#
#         # Process response
#         for obj in response.objects:
#             item = obj.properties
#             json_print(item)
#             # display_media(item)
#             results.append(item)
#
#     client.close()
#     return results

# # Load API key from .env file
# _ = load_dotenv(find_dotenv())
# openai_api_key = os.getenv("OPENAI_API_KEY")
#
# def generate_response_multimodal(query, files):
#     """
#     Generate a description based on a query and retrieved files using GPT-4o app capabilities.
#
#     Parameters:
#         query (str): The query used to retrieve the media files.
#         files (list): A list of dictionaries representing retrieved media files.
#
#     Returns:
#         str: A generated description from GPT-4o.
#     """
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {openai_api_key}"
#     }
#
#     # Prepare media inputs
#     media_inputs = []
#     for file in files:
#         if file['mediaType'] == 'image':  # Handle image files
#             media_inputs.append({
#                 "type": "image_url",
#                 "image_url": {"url": f"data:image/jpeg;base64,{file['image']}"}
#             })
#         elif file['mediaType'] == 'audio':  # Handle audio files
#             media_inputs.append({
#                 "type": "audio_url",
#                 "audio_url": {"url": f"data:audio/wav;base64,{file['audio']}"}
#             })
#         elif file['mediaType'] == 'video':  # Handle video files
#             media_inputs.append({
#                 "type": "video_url",
#                 "video_url": {"url": f"data:video/mp4;base64,{file['video']}"}
#             })
#
#     # Construct the payload with query and media
#     messages = [
#         {
#             "role": "user",
#             "content": [
#                 {"type": "text", "text": query}
#             ]
#         }
#     ]
#
#     # Add each media input to the content of the first user message
#     if media_inputs:
#         messages[0]["content"].extend(media_inputs)
#
#     payload = {
#         "model": "gpt-4o",
#         "messages": messages,
#         "max_tokens": 300
#     }
#
#     print("Payload: " + str(payload))  # Debugging
#
#     # Send the request
#     try:
#         response = requests.post(
#             "https://api.openai.com/v1/chat/completions",
#             headers=headers,
#             json=payload
#         )
#         response.raise_for_status()
#         result = response.json()['choices'][0]['message']['content']
#         print(f"Response: {result}")
#         return result
#
#     except requests.exceptions.RequestException as e:
#         print(f"An error occurred while communicating with the GPT-4 API: {e}")
#         return f"An error occurred: {e}"

def fileobj_to_base64(file_obj):
    file_obj.seek(0)
    data = file_obj.read()
    file_obj.seek(0)
    return base64.b64encode(data).decode('utf-8')

def retrieve_media(query, uploaded_file=None, collection_name=None):

    client = weaviate.connect_to_local()

    if collection_name:
        collections = [(collection_name, client.collections.get(collection_name))]
    else:
        collections = [(name, client.collections.get(name)) for name in client.collections.list_all()]

    results = []

    file_base64 = None
    file_query_type = None
    media_type = None
    if uploaded_file:
        filename = uploaded_file.filename.lower()
        file_base64 = fileobj_to_base64(uploaded_file)
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            file_query_type = "near_image"
        elif filename.endswith(('.mp4', '.avi', '.mov')):
            file_query_type = "near_media"
            media_type = "VIDEO"
        elif filename.endswith(('.wav', '.mp3', '.aac')):
            file_query_type = "near_media"
            media_type = "AUDIO"
        else:
            file_query_type = None

    for coll_name, collection in collections:
        schema = client.collections.export_config(coll_name)
        available_properties = [prop.name for prop in schema.properties]
        return_properties = [prop for prop in ['name', 'path', 'mediaType', 'collection', 'image', 'audio', 'video'] if prop in available_properties]

        if file_base64 and file_query_type:
            if file_query_type == "near_image":
                response_file = collection.query.near_image(
                    near_image=file_base64,
                    return_properties=return_properties,
                    limit=1
                )
            elif file_query_type == "near_media":
                response_file = collection.query.near_media(
                    media=file_base64,
                    media_type=getattr(wq.NearMediaType, media_type),
                    return_properties=return_properties,
                    limit=1
                )
            else:
                response_file = None

            if response_file:
                for obj in response_file.objects:
                    item = obj.properties
                    json_print(item)
                    results.append(item)

        elif query:
            response_text = collection.query.near_text(
                query=query,
                return_properties=return_properties,
                limit=1
            )
            for obj in response_text.objects:
                item = obj.properties
                json_print(item)
                results.append(item)

    client.close()
    return results

import ollama
import base64
import requests

# def generate_response_multimodal_ollama(query, files):
#     """
#     Generate a description based on a query and retrieved files using Ollama.
#
#     Parameters:
#         query (str): The query used to retrieve the media files.
#         files (list): A list of dictionaries representing retrieved media files.
#
#     Returns:
#         str: A generated description from Ollama.
#     """
#     # Prepare media inputs
#     media_inputs = []
#     for file in files:
#         if file['mediaType'] == 'image':  # Handle image files
#             media_inputs.append(file['image'])  # Assuming base64 string
#         elif file['mediaType'] == 'audio':  # Handle audio files
#             media_inputs.append(file['audio'])  # Assuming base64 string
#         elif file['mediaType'] == 'video':  # Handle video files
#             media_inputs.append(file['video'])  # Assuming base64 string
#
#     response = ollama.chat(
#         model='llava:7b',
#         messages=[{
#             'role': 'user',
#             'content': query,
#             'images':media_inputs
#         }]
#     )
#     return response.message['content']

def generate_response_multimodal_ollama(query, files, chat_history):
    media_inputs = []

    for file in files:
        if file['mediaType'] == 'image' and 'image' in file:
            media_inputs.append(file['image'])
        # elif file['mediaType'] == 'audio' and 'audio' in file:
        #     media_inputs.append(file['audio'])
        # elif file['mediaType'] == 'video' and 'video' in file:
        #     media_inputs.append(file['video'])

    messages = chat_history.copy()
    messages.append({"role": "user", "content": query, "images": media_inputs if media_inputs else None})  # 追加用户输入

    response = ollama.chat(
        model='llava:7b',
        messages=messages
    )
    return response.message['content']

