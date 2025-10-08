import json
import os

import ffmpeg


def probe_rtsp(url: str):
    try:
        probe = ffmpeg.probe(
            url,
            v='error',
            select_streams='v:0',
            show_entries='stream=codec_name,codec_type,profile,pix_fmt,width,height,r_frame_rate,avg_frame_rate,bit_rate',
            of='json'
        )
        data = json.loads(json.dumps(probe))  # garante dict limpo
        stream = data.get('streams', [{}])[0]
        codec = stream.get('codec_name')
        print("=== Informações de Vídeo ===")
        print(f"Codec: {codec}")
        print(f"Profile: {stream.get('profile')}")
        print(f"Resolução: {stream.get('width')}x{stream.get('height')}")
        print(f"r_frame_rate: {stream.get('r_frame_rate')}")
        print(f"avg_frame_rate: {stream.get('avg_frame_rate')}")
        print(f"Pixel format: {stream.get('pix_fmt')}")
        print(f"Bitrate (reportado): {stream.get('bit_rate')}")
        # Heurística para sugerir se pode usar copy
        if codec in {"h264", "hevc"}:
            print("Sugestão: Você pode testar FFMPEG_VCODEC=copy para reduzir CPU.")
        else:
            print("Provavelmente será necessário transcodificar (libx264, etc.).")
    except ffmpeg.Error as e:
        print("Falha no probe:")
        print(e.stderr.decode(errors='ignore') if e.stderr else e)
    except Exception as e:
        print(f"Erro inesperado: {e}")


def main():
    url = os.getenv('RTSP_URL')
    if not url:
        print("Defina RTSP_URL antes de rodar.")
        return
    probe_rtsp(url)


if __name__ == '__main__':
    main()

