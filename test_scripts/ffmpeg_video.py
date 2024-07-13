import ffmpeg
import os


def main(source, video_duration):
    args = {
        "rtsp_transport": "tcp",
        "flags": "low_delay",
        "fflags": "nobuffer",
    }
    (ffmpeg.input(source, **args)
     .output('video.mp4', format='mp4', t=video_duration)
     .overwrite_output()
     .run())


if __name__ == "__main__":
    rtsp_url = os.getenv("RTSP_URL")
    video_duration = os.getenv("VIDEO_DURATION", default=10)

    main(rtsp_url, video_duration)
