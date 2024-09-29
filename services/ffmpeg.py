import os
from datetime import datetime

from ffmpeg.ffmpeg import FFmpeg
from ffmpeg.progress import Progress

RTSP_URL = os.getenv("RTSP_URL")
VIDEO_TIME = os.getenv("VIDEO_TIME", default=20)


def generate_video():
    try:
        filename = f"video_{int(datetime.now().timestamp())}.mp4"

        ffmpeg = (FFmpeg()
                  .option("y")  # Overwrite output files
                  .input(RTSP_URL, rtsp_transport="udp")
                  .output(filename, vcodec="libx264", preset="ultrafast", r=24)
                  )

        @ffmpeg.on("progress")
        def time_to_terminate(progress: Progress):
            print(progress)
            if progress.time.seconds >= int(VIDEO_TIME):
                ffmpeg.terminate()

        ffmpeg.execute()
        return filename
    except Exception as e:
        print(f"Error generating video: {e}")
        raise e


def remove_video(filename):
    try:
        os.remove(filename)
    except Exception as e:
        print(f"Error removing video: {e}")
        raise e


def remove_old_videos():
    try:
        for filename in os.listdir():
            if filename.startswith("video_"):
                os.remove(filename)
    except Exception as e:
        print(f"Error removing old videos: {e}")
        raise e
