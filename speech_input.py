import sounddevice as sd
import numpy as np
import scipy.io.wavfile
import whisper

# Load Whisper medium English-only model
#test test
model = whisper.load_model("medium.en")

def record_and_transcribe():
    fs = 16000
    duration = 8  # seconds

    print("Recording… Please speak clearly.")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    print("Recording complete.")

    audio = np.squeeze(audio)
    audio = audio / max(np.abs(audio))  # Normalize
    audio_int16 = (audio * 32767).astype(np.int16)
    scipy.io.wavfile.write("input.wav", fs, audio_int16)

    result = model.transcribe("input.wav", language="en", task="transcribe", fp16=False)

    def correct_keywords(text):
        corrections = {
            "hey dick": "headache",
            "hay dick": "headache",
            "dick": "headache",
            "head ache": "headache",
            "head egg": "headache",
            "head deck": "headache",
            "a deck": "headache",
            "a take": "headache",
            "stomach pane": "stomach pain",
            "stomach bean": "stomach pain",
            "fiver": "fever",
            "coffee": "cough",
            "gold": "cold",
            "sore road": "sore throat",
            "sore wrote": "sore throat"
        }
        text = text.lower()
        for wrong, right in corrections.items():
            text = text.replace(wrong, right)
        return text

    raw_text = result["text"]
    clean_text = correct_keywords(raw_text)

    return clean_text