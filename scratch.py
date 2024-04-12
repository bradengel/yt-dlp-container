import os
from pathlib import Path
import re

# get the video id from part files
download_ids = []
file_paths = []
for file in Path('/youtube').rglob('*'):
    if file.name.endswith((".part", ".ytdl")):
        id = re.search(r"(?<=\[).+?(?=\])", file.name)
        file_paths.append(file.as_posix())
        download_ids.append(id.group())

download_ids = list(set(download_ids))
print(download_ids)
print(file_paths)

# delete the file(s) that match that name
for file in file_paths:
    print("removing: " + file)
    # os.remove(file)

# re-download the files
# create urls
URL_prefix = 'https://youtube.com/watch?v='
redownload_URLs = []
for id in download_ids:
    redownload_URLs.append(URL_prefix + id)



for dir in os.listdir('youtube'):
    for year in os.listdir('youtube/' + dir):
        print(os.path.abspath(year))
        print(os.listdir('youtube/' + dir + '/' + year))