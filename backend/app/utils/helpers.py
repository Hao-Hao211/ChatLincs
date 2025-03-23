'''

import base64


# Helper function to convert a file to base64 representation
def toBase64(path):
    with open(path, 'rb') as file:
        return base64.b64encode(file.read()).decode('utf-8')

'''

# Helper functions to display results
import json
from IPython.display import Image, Audio, Video

def json_print(data):
    print(json.dumps(data, indent=2))

'''

import base64, requests

# Helper function – get base64 representation from an online image
def url_to_base64(url):
    image_response = requests.get(url)
    content = image_response.content
    return base64.b64encode(content).decode('utf-8')

# Helper function - get base64 representation from a local file
def file_to_base64(path):
    with open(path, 'rb') as file:
        return base64.b64encode(file.read()).decode('utf-8')

# Update the url and path to test
#test_image_base64 = url_to_base64("https://path-to-some-online-image.jpg")
#test_file_base64 = file_to_base64("./test/meerkat.jpeg")
'''