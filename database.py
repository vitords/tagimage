import sqlite3


class Database(object):
    """A class for handling the database tasks."""

    def __init__(self):
        self.connection = sqlite3.connect('data/youtube.db')
        self._create()

    def _create(self):
        """Create the database tables.

        If a table already exists, does nothing.
        """
        cursor = self.connection.cursor()

        query = '''CREATE TABLE IF NOT EXISTS videos (
                id          INT         NOT NULL    PRIMARY KEY,
                title       TEXT        NOT NULL,
                description TEXT        NOT NULL,
                thumbnail   TEXT        NOT NULL,
                channel     CHAR(40)    NOT NULL,
                country     CHAR(2)     NOT NULL,
                tag1        INT,
                tag2        INT,
                tag3        INT,
                tag4        INT,
                tag5        INT,
                FOREIGN KEY (tag1, tag2, tag3, tag4, tag5) REFERENCES tags (id, id, id, id, id)
                );
                '''
        cursor.execute(query)

        query = '''CREATE TABLE IF NOT EXISTS tags (
                id          INT         NOT NULL    PRIMARY KEY,
                tag         TEXT        NOT NULL,
                UNIQUE(tag)
                );
                '''
        cursor.execute(query)

    def insert_videos(self, videos):
        """Insert a set of video information in the database.

        Args:
            videos: dict of information about videos
        """
        query = 'INSERT INTO videos (id, title, description, thumbnail, channel, country) VALUES (?, ?, ?, ?, ?, ?)'

        for video_id, video_info in videos.items():
            try:
                self.connection.execute(query, (video_id,
                                                video_info['title'],
                                                video_info['description'],
                                                video_info['thumbnail'],
                                                video_info['channel'],
                                                video_info['country']))
            except sqlite3.IntegrityError:
                print('Error: Tried to insert a video with an existing ID ({}).'.format(video_id))

        self.connection.commit()

    def insert_tags(self, video_id, tags):
        """Associate a video with the tags it received from the classifier.

        If the tag is not yet present in the database, add it to the 'tags' table.

        Args:
            video_id: the ID of the video.
            tags: the tags to be associated with the video.l
        """
        for tag in tags:
            insert_query = 'INSERT OR IGNORE INTO tags (tag) VALUES (?)'

            self.connection.execute(insert_query, (tag))

        cursor = self.connection.cursor()
        update_query = 'UPDATE videos SET tag1 = ?, tag2 = ?, tag3 = ?, tag4 = ?, tag5 = ? WHERE id = ?)'

        cursor.execute(update_query, (tags[0], tags[1], tags[2], tags[3], tags[4], video_id))

        self.connection.commit()

    def select_urls(self):
        """Select all image URLs saved in the database.

        Returns:
            dict of video IDs and corresponding image URLs
        """
        cursor = self.connection.cursor()
        query = "SELECT id, thumbnail FROM videos;"

        urls = cursor.execute(query).fetchall()
        urls = {video_id: url for (video_id, url) in urls}

        return urls

    def close(self):
        """Close the connection with the database."""
        self.connection.close()
