import os
import sys

from apiclient.discovery import build
from apiclient.errors import HttpError

import sqlite3

IMG_DIR = 'data/img/'

if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)


def get_youtube_data(connection, topic, max_videos, region_code, key):
    """Search for YouTube data and save it in the 'videos' table."""
    youtube = build('youtube', 'v3', developerKey=key)

    # Search for videos on YouTube
    video_search_response = youtube.search().list(
      part='id, snippet',
      type='video',
      topicId=topic,
      maxResults=max_videos,
      regionCode=region_code,
      order='viewCount'
    ).execute()

    for video in video_search_response.get('items', []):
        # Search for the video's channel info
        channel_search_response = youtube.channels().list(
            id=video['snippet']['channelId'],
            part='snippet'
        ).execute()
        channel = channel_search_response.get('items', [])[0]

        # Channel's not always have a specified country. In these cases, use the region code.
        country = channel['snippet']['country'] if 'country' in channel['snippet'] else region_code

        query = 'INSERT INTO videos (id, title, description, thumbnail, channel, country) VALUES (?, ?, ?, ?, ?, ?)'

        try:
            connection.execute(query, (video['id']['videoId'],
                                       video['snippet']['title'],
                                       video['snippet']['description'],
                                       video['snippet']['thumbnails']['high']['url'],
                                       channel['snippet']['title'],
                                       country))
        except sqlite3.IntegrityError:
            print('Error: Tried to insert a video with an existing ID ({}).'.format(video['id']['videoId']))

    connection.commit()


if __name__ == '__main__':
    connection = sqlite3.connect('data/test.db')
    cursor = connection.cursor()

    create_db = '''CREATE TABLE videos (
                id          INT         NOT NULL    PRIMARY KEY,
                title       TEXT        NOT NULL,
                description TEXT        NOT NULL,
                thumbnail   TEXT        NOT NULL,
                channel     CHAR(40)    NOT NULL,
                country     CHAR(2)     NOT NULL
                );
                '''
    try:
        cursor.execute(create_db)
    except sqlite3.OperationalError:
        print('Skipping table creation...')
    try:
        get_youtube_data(connection, topic='/m/068hy', max_videos=50, region_code='BR', key=sys.argv[1])
    except HttpError as e:
        print('An HTTP error {} occurred:\n{}'.format(e.resp.status, e.content))

    connection.close()
