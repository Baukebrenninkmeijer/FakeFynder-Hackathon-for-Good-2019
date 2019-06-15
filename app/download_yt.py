from pytube import YouTube

def download_video(link):
    yt = YouTube(link)
    yt.streams.filter(progressive=True).order_by('resolution').desc().first().download()
    