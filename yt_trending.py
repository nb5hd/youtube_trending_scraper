import requests
from bs4 import BeautifulSoup
import psycopg2


page = requests.get("https://www.youtube.com/feed/trending")
soup = BeautifulSoup(page.content, 'html.parser')

view_rows = soup.find_all(class_="yt-lockup-meta-info")
title_rows = soup.find_all(class_="yt-lockup-title")

view_list = []
title_list = []
time_list = []

# Clean up views!
for i, row in enumerate(view_rows):
    # "Creator on The Rise" does not count as trending, so I will exclude these videos
    # They are identified in the code by having the word "views" come before the word "ago" in each row
    row_text = view_rows[i].get_text()

    ago_index = row_text.index("ago")
    views_index = row_text.index("views")

    if views_index > ago_index:
        view_string = row_text[(ago_index+3):(views_index-1)]
        view = view_string.replace(',', '')

        view_list.append(view)

# Clean up titles
for i, row in enumerate(title_rows):

    if i not in [4, 5, 6, 7, 8, 9]:
        # print(row.get_text())

        row_text = title_rows[i].get_text()

        duration_index = row_text.index("Duration")

        title = row_text[:(duration_index-3)]
        time = row_text[(duration_index+10):-1]

        title_list.append(title)
        time_list.append(time)

# print(len(view_list) == len(title_list))

yt_data = list(zip(title_list, view_list, time_list))
# _____________________________________________________________________________________________________________________

conn = psycopg2.connect(database="nikhil", user="postgres", password="", host="localhost", port="5432")

print("Opened database successfully")

cur = conn.cursor()

# Check if yt_table already exists
cur.execute("SELECT EXISTS(SELECT * FROM information_schema.tables where table_name=%s)",
 ('yt_table',))
yt_table_exists = cur.fetchone()[0]

# If yt_table does not exist, then create a table and populate from CSV
if(yt_table_exists != True):
    cur.execute("""CREATE TABLE yt_table(
      title TEXT,
      views INTEGER,
      duration TEXT
      )""")

    for video in yt_data:
        video_title = video[0]
        video_view = video[1]
        video_time = video[2]

        query = "INSERT INTO yt_table (title, views, duration) VALUES (%s, %s, %s);"
        data = (video_title, video_view, video_time)

        cur.execute(query, data)

    print("yt_table was successfully created and populated")
else:
    print("yt_table has already been created and populated")


conn.commit()
conn.close()

