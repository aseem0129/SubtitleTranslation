import yt_dlp
import requests
import json
from transformers import MarianMTModel, MarianTokenizer

# Dictionary to map language codes to model names
model_mapping = {
    'es': 'Helsinki-NLP/opus-mt-en-es',  # Spanish
    'fr': 'Helsinki-NLP/opus-mt-en-fr',  # French
    'de': 'Helsinki-NLP/opus-mt-en-de',  # German
    'it': 'Helsinki-NLP/opus-mt-en-it',  # Italian
    'pt': 'Helsinki-NLP/opus-mt-en-pt',  # Portuguese
    'ru': 'Helsinki-NLP/opus-mt-en-ru',  # Russian
    'zh': 'Helsinki-NLP/opus-mt-en-zh',  # Chinese
    'ja': 'Helsinki-NLP/opus-mt-en-ja',  # Japanese
    'ko': 'Helsinki-NLP/opus-mt-en-ko',  # Korean
    'ar': 'Helsinki-NLP/opus-mt-en-ar',  # Arabic
    'hi': 'Helsinki-NLP/opus-mt-en-hi',  # Hindi
    'nl': 'Helsinki-NLP/opus-mt-en-nl',  # Dutch
    'tr': 'Helsinki-NLP/opus-mt-en-tr'  # Turkish
}


# Function to load the appropriate MarianMT model for the target language
def get_marian_model_and_tokenizer(target_language):
    if target_language in model_mapping:
        model_name = model_mapping[target_language]
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name)
        return model, tokenizer
    else:
        raise ValueError(f"Unsupported language: {target_language}")


# Function to translate using the MarianMT model
def translate_with_marianmt(text, target_language):
    model, tokenizer = get_marian_model_and_tokenizer(target_language)

    # Tokenize the input text
    tokenized_text = tokenizer.prepare_seq2seq_batch([text], return_tensors='pt')

    # Generate the translation
    translated = model.generate(**tokenized_text)

    # Decode the translation back into readable text
    translated_text = [tokenizer.decode(t, skip_special_tokens=True) for t in translated]

    return translated_text[0]  # Return the translated text


def get_subtitles(video_url):
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'subtitlesformat': 'srt',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)

        if 'automatic_captions' in info and 'en' in info['automatic_captions']:
            subtitle_url = info['automatic_captions']['en'][0]['url']
            return subtitle_url
        else:
            return None


def download_subtitles(subtitle_url):
    response = requests.get(subtitle_url)
    return response.text


def parse_subtitles(subtitle_json):
    subtitle_data = json.loads(subtitle_json)
    events = subtitle_data.get('events', [])
    subtitles = []
    for event in events:
        segs = event.get('segs', [])
        for seg in segs:
            text = seg.get('utf8', '')
            if text.strip():
                subtitles.append(text)

    return "\n".join(subtitles)


def translate_subtitles(subtitle_text, target_language):
    # Use the MarianMT model to translate the text based on the target language
    translated_text = translate_with_marianmt(subtitle_text, target_language)

    return translated_text











