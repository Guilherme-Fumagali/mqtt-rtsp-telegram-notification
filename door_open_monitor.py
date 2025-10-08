import asyncio
import logging
import os
import signal
import threading
from datetime import datetime

import paho.mqtt.client as mqtt

import services.logging_config as logging_config
from services.config import Config
from services.ffmpeg import remove_old_videos
from services.gotify import send_gotify_message
from services.recorder_service import MultiCameraRecorder
from services.telegram import send_videos

logging_config.setup_logging()
logger = logging.getLogger(__name__)

config = Config()

_recording_lock = threading.Lock()
recorder = MultiCameraRecorder(config)
_shutdown = False

send_gotify_message("Starting", "Starting ffmpeg_mqtt_listener.py")
logger.info("Aplicação iniciando", extra=config.to_dict_redacted())


def _ensure_event_loop():
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return loop, False
        return loop, False
    except RuntimeError:
        loop = asyncio.new_event_loop()
        return loop, True


def _build_caption(success_results):
    labels = [r.camera_label for r in success_results]
    label_line = ", ".join(labels)
    return f"Portão aberto!\nData: {datetime.now()}\nCâmeras: {len(success_results)}\nLabels: {label_line}"


def _record_and_send_batch():
    results = []
    try:
        results = recorder.capture_all()
        success = [r for r in results if r.ok and r.file_path]
        if not success:
            raise RuntimeError("Nenhum vídeo gerado com sucesso")
        caption = _build_caption(success)
        files = [r.file_path for r in success if r.file_path]

        loop, must_close = _ensure_event_loop()
        try:
            if loop.is_running():
                logger.debug("Loop asyncio ativo - criando task para envio (grupo)")
                task = loop.create_task(send_videos(files, caption))
                def _after(t: asyncio.Task):
                    try:
                        from services.recorder_service import MultiCameraRecorder
                        MultiCameraRecorder.cleanup_files(success)
                        logger.debug("Arquivos removidos após envio", extra={"count": len(files)})
                    except Exception:
                        logger.exception("Erro ao remover arquivos após envio")
                task.add_done_callback(_after)
            else:
                logger.debug("Executando envio síncrono (grupo)")
                loop.run_until_complete(send_videos(files, caption))
                from services.recorder_service import MultiCameraRecorder
                MultiCameraRecorder.cleanup_files(success)
                logger.debug("Arquivos removidos após envio (modo síncrono)")
        finally:
            if must_close:
                loop.close()
        logger.info("Processo de gravação+envio concluído", extra={"arquivos": len(success)})
    except Exception as e:
        logger.exception("Erro durante processo multi-câmera")
        send_gotify_message("Error", f"Erro multi-câmera: {e}")
        from services.recorder_service import MultiCameraRecorder
        MultiCameraRecorder.cleanup_files(results)
    finally:
        if _recording_lock.locked():
            _recording_lock.release()
            logger.debug("Lock de gravação liberado")


def on_connect(client, userdata, flags, reason_code, properties):
    logger.info("Conectado ao broker MQTT", extra={"reason_code": reason_code})
    if config.mqtt_topic:
        client.subscribe(config.mqtt_topic)
        send_gotify_message("Started", f"Connected MQTT rc={reason_code} topic={config.mqtt_topic}")
    else:
        logger.error("MQTT_TOPIC não definido - não será feito subscribe")


def on_message(client, userdata, message):
    payload = getattr(message, 'payload', b'')
    if payload == b"open":
        if not _recording_lock.acquire(blocking=False):
            logger.info("Mensagem 'open' descartada - gravação em andamento")
            return
        if not config.rtsp_urls:
            logger.error("Nenhuma câmera configurada - abortando evento")
            _recording_lock.release()
            return
        logger.info(
            "Mensagem 'open' aceita - iniciando batch",
            extra={"cameras": len(config.rtsp_urls)}
        )
        t = threading.Thread(target=_record_and_send_batch, name="multi-video-recorder", daemon=True)
        t.start()
    else:
        logger.debug("Mensagem ignorada", extra={"payload": payload[:32]})


def _graceful_shutdown(*_):
    global _shutdown
    if _shutdown:
        return
    _shutdown = True
    logger.info("Recebido sinal de término - finalizando...")
    try:
        recorder.shutdown()
    except Exception:
        logger.exception("Erro encerrando recorder")
    try:
        remove_old_videos()
    except Exception:
        logger.exception("Erro limpando vídeos no shutdown")
    os._exit(0)

for sig in (signal.SIGINT, signal.SIGTERM):
    try:
        signal.signal(sig, _graceful_shutdown)
    except Exception:
        pass

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

if config.mqtt_user or config.mqtt_pass:
    mqttc.username_pw_set(config.mqtt_user, config.mqtt_pass)

try:
    remove_old_videos()
    logger.debug("Limpeza de vídeos antigos executada")
    if not config.mqtt_host:
        raise RuntimeError("MQTT_HOST não definido")
    mqttc.connect(config.mqtt_host, 1883, 60)
    logger.info("Entrando no loop principal MQTT")
    mqttc.loop_forever(30, True)
except Exception as e:
    logger.exception("Erro fatal na aplicação")
    send_gotify_message("Crash", f"Error: {e}")
    _graceful_shutdown()
