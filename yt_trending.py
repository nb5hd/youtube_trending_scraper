# Nikhil Bhaip
# yt_trending_v2.py
# TODO: Use File I/O and LOG info
# TODO: Rigorous Unit Tests

import requests
from bs4 import BeautifulSoup
import psycopg2
import os

# "Creator on The Rise" does not count as trending, so I will exclude these videos
# Their ordinal positions are enumerated below
SKIP_ROW_NUMS = [4, 5, 6, 7, 8, 9]

YOUTUBE_URL = "https://www.youtube.com/feed/trending"
PARSER = "html.parser"


TABLE_EXISTS_QUERY = "SELECT EXISTS(SELECT * FROM information_schema.tables where table_name=%s)"
YT_TABLE = 'yt_table'
CREATE_TABLE_QUERY = """CREATE TABLE yt_table(
          title TEXT,
          views INTEGER,
          duration TEXT
          )"""
INSERT_ROW_QUERY = "INSERT INTO yt_table (title, views, duration) VALUES (%s, %s, %s);"


# This class holds information about each video and a list of all_videos
class Video:

    def __init__(self, title="", view=-1, duration=-1):
        self.title = title
        self.view = view
        self.duration = duration

    def __str__(self):
        return "Title: " + self.title + "\nView: " + str(self.view) + "\nDuration: " + str(self.duration) + "\n"


class VideoListInfo:
    view_list = []
    title_list = []
    duration_list = []
    video_info = {"views": [],"title": [],"duration": []}

    def __init__(self):
        pass

    # TODO Write general template code for add method
    def add_view(self, view):
        self.view_list.append(view)

    def add_title(self, title):
        self.title_list.append(title)

    def add_duration(self, duration):
        self.duration_list.append(duration)

    # def add_item(self, item, category):
    #     if category in video_
    #     self.all_video_data[category].append(item)

    # TODO Write general template code for converting 'n' lists into a video with 'n' params. (**kwargs maybe?)
    def get_video_list(self):
        if len(self.view_list) == len(self.title_list) and len(self.title_list) == len(self.duration_list):
            video_list = []
            for i in range(len(self.view_list)):
                video = Video(self.title_list[i], self.view_list[i], self.duration_list[i])
                video_list.append(video)
            return video_list
        else:
            raise Exception("Error: Lengths of information lists don't match. \nExiting...")


# TODO Gets page content from general URL (CHANGE URL procedures)
def get_page_content():
    page = requests.get(YOUTUBE_URL)
    return BeautifulSoup(page.content, PARSER)


class Cleaner(object):
    def __init__(self, rows=None, video_list_info=None):
        self.video_list_info = video_list_info
        self.rows = rows
        # self.cleaned_data = []

    def get_row_and_clean(self):
        for i, row in enumerate(self.rows):
            if i not in SKIP_ROW_NUMS:
                row_text = row.get_text()
                self.clean(row_text)
                # cleaned_item = self.clean(row_text)
                # self.cleaned_data.append(cleaned_item)

    def clean(self, row_text):
        pass


class ViewsCleaner(Cleaner):
    def __init__(self, rows=None, video_list_info=None):
        super().__init__(rows, video_list_info)

    def get_row_and_clean(self):
        super().get_row_and_clean()

    def clean(self, row_text):
        ago_index = row_text.index("ago")
        views_index = row_text.index("views")

        view_string = row_text[(ago_index + 3):(views_index - 1)]
        view = view_string.replace(',', '')

        # return view
        self.video_list_info.add_view(view)


class TitleAndDurationCleaner(Cleaner):
    def __init__(self, rows=None, video_list_info=None):
        super().__init__(rows, video_list_info)

    def get_row_and_clean(self):
        super().get_row_and_clean()

    def clean(self, row_text):
        duration_index = row_text.index("Duration")

        title = row_text[:(duration_index - 3)]
        self.video_list_info.add_title(title)

        duration = row_text[(duration_index + 10):-1]
        self.video_list_info.add_duration(duration)


# def clean(row_text, video_list_info, case):
#     if case == "views":
#         ago_index = row_text.index("ago")
#         views_index = row_text.index("views")
#
#         view_string = row_text[(ago_index + 3):(views_index - 1)]
#         view = view_string.replace(',', '')
#
#         video_list_info.add_view(view)
#     elif case == "title_and_duration":
#         duration_index = row_text.index("Duration")
#
#         title = row_text[:(duration_index - 3)]
#         video_list_info.add_title(title)
#
#         duration = row_text[(duration_index+10):-1]
#         video_list_info.add_duration(duration)
#     else:
#         raise Exception("Invalid case entered")
#
#
# def get_row_and_clean(rows, video_list_info, case="none"):
#     if not isinstance(video_list_info, VideoListInfo):
#         raise Exception("Invalid video_list_info type")
#     for i, row in enumerate(rows):
#         if i not in SKIP_ROW_NUMS:
#             row_text = row.get_text()
#             clean(row_text, video_list_info, case)


def get_database_info():
    # db credentials are saved in an environment variable
    db_name = os.getenv("DATABASE_NAME")
    user = os.getenv("DATABASE_USER")
    password = os.getenv("DATABASE_PWD")
    host = os.getenv("DATABASE_HOST")
    port = os.getenv("DATABASE_PORT")
    return db_name, user, password, host, port


# Returns true if YT_TABLE exists in the database
def check_table_exists(cur):
    cur.execute(TABLE_EXISTS_QUERY, (YT_TABLE,))
    return cur.fetchone()[0]


def make_table(cur, yt_data):
    cur.execute(CREATE_TABLE_QUERY)

    for video in yt_data:

        data = (video.title, video.view, video.duration)
        cur.execute(INSERT_ROW_QUERY, data)

    print("yt_table was successfully created and populated")


def main():
    content = get_page_content()

    # Find all rows
    view_rows = content.find_all(class_="yt-lockup-meta-info")
    title_time_rows = content.find_all(class_="yt-lockup-title")

    if len(view_rows) != len(title_time_rows):
        raise Exception("Error: Mismatch between length of number of views and number of titles. \nExiting...")

    # stores information about videos in different lists
    video_list_info = VideoListInfo()

    view_cleaner = ViewsCleaner(view_rows, video_list_info)
    view_cleaner.get_row_and_clean()

    title_time_cleaner = TitleAndDurationCleaner(title_time_rows, video_list_info)
    title_time_cleaner.get_row_and_clean()

    # organize YouTube data into one list
    yt_data = video_list_info.get_video_list()

    for vid in yt_data:
        print(vid)


    # Connect to Database
    db, uname, pword, host, port = get_database_info()

    # FIXME: Fix database authentication error handling
    try:
        conn = psycopg2.connect(database=db, user=uname, password=pword, host=host, port=port)
    except psycopg2.Error:
        raise Exception("Cannot connect to database.")

    cur = conn.cursor()

    table_exists = check_table_exists(cur)

    if not table_exists:
        make_table(cur, yt_data)
    else:
        print("yt_table has already been created and populated")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
