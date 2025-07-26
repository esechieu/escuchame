from faster_whisper import WhisperModel

# Cargar modelo preentrenado
model = WhisperModel("base", device="cpu", compute_type="int8")

# Transcribir un archivo de prueba
segments, info = model.transcribe("ruta/a/tu/audio.mp3", beam_size=5)

print("Idioma detectado:", info.language)

# Mostrar subtítulos en consola
for segment in segments:
    print(f"[{segment.start:.2f} → {segment.end:.2f}] {segment.text}")
