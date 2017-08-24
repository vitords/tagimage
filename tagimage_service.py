import os.path

import flask
import requests

from tag_image import ImageTagger, download_model_if_necessary

from get_youtube_data import get_youtube_data

from database import Database

import gmplot


IMG_DIR = 'data/img/'
if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

# If there is no TensorFlow model, download it and set it up
download_model_if_necessary()

app = flask.Flask(__name__)
db = Database()

it = ImageTagger()


# @app.route('/tag', methods=['POST'])
# def tag():
#     """Image classifier API endpoint.
#
#     Returns:
#         JSON object with the image URL and the tags assigned to the image.
#     """
#     img_url = flask.request.form['url']
#     filename = img_url.split('/')[-1]
#
#     # Save the image to the image directory
#     with open(IMG_DIR + filename, 'wb') as img:
#         img.write(requests.get(img_url).content)
#
#     # Use the trained TensorFlow model to classify the image
#     tags = it.tag_image(IMG_DIR + filename)
#     # Create the tags dictionary
#     tags = {'tag' + str(key): value for (key, value) in enumerate(tags)}
#
#     return json.dumps({'filename': filename, 'url': img_url, 'tags': tags})


@app.route('/search', methods=['POST'])
def search():
    """Search for YouTube videos and give tags to their thumbnail images."""
    # Get parameters from the request
    topic = flask.request.form['topic']
    max_videos = flask.request.form['max_videos']
    region = flask.request.form['region_code']
    key = flask.request.form['key']

    # Get YouTube video data and save it
    videos = get_youtube_data(topic, max_videos, region, key)
    db.insert_videos(videos)
    # Get image URLs from the database
    img_urls = db.select_urls()

    # Download images to IMG_DIR, classify them and save tags to the database
    for video_id, img_url in img_urls.items():
        with open(IMG_DIR + video_id + '.jpg', 'wb') as img:
            img.write(requests.get(img_url).content)

        tags = it.tag_image(IMG_DIR + video_id + '.jpg')
        db.insert_tags(video_id, tags)

    # Request was successful, returns NO CONTENT message
    return '', 204


@app.route('/visualize', methods=['GET'])
def visualize():
    """Visualize tags in a world map."""
    lat, lng = gmplot.GoogleMapPlotter.geocode('US')

    tags = db.select_tags()
    tags = [[country, tagset] for country, tagset in tags.items()]

    for tag in tags:
        lat, lng = gmplot.GoogleMapPlotter.geocode(tag[0])
        tag.append([lat, lng])

    return flask.render_template('map.html', tag_markers=tags)


def main():
    app.run()

    db.close()
    it.close()


if __name__ == '__main__':
    main()
