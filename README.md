# tagimage

This application uses a TensorFlow image classifier to attribute tags to the thumbnails of the most viewed YouTube videos of a topic specified by the user. 

Everything is done via REST requests, and there is a world map visualization that can show the places that were included in the database, with the set of tags given by the image classifier to the thumbnails of that location's videos.

## Installation
```
$ git clone https://github.com/vitords/tagimage.git
$ virtualenv tagimage 
$ cd tagimage
$ source bin/activate
$ pip install --upgrade -r requirements.txt
```

## Usage
To start the webservice, run:
```
$ python tag_image_service.py
```
When run for the first time, this will download a pre-trained TensorFlow model capable of classifying images into 1000 different labels.

After the download is complete, the service will start to run locally at http://127.0.0.1:5000/.

To populate the database, one should call the search API method (http://127.0.0.1:5000/search). 

A script named `post_data.py` is included to take care of it, and should be edited to at least contain the **YouTube Data API key** on line 3. Then, simply run as many times and with as many parameter combinations as you see fit:
```
$ python post_data.py
```
YouTube topic IDs can be found here: https://developers.google.com/youtube/v3/docs/search/list

Some examples are:
```
/m/06by7  Rock music
/m/0bzvm2 Gaming
/m/03tmr  Ice hockey
/m/068hy  Pets
/m/07bxq  Tourism
/m/01k8wb Knowledge
```
## Visualization
To visualize the data, make sure that you have populated the database and the webservice is running. 

Then access the following address from your browser:
```
http://127.0.0.1:5000/visualize
```
