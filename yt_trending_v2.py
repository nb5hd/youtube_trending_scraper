# Nikhil Bhaip
# yt_trending_v2.py
# Assume that YouTube titles are immutable and unique
# TODO: Use File I/O and LOG info
# TODO: Rigorous Unit Tests

import requests
from bs4 import BeautifulSoup
import datetime
# import psycopg2
# import os

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
class VideoDB(object):

    def __init__(self):
        self.video_dict = {}

    def add_title(self, title, i):
        self.video_dict[title] = {}

    def add_date(self, title, date):
        self.video_dict[title]["time_dependent"] = {}
        self.video_dict[title]["time_dependent"][date] = {}

    def add_rank(self, title, date, rank):
        self.video_dict[title]["time_dependent"][date]["rank"] = rank

    def add_duration(self, duration, title):
        self.video_dict[title]["duration"] = duration

    def add_youtuber(self, youtuber, title):
        self.video_dict[title]["youtuber"] = youtuber

    def add_view(self, title, date, view):
        self.video_dict[title]["time_dependent"][date]["views"] = view

    def __str__(self):
        ret_val = ""
        for title, info in self.video_dict.items():
            ret_val += title + "\n\t" + str(info["youtuber"]) + "\n\t" + str(info["duration"]) + "\n\t"
            for date, date_info in info["time_dependent"].items():
                ret_val += date.strftime("%m/%d/%y") + "\n\t\t "
                ret_val += "View Count: " + str(date_info["views"]) + "\n\t\t"
                ret_val += " Rank: " + str(date_info["rank"]) + "\n\n"
        return ret_val


class Duration:
    def __init__(self, dur_string):
        tokens = dur_string.split(":")
        if len(tokens) == 1:
            self.seconds = int(tokens[0])
            self.minutes = 0
            self.hours = 0
        elif len(tokens) == 2:
            self.seconds = int(tokens[1])
            self.minutes = int(tokens[0])
            self.hours = 0
        elif len(tokens) == 3:
            self.seconds = int(tokens[2])
            self.minutes = int(tokens[1])
            self.hours = int(tokens[0])
        else:
            raise Exception("Program is not able to process videos of this type of duration.")

    def __str__(self):
        if self.hours > 0:
            if self.minutes > 9 and self.seconds > 9:
                return str(self.hours)+":"+str(self.minutes)+":"+str(self.seconds)
            elif self.minutes < 9 and self.seconds > 9:
                return str(self.hours) + ":0" + str(self.minutes) + ":" + str(self.seconds)
            elif self.minutes > 9 and self.seconds < 9:
                return  str(self.hours) + ":" + str(self.minutes) + ":0" + str(self.seconds)
            else:
                return str(self.hours) + ":0" + str(self.minutes) + ":0" + str(self.seconds)
        elif self.minutes > 0:
            if self.seconds > 9:
                return str(self.minutes) + ":" + str(self.seconds)
            else:
                return str(self.minutes) + ":0" + str(self.seconds)
        else:
            if self.seconds > 9:
                return "0:" + str(self.seconds)
            else:
                return "0:0" + str(self.seconds)


# TODO Gets page content from general URL (CHANGE URL procedures)
def get_page_content():
    page = requests.get(YOUTUBE_URL)
    return BeautifulSoup(page.content, PARSER)


# class Clean(object):
#     def __init__(self, rows=None, video_list_info=None):
#         self.video_list_info = video_list_info
#         self.rows = rows
#         # self.cleaned_data = []
#
#     def get_row_and_clean(self):
#         for i, row in enumerate(self.rows):
#             if i not in SKIP_ROW_NUMS:
#                 row_text = row.get_text()
#                 self.clean(row_text)
#                 # cleaned_item = self.clean(row_text)
#                 # self.cleaned_data.append(cleaned_item)
#
#     def clean(self, row_text):
#         pass
#
#
# class CleanViews(Clean):
#     def __init__(self, rows=None, video_list_info=None):
#         super().__init__(rows, video_list_info)
#
#     def get_row_and_clean(self):
#         super().get_row_and_clean()
#
#     def clean(self, row_text):
#         ago_index = row_text.index("ago")
#         views_index = row_text.index("views")
#
#         view_string = row_text[(ago_index + 3):(views_index - 1)]
#         view = view_string.replace(',', '')
#
#         # return view
#         self.video_list_info.add_view(view)
#
#
# class CleanTitleAndDuration(Clean):
#     def __init__(self, rows=None, video_list_info=None):
#         super().__init__(rows, video_list_info)
#
#     def get_row_and_clean(self):
#         super().get_row_and_clean()
#
#     def clean(self, row_text):
#         duration_index = row_text.index("Duration")
#
#         title = row_text[:(duration_index - 3)]
#         self.video_list_info.add_title(title)
#
#         duration = row_text[(duration_index + 10):-1]
#         self.video_list_info.add_duration(duration)
#
#
# # def clean(row_text, video_list_info, case):
# #     if case == "views":
# #         ago_index = row_text.index("ago")
# #         views_index = row_text.index("views")
# #
# #         view_string = row_text[(ago_index + 3):(views_index - 1)]
# #         view = view_string.replace(',', '')
# #
# #         video_list_info.add_view(view)
# #     elif case == "title_and_duration":
# #         duration_index = row_text.index("Duration")
# #
# #         title = row_text[:(duration_index - 3)]
# #         video_list_info.add_title(title)
# #
# #         duration = row_text[(duration_index+10):-1]
# #         video_list_info.add_duration(duration)
# #     else:
# #         raise Exception("Invalid case entered")
# #
# #
# # def get_row_and_clean(rows, video_list_info, case="none"):
# #     if not isinstance(video_list_info, VideoListInfo):
# #         raise Exception("Invalid video_list_info type")
# #     for i, row in enumerate(rows):
# #         if i not in SKIP_ROW_NUMS:
# #             row_text = row.get_text()
# #             clean(row_text, video_list_info, case)
#
#
# def get_database_info():
#     # db credentials are saved in an environment variable
#     db_name = os.getenv("DATABASE_NAME")
#     user = os.getenv("DATABASE_USER")
#     password = os.getenv("DATABASE_PWD")
#     host = os.getenv("DATABASE_HOST")
#     port = os.getenv("DATABASE_PORT")
#     return db_name, user, password, host, port
#
#
# # Returns true if YT_TABLE exists in the database
# def check_table_exists(cur):
#     cur.execute(TABLE_EXISTS_QUERY, (YT_TABLE,))
#     return cur.fetchone()[0]
#
#
# def make_table(cur, yt_data):
#     cur.execute(CREATE_TABLE_QUERY)
#
#     for video in yt_data:
#
#         data = (video.title, video.view, video.duration)
#         cur.execute(INSERT_ROW_QUERY, data)
#
#     print("yt_table was successfully created and populated")

# Get the title from html_text
def title_retriever(title_list):
    ret_list = []
    for i, row in enumerate(title_list):
        duration_index = row.index("Duration")
        title = row[:(duration_index - 3)]
        ret_list.append(title)
    return ret_list


def views_retriever(views_list):
    ret_list = []
    for i, row in enumerate(views_list):
        ago_index = row.index("ago")
        views_index = row.index("views")
        if views_index > ago_index:
            view_string = row[(ago_index + 3):(views_index - 1)]
        else:
            view_string = row[:(views_index - 1)]
        view = view_string.replace(',', '')
        ret_list.append(view)
    return ret_list


# Get the duration from html_text
def duration_retriever(duration_list):
    ret_list = []
    for i, row in enumerate(duration_list):
        duration_index = row.index("Duration")
        duration = row[(duration_index + 10):-1]
        ret_list.append(duration)
    return ret_list


def main():
    # First pass is to get titles and populate video_db
    content = get_page_content()
    video_db = VideoDB()
    today = datetime.date.today()
    todays_feed_order = {}

    # TODO convert next three lines to a method
    title_rows = content.find_all(class_="yt-lockup-title")
    raw_titles_list = [row.get_text() for row in list(title_rows)]
    titles_list = title_retriever(raw_titles_list)
    print(len(titles_list))

    for i, title in enumerate(titles_list):
        video_db.add_title(title, i+1)
        todays_feed_order[i+1] = title
        video_db.add_date(title, today)
        video_db.add_rank(title, today, i+1)

    # Second pass is to get durations and populate video_db
    duration_rows = content.find_all(class_="yt-lockup-title")
    raw_durations_list = [row.get_text() for row in list(duration_rows)]
    durations_list = duration_retriever(raw_durations_list)

    for i, duration_str in enumerate(durations_list):
        title = todays_feed_order[i+1]
        duration_obj = Duration(duration_str)
        video_db.add_duration(duration_obj, title)

    # Third pass is to get views and populate video_db
    view_rows = content.find_all(class_="yt-lockup-meta-info")
    raw_views_list = [row.get_text() for row in list(view_rows)]
    views_list = views_retriever(raw_views_list)

    for i, view in enumerate(views_list):
        title = todays_feed_order[i + 1]
        video_db.add_view(title, today, view)

    # Fourth pass is to get YouTuber and populate video_db

    youtuber_rows = content.find_all(class_="yt-lockup-byline")
    raw_youtuber_list = [row.get_text() for row in list(youtuber_rows)]
    youtuber_list = [row.strip("\xa0") if "\xa0" in row else row for row in raw_youtuber_list]

    for i, youtuber in enumerate(youtuber_list):
         title = todays_feed_order[i + 1]
         video_db.add_youtuber(youtuber, title)

    with open("output.txt", "w") as text_file:
        print(video_db, file=text_file)


if __name__ == "__main__":
    main()
