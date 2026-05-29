# backend.prompt.md — Estrutura Inicial do Backend

## Contexto

Estou criando uma plataforma chamada inicialmente **Sport AI Platform**.

A plataforma será voltada para análise esportiva por vídeo com IA, começando pelo esporte **Crossfit**.

Neste primeiro momento, o backend deve ser responsável apenas por:

1. Subir uma API com FastAPI
2. Receber upload de vídeos
3. Validar arquivos de vídeo
4. Salvar vídeos localmente
5. Retornar um identificador único do vídeo
6. Permitir consultar informações básicas de um vídeo enviado

Não implementar análise com IA ainda.

---

## Stack obrigatória

- Python 3.11
- FastAPI
- Uvicorn
- python-multipart
- Pydantic
- Estrutura modular simples

---

## Objetivo da implementação

Criar uma API backend inicial, limpa e organizada, pronta para receber vídeos do frontend.

O frontend está rodando em:

```txt
http://localhost:3000
```

A API deve rodar em:

```txt
http://localhost:8000
```

---

## Estrutura esperada do projeto

Criar a seguinte estrutura dentro da pasta `backend`:

```txt
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── videos.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── video_service.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── video_schema.py
│   └── uploads/
├── requirements.txt
└── README.md
```

---

## Responsabilidade de cada arquivo

### `app/main.py`

Arquivo principal da API.

Deve conter:

- criação da aplicação FastAPI
- configuração de CORS
- rota `/health`
- inclusão das rotas de vídeos

---

### `app/core/config.py`

Arquivo central de configurações.

Deve conter:

- diretório base do projeto
- diretório de uploads
- tamanho máximo permitido para vídeos
- extensões permitidas
- content types permitidos

---

### `app/routes/videos.py`

Arquivo responsável pelas rotas de vídeo.

Deve conter:

- `POST /videos/upload`
- `GET /videos/{video_id}`

As rotas devem apenas receber a requisição e chamar o service.

Não colocar regra de negócio pesada nas rotas.

---

### `app/services/video_service.py`

Arquivo responsável pela regra de negócio dos vídeos.

Deve conter funções para:

- validar extensão do arquivo
- validar content type
- validar tamanho máximo
- salvar vídeo localmente
- gerar UUID para o vídeo
- consultar vídeo salvo

---

### `app/schemas/video_schema.py`

Arquivo responsável pelos modelos de resposta.

Deve conter schemas Pydantic para:

- resposta do upload
- resposta da consulta de vídeo

---

### `app/uploads/`

Pasta onde os vídeos enviados serão salvos localmente.

---

## Regras de validação

O upload deve aceitar apenas arquivos de vídeo.

### Extensões permitidas

```txt
mp4
mov
avi
mkv
webm
```

### Content types permitidos

```txt
video/mp4
video/quicktime
video/x-msvideo
video/x-matroska
video/webm
```

### Tamanho máximo

```txt
200MB
```

Se o arquivo enviado não for válido, retornar erro `400`.

Se o vídeo não for encontrado em uma consulta, retornar erro `404`.

Se ocorrer erro inesperado, retornar erro `500`.

---

## Endpoints esperados

### Health check

```http
GET /health
```

Resposta esperada:

```json
{
  "status": "ok"
}
```

---

### Upload de vídeo

```http
POST /videos/upload
```

Tipo da requisição:

```txt
multipart/form-data
```

Campo esperado:

```txt
file
```

Resposta esperada:

```json
{
  "message": "Vídeo recebido com sucesso",
  "videoId": "uuid-do-video",
  "filename": "uuid-do-video.mp4",
  "originalFilename": "meu-video.mp4",
  "contentType": "video/mp4",
  "size": 1024000,
  "path": "app/uploads/uuid-do-video.mp4"
}
```

---

### Consultar vídeo

```http
GET /videos/{video_id}
```

Resposta esperada:

```json
{
  "videoId": "uuid-do-video",
  "filename": "uuid-do-video.mp4",
  "exists": true,
  "path": "app/uploads/uuid-do-video.mp4"
}
```

---

## Implementação esperada

### `requirements.txt`

Criar com:

```txt
fastapi
uvicorn
python-multipart
```

---

### `app/core/config.py`

Implementar algo equivalente a:

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"

MAX_VIDEO_SIZE_MB = 200
MAX_VIDEO_SIZE_BYTES = MAX_VIDEO_SIZE_MB * 1024 * 1024

ALLOWED_EXTENSIONS = {"mp4", "mov", "avi", "mkv", "webm"}

ALLOWED_CONTENT_TYPES = {
    "video/mp4",
    "video/quicktime",
    "video/x-msvideo",
    "video/x-matroska",
    "video/webm",
}
```

---

### `app/main.py`

Deve:

- criar `app = FastAPI(...)`
- configurar CORS para `http://localhost:3000`
- criar rota `/health`
- importar e registrar `videos_router`

Exemplo de comportamento esperado:

```python
app.include_router(videos_router, prefix="/videos", tags=["Videos"])
```

---

### `app/schemas/video_schema.py`

Criar schemas:

```python
from pydantic import BaseModel


class VideoUploadResponse(BaseModel):
    message: str
    videoId: str
    filename: str
    originalFilename: str
    contentType: str
    size: int
    path: str


class VideoInfoResponse(BaseModel):
    videoId: str
    filename: str
    exists: bool
    path: str
```

---

### `app/services/video_service.py`

Implementar as funções:

```python
async def save_video(file: UploadFile) -> dict:
    pass
```

```python
def get_video_info(video_id: str) -> dict:
    pass
```

```python
def validate_video_extension(filename: str) -> str:
    pass
```

```python
def validate_video_content_type(content_type: str) -> None:
    pass
```

Regras:

- gerar UUID para o arquivo
- preservar extensão original
- salvar arquivo em `app/uploads`
- criar pasta de uploads caso não exista
- validar extensão
- validar content type
- validar tamanho máximo de 200MB
- retornar dados do vídeo salvo

---

### `app/routes/videos.py`

Criar as rotas:

```python
@router.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    pass
```

```python
@router.get("/{video_id}")
def get_video(video_id: str):
    pass
```

As rotas devem chamar as funções do service.

---

## Critérios de aceite

A implementação estará pronta quando:

- a API subir com `python -m uvicorn app.main:app --reload`
- `/health` retornar `{ "status": "ok" }`
- Swagger abrir em `http://localhost:8000/docs`
- `POST /videos/upload` aceitar vídeo válido
- `POST /videos/upload` rejeitar arquivo inválido
- vídeo for salvo em `app/uploads`
- API retornar `videoId`
- `GET /videos/{video_id}` retornar informações do vídeo
- código estiver separado em `routes`, `services`, `schemas` e `core`

---

## Comandos para rodar

Criar ambiente virtual:

```bash
python -m venv venv
```

Ativar no Windows:

```bash
venv\Scripts\activate
```

Instalar dependências:

```bash
pip install -r requirements.txt
```

Rodar API:

```bash
python -m uvicorn app.main:app --reload
```

---

## Não implementar agora

Não implementar neste momento:

- autenticação
- banco de dados
- Docker
- testes automatizados
- OpenCV
- MediaPipe
- IA real
- análise de biomecânica
- filas/background jobs
- upload para cloud
- dashboard
- login de usuário

Esses pontos serão tratados em etapas futuras.
