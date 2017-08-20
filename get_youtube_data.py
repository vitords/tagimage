import sys

from apiclient.discovery import build
from apiclient.errors import HttpError


def get_youtube_data(topic, max_videos, region_code, key):
    """Search and retrieve YouTube data.

    Args:
        topic: Video topic as curated by YouTube.
        max_videos: Max number of videos to be returned from the search.
        region_code: The region where the video is available (ISO 3166-1 alpha-2).
        key: YouTube Data API key.

    Returns:
        videos: dict containing the info for all videos returned in the search.

    Note:
        'region_code' does not guarantee a video was uploaded from that region.
        This was used simply as a quick way to get geolocation info since this is
        not very common in YouTube videos.
    """
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

    videos = {}

    for video in video_search_response.get('items', []):
        # Search for the video's channel info
        channel_search_response = youtube.channels().list(
            id=video['snippet']['channelId'],
            part='snippet'
        ).execute()
        channel = channel_search_response.get('items', [])[0]

        # Channel's not always have a specified country. In these cases, use the region code.
        country = channel['snippet']['country'] if 'country' in channel['snippet'] else region_code

        videos[video['id']['videoId']] = {'title': video['snippet']['title'],
                                          'description': video['snippet']['description'],
                                          'thumbnail': video['snippet']['thumbnails']['high']['url'],
                                          'channel': channel['snippet']['title'],
                                          'country': country,
                                          }

    return videos


if __name__ == '__main__':
    try:
        print(get_youtube_data(topic='/m/068hy', max_videos=50, region_code='BR', key=sys.argv[1]))
    except HttpError as e:
        print('An HTTP error {} occurred:\n{}'.format(e.resp.status, e.content))
