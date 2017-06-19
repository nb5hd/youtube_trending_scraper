# Nikhil Bhaip
# yt_trending_v2.py

import requests
from bs4 import BeautifulSoup
# import psycopg2

# "Creator on The Rise" does not count as trending, so I will exclude these videos
# Their ordinal positions are enumerated below
SKIP_ROW_NUMS = [4,5,6,7,8,9]

YOUTUBE_URL = "https://www.youtube.com/feed/trending"
PARSER = 'html.parser'


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
    time_list = []

    def __init__(self):
        pass




# Gets page content from URL (CHANGE URL procedures)
def get_page_content():

    page = requests.get(YOUTUBE_URL)
    return BeautifulSoup(page.content, PARSER)


def scrape_and_clean(rows, case="none"):
    for i, row in enumerate(rows):
        if i not in SKIP_ROW_NUMS:
            row_text = row.get_text()
            if case == "views":
                ago_index = row_text.index("ago")
                views_index = row_text.index("views")





def main():
    content = get_page_content()

    # Find all rows
    view_rows = content.find_all(class_="yt-lockup-meta-info")
    title_time_rows = content.find_all(class_="yt-lockup-title")

    if len(view_rows) != len(title_time_rows):
        print("Error: Mismatch between length of number of views and number of titles. \nExiting...")
        exit()

    scrape_and_clean(view_rows, case="views")
    scrape_and_clean(title_time_rows)

if __name__ == "__main__":
    main()