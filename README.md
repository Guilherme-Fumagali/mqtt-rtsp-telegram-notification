# mqtt-rtsp-telegram-notification

Sistema que escuta um tópico MQTT e, ao receber a mensagem `open`, grava vídeos de câmeras RTSP em paralelo e envia para o Telegram.

---

## Requisitos
- Python 3.11+ (ou use Docker)
- ffmpeg instalado (caso rode fora de container)
- Câmeras RTSP acessíveis
- Broker MQTT acessível
- Bot do Telegram (TOKEN + CHAT_ID)

---

## Variáveis de Ambiente

### **Obrigatórias**

#### MQTT
- `MQTT_HOST` - Endereço do broker MQTT (ex: `192.168.1.10`)
- `MQTT_TOPIC` - Tópico MQTT a escutar (ex: `casa/portao`)

#### RTSP
- `RTSP_URLS` - URLs das câmeras RTSP separadas por vírgula (ex: `rtsp://user:pass@192.168.0.10/stream,rtsp://user:pass@192.168.0.11/stream`)

#### FFmpeg
- `FFMPEG_INPUT_ARGS` - Argumentos de entrada do ffmpeg (ex: `-rtsp_transport tcp -analyzeduration 0 -probesize 500000 -fflags nobuffer+genpts`)
- `FFMPEG_OUTPUT_ARGS` - Argumentos de saída do ffmpeg (ex: `-c copy -map 0 -t 15 -copyinkf -reset_timestamps 1 -movflags +faststart`)

#### Telegram (obrigatório se usar notificação)
- `BOT_TOKEN` - Token do bot do Telegram
- `BOT_CHAT_ID` - ID do chat para enviar vídeos (obrigatório quando `BOT_TOKEN` estiver definido)

### **Opcionais**

#### MQTT
- `MQTT_USERNAME` - Usuário MQTT (se necessário autenticação)
- `MQTT_PASSWORD` - Senha MQTT (se necessário autenticação)

#### RTSP
- `RTSP_LABELS` - Labels das câmeras separadas por vírgula (ex: `Frente,Garagem`). Se não definido, usa `Cam1, Cam2, ...`

#### FFmpeg
- `FFMPEG_COMPRESS_ARGS` - Argumentos para compressão do vídeo (ex: `-c:v libx264 -crf 32 -preset fast -c:a aac -b:a 128k -movflags +faststart -vf scale=720:-1,fps=15 -maxrate 1M -bufsize 2M`)

#### Outros
- `VIDEO_TMP_DIR` - Diretório temporário para vídeos (padrão: `/dev/shm` ou `.`)
- `LOG_LEVEL` - Nível de log: `DEBUG`, `INFO`, `WARNING`, `ERROR` (padrão: `INFO`)

#### Gotify (opcional)
- `GOTIFY_URL` - URL do servidor Gotify
- `GOTIFY_TOKEN` - Token Gotify (obrigatório quando `GOTIFY_URL` estiver definido)

---

## Exemplo de .env

```env
# MQTT (obrigatório)
MQTT_HOST=192.168.1.10
MQTT_TOPIC=casa/portao
MQTT_USERNAME=usuario
MQTT_PASSWORD=senha

# RTSP (obrigatório)
RTSP_URLS=rtsp://user:pass@192.168.0.10/stream,rtsp://user:pass@192.168.0.11/stream
RTSP_LABELS=Frente,Garagem

# FFmpeg (obrigatório)
FFMPEG_INPUT_ARGS=-rtsp_transport tcp -analyzeduration 0 -probesize 500000 -fflags nobuffer+genpts -use_wallclock_as_timestamps 1
FFMPEG_OUTPUT_ARGS=-c copy -map 0 -t 15 -copyinkf -reset_timestamps 1 -movflags +faststart

# Compressão (opcional - acelera envio)
FFMPEG_COMPRESS_ARGS=-c:v libx264 -crf 32 -preset fast -c:a aac -b:a 128k -movflags +faststart -vf scale=720:-1,fps=15 -maxrate 1M -bufsize 2M

# Telegram (obrigatório)
BOT_TOKEN=XXXXXXXX:YYYYY
BOT_CHAT_ID=123456789

# Outros (opcionais)
VIDEO_TMP_DIR=/dev/shm
LOG_LEVEL=INFO

# Gotify (opcional)
GOTIFY_URL=https://gotify.exemplo.com
GOTIFY_TOKEN=seu_token_aqui
```

---

## Execução Local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export MQTT_HOST=192.168.1.10
export MQTT_TOPIC=casa/portao
export RTSP_URLS="rtsp://user:pass@192.168.0.10/stream"
export FFMPEG_INPUT_ARGS="-rtsp_transport tcp -analyzeduration 0 -probesize 500000"
export FFMPEG_OUTPUT_ARGS="-c copy -t 15 -movflags +faststart"
export BOT_TOKEN="XXXX:YYYY"
export BOT_CHAT_ID="123456789"

python door_open_monitor.py
```

---

## Execução com Docker

```bash
# Criar .env baseado no exemplo acima
docker build -t mqtt-rtsp-telegram:latest .

docker run --rm \
  --name mqtt-rtsp-telegram \
  --env-file .env \
  --shm-size=256m \
  mqtt-rtsp-telegram:latest
```

Ou via docker compose:
```bash
docker compose up -d --build
docker logs -f mqtt-rtsp-telegram
```

---

## Compressão de Vídeo

O sistema suporta compressão automática dos vídeos antes do envio ao Telegram, acelerando significativamente o upload.

Para ativar, defina `FFMPEG_COMPRESS_ARGS`:

```env
# Compressão rápida com qualidade média
FFMPEG_COMPRESS_ARGS=-c:v libx264 -crf 32 -preset fast -c:a aac -b:a 128k -movflags +faststart -vf scale=720:-1,fps=15 -maxrate 1M -bufsize 2M

# Compressão mais agressiva (menor tamanho)
FFMPEG_COMPRESS_ARGS=-c:v libx264 -crf 35 -preset faster -c:a aac -b:a 96k -movflags +faststart -vf scale=640:-1,fps=12 -maxrate 800k -bufsize 1600k
```

Se não definido, o vídeo original é enviado sem compressão.

---

## Observações

- Media group do Telegram suporta no máximo 10 vídeos
- Vídeos temporários são armazenados em `/dev/shm` (RAM) quando disponível
- Use `-copyinkf` nos `FFMPEG_OUTPUT_ARGS` para evitar erros de keyframe
- O sistema usa lock para garantir que apenas uma gravação ocorra por vez
- Logs estruturados em JSON quando necessário

---

## Fluxo de Funcionamento

1. Aplicação conecta ao broker MQTT
2. Escuta mensagens no tópico configurado
3. Ao receber `open`, inicia gravação paralela de todas as câmeras
4. Cada vídeo é gravado e opcionalmente comprimido
5. Vídeos são enviados ao Telegram (em media group se múltiplos)
6. Arquivos temporários são removidos automaticamente
7. Notificação Gotify enviada (se configurado)

---

## Licença

Uso pessoal / interno. Ajuste conforme necessidade.
