import os
import customtkinter
import tkinter as tk
import yt_dlp
from playsound import playsound

configFile = 'config.txt'


def savePath(path):
    with open(configFile, 'w') as file:
        file.write(path)


def loadPath():
    if os.path.exists(configFile):
        with open(configFile, 'r') as file:
            return file.read().strip()
    return ""


def categorize_music(info):
    # Combine title, description, and keywords for better categorization
    title = info.get('title', '').lower()
    description = info.get('description', '').lower()
    keywords = [keyword.lower() for keyword in info.get('tags', [])]

    # Example categorization based on multiple metadata fields
    if any(keyword in title or keyword in description or keyword in keywords for keyword in ['rock', 'metal', 'punk']):
        return 'Rock'
    elif any(
            keyword in title or keyword in description or keyword in keywords for keyword in ['hip-hop', 'rap', 'r&b']):
        return 'Hip-Hop'
    elif any(keyword in title or keyword in description or keyword in keywords for keyword in
             ['classical', 'orchestra', 'symphony']):
        return 'Classical'
    else:
        return 'Other'


def startDownload():
    try:
        ytLink = link.get()
        print(f'Downloading {ytLink}')

        # Reset the progress bar and percentage label
        progressBar.set(0)
        progressBar.update()
        percentage_label.configure(text="0%")

        # Define the file path
        outputPath = path.get()
        if outputPath:
            savePath(outputPath)

        print(f'Downloading to path {outputPath}')

        # Extract metadata
        ydl_opts_meta = {
            'quiet': True,
            'skip_download': True,
            'format': 'bestaudio/best',
        }

        with yt_dlp.YoutubeDL(ydl_opts_meta) as ydl:
            info = ydl.extract_info(ytLink, download=False)
            category = categorize_music(info)
            outputPath = os.path.join(outputPath, category)
            os.makedirs(outputPath, exist_ok=True)
            print(f'Categorized as {category}')

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(outputPath, '%(title)s.%(ext)s'),
            'progress_hooks': [progressHook],
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'postprocessor_args': [
                '-ar', '44100'  # Set audio sample rate to 44.1 kHz
            ],
            'prefer_ffmpeg': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([ytLink])

        print(f"congrats on your loot!")

        progressBar.set(1)
        progressBar.update()
        percentage_label.configure(text="100%")

        # Play sound notification
        playsound(
            'complete.mp3')  # Ensure 'complete.wav' is in the same directory as the script or provide the full path

    except Exception as e:
        print(f"Error: {e}")


def progressHook(d):
    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes', 0)
        downloaded_bytes = d.get('downloaded_bytes', 0)
        if total_bytes > 0:
            percentage = downloaded_bytes / total_bytes
            progressBar.set(percentage)
            progressBar.update()
            percentage_label.configure(text=f"{int(percentage * 100)}%")
    elif d['status'] == 'finished':
        progressBar.set(1)
        progressBar.update()
        percentage_label.configure(text="100%")


# App Frame
app = customtkinter.CTk()
app.geometry('750x450')
app.title('Crate Digger')
app.resizable(True, True)
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

# UI Elements
title = customtkinter.CTkLabel(app, text='Insert YouTube link', font=('Helvetica', 27))
title.pack(pady=10, padx=10)

url = tk.StringVar()
link = customtkinter.CTkEntry(app, width=350, height=40, textvariable=url)
link.pack(pady=10)

download_button = customtkinter.CTkButton(app, text='Download', command=startDownload)
download_button.pack(pady=20, padx=20)

progressBar = customtkinter.CTkProgressBar(app, width=350, height=40)
progressBar.pack(pady=20, padx=20)
progressBar.set(0)

percentage_label = customtkinter.CTkLabel(app, text="0%", font=('Helvetica', 18))
percentage_label.pack(pady=10)

pathLabel = customtkinter.CTkLabel(app, text='Insert download path', font=('Helvetica', 27))
pathLabel.pack(pady=10, padx=10)
path = tk.StringVar()
pathEntry = customtkinter.CTkEntry(app, width=350, height=40, textvariable=path)
pathEntry.pack(pady=10)

# Load the saved path if it exists
savedPath = loadPath()
if savedPath:
    path.set(savedPath)

# Run app
app.mainloop()
