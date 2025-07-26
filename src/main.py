import os
import tkinter as tk
from tkinter import ttk

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
# FUNCIONES DE FORMATO SRT
# ==============================


def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


# ==============================
# FUNCIÓN PRINCIPAL
# ==============================


def grabar_y_transcribir(text_widget):
    os.makedirs("temp_audio", exist_ok=True)

    text_widget.insert(tk.END, "🎙️ Grabando audio...")
    text_widget.update()

    audio = sd.rec(int(DURACION * FS), samplerate=FS, channels=1, dtype="int16")
    sd.wait()

    write(ARCHIVO_SALIDA, FS, audio)
    text_widget.insert(tk.END, f"✅ Audio guardado en: {ARCHIVO_SALIDA}")
    text_widget.update()

    text_widget.insert(tk.END, "🤖 Transcribiendo...")
    text_widget.update()

    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, info = model.transcribe(ARCHIVO_SALIDA, beam_size=5)

    text_widget.insert(tk.END, f"🌍 Idioma detectado: {info.language}\n\n")
    text_widget.update()

    # Mostrar subtítulos en vivo
    srt_path = "temp_audio/subtitulos.srt"
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, segment in enumerate(segments, start=1):
            linea = f"[{segment.start:.2f} → {segment.end:.2f}] {segment.text}\n"
            text_widget.insert(tk.END, linea)
            text_widget.update()

            # Guardar en SRT
            f.write(f"{i}\n")
            f.write(f"{format_time(segment.start)} --> {format_time(segment.end)}\n")
            f.write(f"{segment.text.strip()}\n\n")

    text_widget.insert(tk.END, f"\n📄 Subtítulos guardados: {srt_path}")
    text_widget.update()


# ==============================
# INTERFAZ CON TKINTER
# ==============================

ventana = tk.Tk()
ventana.title("Escúchame - Subtítulos en Vivo")
ventana.configure(bg="black")

# Widget de texto grande
texto = tk.Text(
    ventana,
    wrap=tk.WORD,
    font=("Helvetica", 18),
    bg="black",
    fg="yellow",
    height=20,
    width=70,
)
texto.pack(padx=20, pady=20)

# Botón para iniciar
boton = ttk.Button(
    ventana, text="Iniciar subtitulado", command=lambda: grabar_y_transcribir(texto)
)
boton.pack(pady=10)

# Iniciar loop
ventana.mainloop()
