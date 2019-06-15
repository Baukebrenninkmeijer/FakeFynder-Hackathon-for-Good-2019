from pytube import YouTube

def download_video(link):
    yt = YouTube(link)
    yt.streams.filter(progressive=True).order_by('resolution').desc().first().download()

# if __name__ == "__main__":
# 	download_video('https://www.youtube.com/watch?v=cQ54GDm1eL0')
