import yt_dlp
import requests
import json
import os
from google.cloud import translate_v2 as translate


def get_subtitles(video_url):
    ydl_opts = {
        'skip_download': True, 
        'writesubtitles': True, 
        'subtitlesformat': 'srt',  
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)

        # Try to get auto-generated English subtitles
        if 'automatic_captions' in info and 'en' in info['automatic_captions']:
            subtitle_url = info['automatic_captions']['en'][0]['url']
            return subtitle_url
        else:
            print("No auto-generated subtitles found.")
            return None


def download_subtitles(subtitle_url):
    # Download the subtitle file from the URL
    response = requests.get(subtitle_url)
    return response.text


def parse_subtitles(subtitle_json):
    # Load the JSON data
    subtitle_data = json.loads(subtitle_json)

    # Extract the subtitle events
    events = subtitle_data.get('events', [])

    # Collect all subtitle segments
    subtitles = []
    for event in events:
        segs = event.get('segs', [])
        for seg in segs:
            text = seg.get('utf8', '')
            if text.strip():  # Only add non-empty text
                subtitles.append(text)

    return "\n".join(subtitles)


def translate_subtitles(subtitle_text, target_language):
    # Split subtitles into lines and translate each one
    lines = subtitle_text.split('\n')
    translated_lines = []

    for line in lines:
        if line.strip():  # Only translate non-empty lines
            translated_text = translator.translate(line, target_language=target_language)['translatedText']
            translated_lines.append(translated_text)
        else:
            translated_lines.append('')  # Keep empty lines as they are for formatting

    return "\n".join(translated_lines)


if __name__ == "__main__":
    # Ask the user for the YouTube video URL and the target language
    video_url = input("Enter the YouTube video URL: ")
    target_language = input("Enter the target language (e.g., 'es' for Spanish, 'fr' for French): ")

    # Fetch the subtitle URL
    subtitle_url = get_subtitles(video_url)

    if subtitle_url:
        print("Downloading subtitles...")
        subtitle_json = download_subtitles(subtitle_url)

        print("Parsing subtitles...")
        subtitles = parse_subtitles(subtitle_json)

        print("\nParsed Subtitles:\n")
        print(subtitles)

        print("\nTranslating subtitles...")
        translated_subtitles = translate_subtitles(subtitles, target_language)

        # Show the translated subtitles
        print("\nTranslated Subtitles:\n")
        print(translated_subtitles)
    else:
        print("No subtitles found.")


