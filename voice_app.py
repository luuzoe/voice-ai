# Voice AI — PC Text to Voice app (Python)
# မြန်မာအသံ (Nilar/Thiha) — အခမဲ့, internet လိုတယ်
#
# Setup (၃ ဆင့်ပဲ):
#   1) python.org က Python သွင်း ("Add python.exe to PATH" ကို tick လုပ်)
#   2) pip install edge-tts
#   3) python voice_app.py

import asyncio
import os
import tempfile
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import edge_tts

VOICES = {
    "Nilar (မိန်းကလေး အသံ)": "my-MM-NilarNeural",
    "Thiha (ယောကျ်ားလေး အသံ)": "my-MM-ThihaNeural",
}


def text_to_mp3(text, voice_id, out_path):
    async def _run():
        tts = edge_tts.Communicate(text, voice_id)
        await tts.save(out_path)

    asyncio.run(_run())


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Voice AI — Text to Voice")
        self.geometry("560x540")

        ttk.Label(self, text="စာသား",
                  font=("", 11, "bold")).pack(anchor="w", padx=12, pady=(12, 4))
        self.text = tk.Text(self, height=12, font=("", 12), wrap="word")
        self.text.pack(fill="both", expand=True, padx=12)
        self.text.insert("1.0", "မင်္ဂလာပါ။ ဒါက Voice AI စမ်းသပ်မှုပါ။")

        row = ttk.Frame(self)
        row.pack(fill="x", padx=12, pady=10)
        ttk.Label(row, text="အသံ:").pack(side="left")
        self.voice_var = tk.StringVar(value=list(VOICES)[0])
        ttk.Combobox(row, textvariable=self.voice_var,
                     values=list(VOICES), state="readonly",
                     width=28).pack(side="left", padx=8)

        btns = ttk.Frame(self)
        btns.pack(pady=6)
        self.speak_btn = ttk.Button(btns, text="🔊 ဖတ်ပြ",
                                    command=self.on_speak)
        self.speak_btn.pack(side="left", padx=6)
        self.save_btn = ttk.Button(btns, text="💾 MP3 သိမ်း",
                                   command=self.on_save)
        self.save_btn.pack(side="left", padx=6)

        self.status = ttk.Label(self, text="အဆင်သင့်", foreground="gray")
        self.status.pack(pady=8)

    def _set_busy(self, busy, msg):
        for b in (self.speak_btn, self.save_btn):
            b.config(state="disabled" if busy else "normal")
        self.status.config(text=msg)
        self.update_idletasks()

    def _get_input(self):
        text = self.text.get("1.0", "end").strip()
        voice_id = VOICES[self.voice_var.get()]
        return text, voice_id

    def on_speak(self):
        text, voice_id = self._get_input()
        if not text:
            messagebox.showwarning("သတိ", "စာသား အရင်ရိုက်ထည့်ပါ")
            return
        self._set_busy(True, "အသံထုတ်နေတယ်…")

        def work():
            try:
                path = os.path.join(tempfile.gettempdir(),
                                    "voice_ai_speak.mp3")
                text_to_mp3(text, voice_id, path)
                os.startfile(path)  # Windows default player နဲ့ ဖွင့်
                self.after(0, lambda: self._set_busy(False, "ပြီးပြီ ✓"))
            except Exception as e:
                self.after(0, lambda: self._set_busy(False, "အမှား"))
                self.after(0, lambda m=str(e): messagebox.showerror(
                    "အမှား", f"အသံထုတ်မရဘူး:\n{m}"))

        threading.Thread(target=work, daemon=True).start()

    def on_save(self):
        text, voice_id = self._get_input()
        if not text:
            messagebox.showwarning("သတိ", "စာသား အရင်ရိုက်ထည့်ပါ")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("MP3 files", "*.mp3")],
            initialfile="voice.mp3")
        if not path:
            return
        self._set_busy(True, "MP3 သိမ်းနေတယ်…")

        def work():
            try:
                text_to_mp3(text, voice_id, path)
                self.after(0, lambda: self._set_busy(
                    False, f"သိမ်းပြီးပြီ ✓\n{path}"))
            except Exception as e:
                self.after(0, lambda: self._set_busy(False, "အမှား"))
                self.after(0, lambda m=str(e): messagebox.showerror(
                    "အမှား", f"သိမ်းမရဘူး:\n{m}"))

        threading.Thread(target=work, daemon=True).start()


if __name__ == "__main__":
    App().mainloop()
