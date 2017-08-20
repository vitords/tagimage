import flask
import json
import requests

import tensorflow as tf
from tag_image import tag_image, download_model_if_necessary


IMG_DIR = 'data/img/'

app = flask.Flask(__name__)

# Start a persistent TensorFlow session
tf_session = tf.Session()


@app.route('/tag', methods=['POST'])
def tag():
    """Image classifier API endpoint.

    Returns:
        JSON object with the image URL and the tags assigned to the image.
    """
    img_url = flask.request.form['url']
    filename = img_url.split('/')[-1]

    # Save the image to the image directory
    with open(IMG_DIR + filename, 'wb') as img:
        img.write(requests.get(img_url).content)

    # Use the trained TensorFlow model to classify the image
    tags = tag_image(tf_session, IMG_DIR + filename)
    # Create the tags dictionary
    tags = {'tag' + str(key): value for (key, value) in enumerate(tags)}

    return json.dumps({'image_url': img_url, 'tags': tags})


if __name__ == '__main__':
    # If there is no TensorFlow model, download it and set it up
    download_model_if_necessary()
    app.run()
