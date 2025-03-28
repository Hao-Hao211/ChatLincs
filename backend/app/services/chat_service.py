import base64

import requests
import os
from dotenv import load_dotenv, find_dotenv
import weaviate

from app.utils.helpers import json_print

import json
import weaviate.classes.query as wq

# Helper function - get base64 representation from a local file
def file_to_base64(path):
    with open(path, 'rb') as file:
        return base64.b64encode(file.read()).decode('utf-8')

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

