from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Optional

from .config import Config
from .ffmpeg import generate_video, remove_video

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class VideoResult:
    camera_label: str
    url: str
    file_path: Optional[str]
    ok: bool
    error: Optional[str] = None


class MultiCameraRecorder:
    def __init__(self, config: Config):
        self.config = config
        self._executor = ThreadPoolExecutor(
            max_workers=len(config.rtsp_urls),
            thread_name_prefix="cam-rec"
        )

    def shutdown(self):
        self._executor.shutdown(wait=False, cancel_futures=True)

    def capture_all(self) -> List[VideoResult]:
        urls = self.config.rtsp_urls
        labels = self.config.camera_labels
        if not urls:
            raise ValueError("Nenhuma câmera configurada")

        logger.info(
            "Iniciando captura paralela",
            extra={"cameras": len(urls), "labels": labels}
        )

        futures = {}
        for url, label in zip(urls, labels):
            futures[self._executor.submit(
                generate_video,
                url,
                self.config.ffmpeg_input_args,
                self.config.ffmpeg_output_args,
                self.config.ffmpeg_compress_args
            )] = (url, label)

        results: List[VideoResult] = []
        for fut in as_completed(futures):
            url, label = futures[fut]
            safe_tag = url.split('@')[-1][:60]
            try:
                path = fut.result()
                logger.info("Captura concluída", extra={"camera": safe_tag, "label": label, "file": path})
                results.append(VideoResult(label, url, path, True))
            except Exception as e:
                logger.error("Falha capturando câmera", extra={"camera": safe_tag, "label": label, "error": str(e)})
                results.append(VideoResult(label, url, None, False, str(e)))
        ok = sum(1 for r in results if r.ok)
        fail = len(results) - ok
        if fail:
            logger.warning("Captura finalizada com erros", extra={"ok": ok, "falhas": fail})
        return results

    @staticmethod
    def cleanup_files(results: List[VideoResult]):
        for r in results:
            if r.file_path:
                try:
                    remove_video(r.file_path)
                except Exception:
                    logger.exception("Erro removendo arquivo", extra={"file": r.file_path})
