import os

import sounddevice as sd
from faster_whisper import WhisperModel
from scipy.io.wavfile import write

# ==============================
# CONFIGURACIÓN
# ==============================

DURACION = 5  # duración de grabación en segundos
FS = 16000  # frecuencia de muestreo
ARCHIVO_SALIDA = "temp_audio/mic_input.wav"

# ==============================
# GRABACIÓN DE AUDIO
# ==============================

os.makedirs("temp_audio", exist_ok=True)
print(f"🎙️ Grabando audio del micrófono durante {DURACION} segundos...")

audio = sd.rec(int(DURACION * FS), samplerate=FS, channels=1, dtype="int16")
sd.wait()

write(ARCHIVO_SALIDA, FS, audio)
print(f"✅ Audio guardado en: {ARCHIVO_SALIDA}")

# ==============================
# TRANSCRIPCIÓN CON WHISPER
# ==============================

print("🤖 Transcribiendo audio...")

model = WhisperModel("base", device="cpu", compute_type="int8")
segments, info = model.transcribe(ARCHIVO_SALIDA, beam_size=5)

print("🌍 Idioma detectado:", info.language)

print("\n📋 Subtítulos:")
for segment in segments:
    print(f"[{segment.start:.2f} → {segment.end:.2f}] {segment.text}")
