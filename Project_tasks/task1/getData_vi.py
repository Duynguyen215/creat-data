import os
import json
import subprocess
import re
import sys
import io

channel_url = "https://www.youtube.com/@phamnguyengiahuyy/videos"  

#Get list of video URLs from the channel
print("Fetching video list...")
playlist_json = "playlist.json"
subprocess.run(["yt-dlp", "--flat-playlist", "-J", channel_url], stdout=open(playlist_json, "w"))

#Extract URLs from playlist JSON
with open(playlist_json, "r") as f:
    data = json.load(f)
video_urls = [f"https://www.youtube.com/watch?v={entry['id']}" for entry in data["entries"]]

with open("video_urls.txt", "w") as f:
    for url in video_urls:
        f.write(url + "\n")

#Download MP3_files
print("Downloading MP3 audio files...")
subprocess.run([
    "yt-dlp", "-x", "--audio-format", "mp3", "-a", "video_urls.txt",
    "-o", "%(title)s.%(ext)s"
])

#Download auto-generated subtitles (transcripts) (.vtt_file)
print("Downloading subtitles...")
subprocess.run([
    "yt-dlp", "--write-auto-sub", "--sub-lang", "vi", "--skip-download",
    "-a", "video_urls.txt"
])

#  Convert .vtt subtitle files to plain text

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')



def convert_vtt_to_txt():
    current_dir = os.getcwd()
    vtt_files = [f for f in os.listdir(current_dir) if f.endswith(".vi.vtt")]

    if not vtt_files:
        print("No .vi.vtt subtitle files found in the current directory.")
        return

    print(f"Found {len(vtt_files)} .vi.vtt files.")

    for filename in vtt_files:
        print(f"Processing: {filename}")
        txt_filename = filename.replace(".vi.vtt", ".txt")

        try:
            with open(filename, "r", encoding="utf-8", errors="ignore") as vtt_file:
                lines = vtt_file.readlines()
        except Exception as e:
            print(f" Error reading {filename}: {e}")
            continue

        cleaned_lines = []
        previous_line = ""

        for line in lines:
            line = line.strip()

            # Skip timestamps and empty lines
            if not line or "-->" in line or line.isdigit():
                continue

            # Remove tags like <c> and timestamps inside angle brackets
            clean_line = re.sub(r"<[^>]+>", "", line).strip()

            # Avoid duplicate lines
            if clean_line and clean_line != previous_line:
                cleaned_lines.append(clean_line)
                previous_line = clean_line

        final_text = " ".join(cleaned_lines)

        try:
            with open(txt_filename, "w", encoding="utf-8") as txt_file:
                txt_file.write(final_text)
            print(f"Converted: {filename} -> {txt_filename}")
        except Exception as e:
            print(f" Failed to write {txt_filename}: {e}")

    


convert_vtt_to_txt()


print("Done!.")
