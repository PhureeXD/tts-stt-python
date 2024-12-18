# %% [markdown]
# ## Speech To Text and Text To Speech with Python and Tkinter

# %%
import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"  # Hide pygame support prompt

import tempfile
import threading
import tkinter as tk
from tkinter import *
from tkinter.ttk import Combobox
from typing import Union

import pygame
import pyttsx3
import speech_recognition as sr
from gtts import gTTS

# %% [markdown]
# ### Constants

# %%
# Fonts and Colors


main_font = ("Arial", 15)


header_font = ("Arial", 30, "bold")


bg_color = "#2C3E50"
btn_color = "lime"


btn_hover = "red"


text_bg = "#ECF0F1"


text_fg = "#2C3E50"


label_fg = "white"


upper_frame_color = "#3498DB"

# %%
# Root Configuration


root = tk.Tk()


root.title("TTS & STT App")

root.iconphoto(False, PhotoImage(file="./img/icons8-streamlit-48.png"))

root.wm_iconphoto(True, PhotoImage(file="./img/icons8-streamlit-48.png"))

root.geometry("1000x580+500+80")  # width x height

root.resizable(False, False)

root.config(bg=upper_frame_color)

# %% [markdown]
# ### Codes

# %%
# Tooltip Function


def create_tooltip(widget: Union[Button, Combobox, Widget], text: str) -> None:

    tooltip = Label(
        root,
        text=text,
        bg="white",
        fg="black",
        font=("Arial", 10),
        relief="ridge",
        borderwidth=1,
        wraplength=200,
    )

    tooltip.place_forget()  # Hide tooltip when created

    widget.bind(
        "<Enter>",
        lambda _: (
            tooltip.place(
                x=widget.winfo_x() + widget.winfo_width() + 10, y=widget.winfo_y()
            ),
            tooltip.lift(),  # Lift the tooltip to the top order
        ),
    )

    widget.bind("<Leave>", lambda _: tooltip.place_forget())


# %%
# Upper Frame with Header


upper_frame = Frame(root, bg=upper_frame_color, width=1000, height=130)


upper_frame.place(x=0, y=0)


header_label = Label(
    upper_frame,
    text="Text-to-Speech & Speech-to-Text App",
    font=header_font,
    bg=upper_frame_color,
    fg=label_fg,
)


header_label.place(relx=0.5, rely=0.5, anchor="center")

# %%
# Text Box


text_box = Text(
    root,
    font=main_font,
    bg=text_bg,
    fg=text_fg,
    wrap="word",
    relief="flat",
    highlightthickness=1,
)


text_box.place(x=30, y=150, width=940, height=160)


text_box.config(highlightbackground=btn_color)


# Language Combobox


Label(root, text="Select Language", font=main_font, bg=bg_color, fg=label_fg).place(
    x=200, y=320
)


language_box = Combobox(
    root, font=main_font, values=["English", "Thai"], state="readonly"
)


language_box.place(x=200, y=350, width=180, height=40)


language_box.set("English")
create_tooltip(
    language_box, "Choose the language: English or Thai (No Voice Change for Thai)"
)


# Speed Combobox


Label(root, text="Select Speed", font=main_font, bg=bg_color, fg=label_fg).place(
    x=600, y=320
)


speed_box = Combobox(root, font=main_font, values=["Medium", "Slow"], state="readonly")


speed_box.place(x=600, y=350, width=180, height=40)


speed_box.set("Medium")


create_tooltip(speed_box, "Choose the speaking speed: Medium or Slow")

# %%
# Text-to-Speech Engine
engine = pyttsx3.init()

# Initialize pygame mixer
pygame.mixer.init()


def text_to_speech():

    text = text_box.get("1.0", "end").strip()
    speed = speed_box.get()

    lang = language_box.get()

    # print(f"Text: {text}, Speed: {speed}, Language: {lang}")

    if not text:

        text_box.delete("1.0", tk.END)

    try:
        if lang == "Thai":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                speech_file = temp_file.name
                # Use gTTS for Thai language
                tts = gTTS(text=text, lang="th", slow=(speed == "Slow"))
                tts.save(speech_file)

            # Play using pygame mixer
            pygame.mixer.music.load(speech_file)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(4)

            pygame.mixer.music.unload()
            os.unlink(speech_file)  # Safely delete the temporary file

        else:

            # Use pyttsx3 for English (can change voice speed,gender)

            engine.setProperty("rate", 150 if speed == "Slow" else 200)

            engine.say(text)

            engine.runAndWait()

    except Exception as e:

        text_box.delete("1.0", tk.END)

        text_box.insert("end", f"Error: {str(e)}")


# %%
# Speech-to-Text Engine


def speech_to_text():

    recognizer = sr.Recognizer()

    def recognize():

        with sr.Microphone() as source:

            text_box.delete("1.0", tk.END)

            text_box.insert("end", "Listening...\n")

            root.update_idletasks()

            try:

                # Adjust for ambient noise and listen for 5 seconds

                recognizer.adjust_for_ambient_noise(source, duration=1)

                audio = recognizer.listen(source)

                # Recognize speech

                text = recognizer.recognize_google(audio)

                # Clear previous text and insert recognized text

                text_box.delete("1.0", tk.END)

                text_box.insert("end", text + "\n")

            except sr.UnknownValueError:

                text_box.delete("1.0", tk.END)
                text_box.insert(
                    "end", "Google Speech Recognition could not understand audio\n"
                )

            except sr.RequestError as e:

                text_box.delete("1.0", tk.END)
                text_box.insert(
                    "end",
                    f"Could not request results from Google Speech Recognition service; {e}\n",
                )

            except OSError as e:

                text_box.delete("1.0", tk.END)

                text_box.insert("end", f"Microphone Error: {str(e)}\n")

            finally:

                # Reset button state

                record_btn.config(text=" Record", bg=btn_color)

    # Start recognition in a separate thread to prevent UI freezing

    threading.Thread(target=recognize, daemon=True).start()


# %%
# Play Button


play_img = PhotoImage(file="./img/play-svgrepo-com.png").subsample(6, 6)


play_btn = Button(
    root,
    text=" Play",
    image=play_img,
    compound="left",
    font=main_font,
    bg=btn_color,
    fg="black",
    activebackground=btn_hover,
    width=150,
    height=50,
    relief="flat",
    command=text_to_speech,
)


play_btn.place(relx=0.5, rely=0.85, anchor="s")


play_btn.bind("<Enter>", lambda _: play_btn.config(bg=btn_hover))


play_btn.bind("<Leave>", lambda _: play_btn.config(bg=btn_color))


create_tooltip(play_btn, "Click to play the text as speech")

# %%
# Record Button


record_img = PhotoImage(file="./img/microphone-svgrepo-com.png").subsample(6, 6)


is_recording = False


def toggle_recording():
    global is_recording

    if not is_recording:

        is_recording = True

        record_btn.config(text=" Stop", bg=btn_hover)
        speech_to_text()

    else:

        is_recording = False

        record_btn.config(text=" Record", bg=btn_color)


record_btn = Button(
    root,
    text=" Record",
    image=record_img,
    compound="left",
    font=main_font,
    bg=btn_color,
    fg="black",
    activebackground=btn_hover,
    width=150,
    height=50,
    relief="flat",
    command=toggle_recording,
)


record_btn.place(relx=0.5, rely=0.75, anchor="s")


record_btn.bind("<Enter>", lambda _: record_btn.config(bg=btn_hover))


record_btn.bind("<Leave>", lambda _: record_btn.config(bg=btn_color))


create_tooltip(record_btn, "Click to record speech and convert to text")

# %% [markdown]
# #### Run the app
# ```python
# (By the way, if you are running this notebook on Google Colab it will not work because the GUI is not supported on Colab)

# %%
root.mainloop()
