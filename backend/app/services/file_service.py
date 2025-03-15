import os
import base64
import mimetypes
import weaviate, json
import weaviate.classes as wvc

# client = weaviate.connect_to_local()

def insert_file_into_collection(file, collection_name):
    """
    Insert a single file into a specified collection and save it locally.

    Parameters:
        file (File-like or str): Path to the file or file-like object (e.g., from Gradio uploads).
        collection_name (str): Name of the collection.
    """
    client = weaviate.connect_to_local()
    # Save uploaded file locally if it's a file-like object
    if hasattr(file, 'read'):  # File-like object from Gradio or web uploads
        file_path = f"./source/{file.filename}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Ensure directory exists
        with open(file_path, 'wb') as f:
            f.write(file.read())
    else:  # Assume it's a file path
        file_path = file

    # Determine file type automatically
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        raise ValueError(f"Unable to determine the MIME type of the file: {file_path}")

    if mime_type.startswith('image/'):
        file_type = "image"
        save_dir = "./source/image/"
    elif mime_type.startswith('audio/'):
        file_type = "audio"
        save_dir = "./source/audio/"
    elif mime_type.startswith('video/'):
        file_type = "video"
        save_dir = "./source/video/"
    else:
        raise ValueError(f"Unsupported file type for MIME type: {mime_type}")

    # Save the file into the appropriate local directory
    os.makedirs(save_dir, exist_ok=True)
    saved_path = os.path.join(save_dir, os.path.basename(file_path))
    if not os.path.exists(saved_path):  # Avoid overwriting existing files
        with open(file_path, 'rb') as src, open(saved_path, 'wb') as dest:
            dest.write(src.read())
    print(f"File saved locally at: {saved_path}")

    # Check if the collection exists; create it if it doesn't
    if not client.collections.exists(collection_name):
        client.collections.create(
            name=collection_name,
            vectorizer_config=wvc.config.Configure.Vectorizer.multi2vec_bind(
                audio_fields=["audio"],
                image_fields=["image"],
                video_fields=["video"],
            )
        )
        print(f"Collection '{collection_name}' created successfully.")

    # Helper function to convert a file to Base64
    def to_base64(path):
        with open(path, 'rb') as file:
            return base64.b64encode(file.read()).decode('utf-8')

    # Prepare file for insertion
    media_data = {
        "name": os.path.basename(saved_path),
        "path": saved_path,
        file_type: to_base64(saved_path),
        "mediaType": file_type,
        "collection": collection_name
    }

    # Insert the file into the collection
    print(f"Inserting {file_type} file: {media_data['name']} into collection '{collection_name}'.")
    collection = client.collections.get(collection_name)
    collection.data.insert(media_data)

    # Confirm insertion
    print(f"File '{media_data['name']}' successfully inserted into '{collection_name}'.")
    client.close()

if __name__ == '__main__':
    file_path = "../test/test-dog.jpg"
    collection_name = "new_animals"
    insert_file_into_collection(file_path, collection_name)