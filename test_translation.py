import requests

# URL of your Flask app
url = 'http://127.0.0.1:5000/translate_video'

# Data to send (replace 'video_url' with an actual YouTube link)
data = {
    'video_url': 'https://www.youtube.com/watch?v=5YagUlY9_Uc',  # Example YouTube link
    'target_language': 'es'  # 'es' for Spanish, change to any other language code
}

# Send POST request
response = requests.post(url, data=data)

# Print the translated subtitles
print(response.text)
