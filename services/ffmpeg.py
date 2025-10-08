import logging
import os
import subprocess
from datetime import datetime
from uuid import uuid4

VIDEO_DIR = os.getenv("VIDEO_TMP_DIR") or "/dev/shm"
if not os.path.isdir(VIDEO_DIR):
    VIDEO_DIR = "."

logger = logging.getLogger(__name__)


def _unique_filename():
    return f"video_{datetime.now().strftime('%Y%m%dT%H%M%S')}_{uuid4().hex[:8]}"


def compress_video(input_path: str, compress_args: str | None = None) -> str:
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: {input_path}")

    if not compress_args:
        return input_path

    original_size = os.path.getsize(input_path)

    base, ext = os.path.splitext(input_path)
    compressed_path = f"{base}_compressed{ext}"

    cmd = ["ffmpeg", "-i", input_path, *compress_args.split(), "-y", compressed_path]

    logger.info("Iniciando compressão do vídeo", extra={
        "file": input_path,
        "original_size_mb": round(original_size / 1024 / 1024, 2)
    })

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=120)

        if not os.path.isfile(compressed_path) or os.path.getsize(compressed_path) == 0:
            raise RuntimeError("Arquivo comprimido não foi gerado ou está vazio")

        compressed_size = os.path.getsize(compressed_path)
        reduction_pct = round((1 - compressed_size / original_size) * 100, 1)

        logger.info("Compressão concluída", extra={
            "file": compressed_path,
            "original_size_mb": round(original_size / 1024 / 1024, 2),
            "compressed_size_mb": round(compressed_size / 1024 / 1024, 2),
            "reduction_percent": reduction_pct
        })

        try:
            os.remove(input_path)
            logger.debug("Arquivo original removido após compressão", extra={"file": input_path})
        except Exception as e:
            logger.warning("Erro removendo arquivo original", extra={"file": input_path, "error": str(e)})

        return compressed_path

    except subprocess.TimeoutExpired:
        logger.error("Timeout na compressão do vídeo", extra={"file": input_path})

        if os.path.isfile(compressed_path):
            try:
                os.remove(compressed_path)
            except OSError:
                pass
        raise RuntimeError("Timeout ao comprimir vídeo")
    except subprocess.CalledProcessError as e:
        logger.error("Erro no ffmpeg durante compressão", extra={
            "file": input_path,
            "stderr": e.stderr[-400:] if e.stderr else ""
        })
        if os.path.isfile(compressed_path):
            try:
                os.remove(compressed_path)
            except OSError:
                pass
        raise RuntimeError(f"Falha ao comprimir vídeo: {e.stderr[-400:] if e.stderr else 'erro desconhecido'}")


def generate_video(rtsp_url: str, input_args: str, output_args: str, compress_args: str | None = None) -> str:
    if not rtsp_url:
        raise ValueError("RTSP_URL não definida e nenhum rtsp_url fornecido")

    basename = _unique_filename()
    filename = f"{basename}.mp4"
    full_path = os.path.join(VIDEO_DIR, filename)

    cmd = ["ffmpeg", *input_args.split(), "-i", rtsp_url, *output_args.split(), "-y", full_path]

    logger.info("Executando ffmpeg", extra={"cmd": " ".join(cmd)})
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        logger.error("Erro no ffmpeg", extra={"stderr": e.stderr[-400:]})
        raise RuntimeError(f"FFmpeg falhou: {e.stderr[-400:]}")

    if not os.path.isfile(full_path) or os.path.getsize(full_path) == 0:
        raise RuntimeError("Arquivo não gerado ou vazio")

    logger.info("Captura concluída", extra={"file": full_path, "size": os.path.getsize(full_path)})

    try:
        full_path = compress_video(full_path, compress_args)
    except Exception as e:
        logger.warning("Falha na compressão, usando vídeo original", extra={"error": str(e)})

    return full_path

def remove_video(filename):
    try:
        os.remove(filename)
        logger.debug("Arquivo removido", extra={"file": filename})
    except FileNotFoundError:
        logger.warning("Arquivo para remover não encontrado", extra={"file": filename})
    except Exception:
        logger.exception("Erro removendo vídeo", extra={"file": filename})
        raise


def remove_old_videos():
    try:
        for fname in os.listdir(VIDEO_DIR):
            if fname.startswith("video_"):
                try:
                    os.remove(os.path.join(VIDEO_DIR, fname))
                    logger.debug("Vídeo antigo removido", extra={"file": fname})
                except FileNotFoundError:
                    logger.warning("Vídeo antigo já não existe", extra={"file": fname})
                except Exception:
                    logger.exception("Erro removendo vídeo antigo", extra={"file": fname})
    except Exception:
        logger.exception("Erro listando/removendo vídeos antigos")
        raise
