import os
import tkinter as tk
from tkinter import ttk

import noisereduce as nr
import numpy as np
import sounddevice as sd
import soundfile as sf
from deep_translator import GoogleTranslator
from faster_whisper import WhisperModel
from scipy.io.wavfile import write

# ==============================
# CONFIGURACIÓN
# ==============================

DURACION = 5
FS = 16000
ARCHIVO_RUIDOSO = "temp_audio/mic_input.wav"
ARCHIVO_LIMPIO = "temp_audio/mic_input_clean.wav"

# ==============================
# FUNCIONES AUXILIARES
# ==============================


def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def grabar_y_traducir(text_widget, idioma_destino):
    os.makedirs("temp_audio", exist_ok=True)

    text_widget.config(state=tk.NORMAL)
    text_widget.delete("1.0", tk.END)
    text_widget.insert(tk.END, "🎙️ Grabando audio...\n")
    text_widget.update()

    audio = sd.rec(int(DURACION * FS), samplerate=FS, channels=1, dtype="int16")
    sd.wait()
    write(ARCHIVO_RUIDOSO, FS, audio)

    text_widget.insert(tk.END, "🧹 Limpiando ruido...\n")
    text_widget.update()

    data, rate = sf.read(ARCHIVO_RUIDOSO)
    reduced_noise = nr.reduce_noise(y=data.flatten(), sr=rate)
    sf.write(ARCHIVO_LIMPIO, reduced_noise, rate)

    text_widget.insert(tk.END, "🤖 Transcribiendo...\n")
    text_widget.update()

    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, info = model.transcribe(ARCHIVO_LIMPIO, beam_size=5)
    idioma_detectado = info.language
    text_widget.insert(tk.END, f"🌍 Idioma detectado: {idioma_detectado}\n\n")
    text_widget.update()

    traductor = GoogleTranslator(source=idioma_detectado, target=idioma_destino)

    srt_path = "temp_audio/subtitulos_traducidos.srt"
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, segment in enumerate(segments, start=1):
            original = segment.text.strip()
            traducido = traductor.translate(original)

            f.write(f"{i}\n")
            f.write(f"{format_time(segment.start)} --> {format_time(segment.end)}\n")
            f.write(f"{original}\n{traducido}\n\n")

            text_widget.insert(tk.END, f"{original}\n→ {traducido}\n\n")
            text_widget.update()

    text_widget.insert(tk.END, f"\n📄 Subtítulos traducidos guardados: {srt_path}")
    text_widget.config(state=tk.DISABLED)


# ==============================
# INTERFAZ
# ==============================

ventana = tk.Tk()
ventana.title("Escúchame - Traducción Multilingüe")
ventana.geometry("900x650")
ventana.configure(bg="white")

frame_top = tk.Frame(ventana, bg="white")
frame_top.pack(pady=10)

label = tk.Label(
    frame_top, text="🌐 Elegí idioma de traducción:", bg="white", font=("Helvetica", 14)
)
label.pack(side="left", padx=(10, 5))

idioma_var = tk.StringVar(value="en")
combo = ttk.Combobox(
    frame_top,
    textvariable=idioma_var,
    font=("Helvetica", 12),
    width=10,
    state="readonly",
)
combo["values"] = ("en", "es", "pt")
combo.pack(side="left")

boton = ttk.Button(
    frame_top,
    text="🎙️ Iniciar subtitulado y traducción",
    command=lambda: grabar_y_traducir(texto, idioma_var.get()),
)
boton.pack(side="left", padx=20)

texto = tk.Text(
    ventana,
    wrap=tk.WORD,
    font=("Helvetica", 16),
    bg="white",
    fg="black",
    height=30,
    width=100,
)
texto.pack(padx=20, pady=10)

ventana.mainloop()
