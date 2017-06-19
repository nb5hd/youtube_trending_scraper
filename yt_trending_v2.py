# Nikhil Bhaip
# yt_trending_v2.py
# TODO: Use File I/O and LOG info

import requests
from bs4 import BeautifulSoup
import psycopg2

# "Creator on The Rise" does not count as trending, so I will exclude these videos
# Their ordinal positions are enumerated below
SKIP_ROW_NUMS = [4, 5, 6, 7, 8, 9]

YOUTUBE_URL = "https://www.youtube.com/feed/trending"
PARSER = "html.parser"
HOST = "localhost"
PORT = 5432


# This class holds information about each video and a list of all_videos
class Video:
    # class variable "all_videos" holds all videos ever instantiated
    all_videos = []

    def __init__(self, title="", view=-1, duration=-1):
        self.title = title
        self.view = view
        self.duration = duration
        self.all_videos.append(self)

    def __str__(self):
        return "Title: " + self.title + "\nView: " + str(self.view) + "\nDuration: " + str(self.duration)


class VideoListInfo:
    view_list = []
    title_list = []
    duration_list = []

    def __init__(self):
        pass

    # TODO Write general template code for add method
    def add_view(self, view):
        self.view_list.append(view)

    def add_title(self, title):
        self.title_list.append(title)

    def add_duration(self, duration):
        self.duration_list.append(duration)

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

# TODO create a class that holds video_list_info and case_info to avoid extraneous args in methods...


def clean(row_text, video_list_info, case):
    if case == "views":
        ago_index = row_text.index("ago")
        views_index = row_text.index("views")

        view_string = row_text[(ago_index + 3):(views_index - 1)]
        view = view_string.replace(',', '')

        video_list_info.add_view(view)
    elif case == "title_and_duration":
        duration_index = row_text.index("Duration")

        title = row_text[:(duration_index - 3)]
        video_list_info.add_title(title)

        duration = row_text[(duration_index+10):-1]
        video_list_info.add_duration(duration)
    else:
        raise Exception("Invalid case entered")


def get_row_and_clean(rows, video_list_info, case="none"):
    if not isinstance(video_list_info, VideoListInfo):
        raise Exception("Invalid video_list_info type")
    for i, row in enumerate(rows):
        if i not in SKIP_ROW_NUMS:
            row_text = row.get_text()
            clean(row_text, video_list_info, case)


def main():
    content = get_page_content()

    # Find all rows
    view_rows = content.find_all(class_="yt-lockup-meta-info")
    title_time_rows = content.find_all(class_="yt-lockup-title")

    if len(view_rows) != len(title_time_rows):
        raise Exception("Error: Mismatch between length of number of views and number of titles. \nExiting...")

    video_list_info = VideoListInfo()

    get_row_and_clean(view_rows, video_list_info, case="views")
    get_row_and_clean(title_time_rows, video_list_info, case="title_and_duration")

    # TODO Use File I/O to hold DB credentials
    db = input("Enter database name: ")
    uname = input("Enter username: ")
    pwd = input("Enter password: ")

    try:
        conn = psycopg2.connect(database=db, user=uname, password=pwd, host=HOST, port=PORT)
    except psycopg2.OperationalError:
        raise Exception("Cannot connect to database.")


if __name__ == "__main__":
    main()
