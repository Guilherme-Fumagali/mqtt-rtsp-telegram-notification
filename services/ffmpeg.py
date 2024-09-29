import os
from datetime import datetime

import ffmpeg

RTSP_URL = os.getenv("RTSP_URL")
VIDEO_TIME = os.getenv("VIDEO_TIME", default=20)


def generate_video():
    try:
        filename = f"video_{int(datetime.now().timestamp())}.mp4"

        (ffmpeg.input(RTSP_URL, rtsp_transport="udp")
         .output(filename, vcodec="libx264", preset="ultrafast", r=24, format="mp4", t=VIDEO_TIME)
         .overwrite_output()
         .run())

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
