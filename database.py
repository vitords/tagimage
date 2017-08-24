import sqlite3


class Database(object):
    """A class for handling the database tasks."""

    def __init__(self):
        self.connection = sqlite3.connect('data/youtube.db')
        self.__create()

    def __create(self):
        """Create the database tables.

        If a table already exists, does nothing.
        """
        cursor = self.connection.cursor()

        query = '''CREATE TABLE IF NOT EXISTS videos (
                id          CHAR(12)    NOT NULL    PRIMARY KEY,
                title       TEXT        NOT NULL,
                description TEXT        NOT NULL,
                thumbnail   TEXT        NOT NULL,
                channel     CHAR(40)    NOT NULL,
                country     CHAR(2)     NOT NULL,
                tag1        INTEGER,
                tag2        INTEGER,
                tag3        INTEGER,
                tag4        INTEGER,
                tag5        INTEGER,
                FOREIGN KEY (tag1, tag2, tag3, tag4, tag5) REFERENCES tags (id, id, id, id, id)
                );
                '''
        cursor.execute(query)

        query = '''CREATE TABLE IF NOT EXISTS tags (
                id          INTEGER     PRIMARY KEY     AUTOINCREMENT,
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
        cursor = self.connection.cursor()

        tag_ids = []
        for tag in tags:
            insert_query = 'INSERT OR IGNORE INTO tags (tag) VALUES (?);'
            cursor.execute(insert_query, (tag, ))
            cursor.execute('SELECT id FROM tags WHERE tag = ?', (tag, ))
            if cursor.fetchone is None:
                tag_ids.append(cursor.lastrowid)
            else:
                tag_ids.append(cursor.fetchone()[0])

        self.connection.commit()

        values = tag_ids
        values.append(video_id)

        update_query = 'UPDATE videos SET tag1 = ?, tag2 = ?, tag3 = ?, tag4 = ?, tag5 = ? WHERE id = ?;'
        cursor.execute(update_query, values)

        self.connection.commit()

    def select_urls(self):
        """Select all image URLs saved in the database.

        Returns:
            dict of video IDs and corresponding image URLs
        """
        cursor = self.connection.cursor()
        query = 'SELECT id, thumbnail FROM videos;'

        urls = cursor.execute(query).fetchall()
        urls = {video_id: url for (video_id, url) in urls}

        return urls

    def select_tags(self):
        """Select the country and tags for each entry.

        Returns:
            dict in the format {'country code': [list of tags]}
        """
        cursor = self.connection.cursor()
        query = """SELECT v.country, t1.tag, t2.tag, t3.tag, t4.tag, t5.tag
                FROM videos AS v
                LEFT JOIN tags AS t1 ON v.tag1 = t1.id
                LEFT JOIN tags AS t2 ON v.tag2 = t2.id
                LEFT JOIN tags AS t3 ON v.tag3 = t3.id
                LEFT JOIN tags AS t4 ON v.tag4 = t4.id
                LEFT JOIN tags AS t5 ON v.tag5 = t5.id
                ORDER BY v.country;"""
        tags = cursor.execute(query).fetchall()
        tags_dict = {}
        for (country, tag1, tag2, tag3, tag4, tag5) in tags:
            tags_dict.setdefault(country, []).append(tag1)
            tags_dict.setdefault(country, []).append(tag2)
            tags_dict.setdefault(country, []).append(tag3)
            tags_dict.setdefault(country, []).append(tag4)
            tags_dict.setdefault(country, []).append(tag5)

        return tags_dict

    def close(self):
        """Close the connection with the database."""
        self.connection.close()
