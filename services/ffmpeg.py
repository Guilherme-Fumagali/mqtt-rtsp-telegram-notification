import os
from io import BytesIO

import ffmpeg

from services.gotify import send_gotify_message

RTSP_URL = os.getenv("RTSP_URL")
VIDEO_TIME = os.getenv("VIDEO_TIME", default=20)


def generate_video():
    args = {
        "rtsp_transport": "tcp",
        "flags": "low_delay",
        "fflags": "nobuffer",
    }

    video_buffer = BytesIO()

    try:
        (ffmpeg.input(RTSP_URL, **args)
         .output('pipe:', format='mp4', t=VIDEO_TIME)
         .overwrite_output()
         .run(pipe_stdout=True, pipe_stderr=True, output=video_buffer))

        video_buffer.seek(0)
        return video_buffer
    except Exception as e:
        print(f"Error generating video: {e}")
        send_gotify_message("Error generating video", f"Error generating video: {e}")
        raise e
