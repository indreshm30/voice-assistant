from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
from io import BytesIO
import base64

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    source_lang = data['source_lang']
    target_lang = data['target_lang']

    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.pause_threshold = 1
    recognizer.dynamic_energy_threshold = True

    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    
    try:
        text = recognizer.recognize_google(audio, language=source_lang)
        print("Transcribed:", text)
    except sr.UnknownValueError:
        return jsonify({"transcribed": "Could not understand", "translated": "", "audio": ""})
    except sr.RequestError as e:
        return jsonify({"transcribed": f"API error: {e}", "translated": "", "audio": ""})

    translated = GoogleTranslator(source=source_lang, target=target_lang).translate(text)

    tts = gTTS(text=translated, lang=target_lang)
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    audio_data = base64.b64encode(mp3_fp.read()).decode('utf-8')

    return jsonify({
        "transcribed": text,
        "translated": translated,
        "audio": audio_data
    })

if __name__ == "__main__":
    app.run(debug=True)
