# Sport AI API - Backend

API inicial da Sport AI Platform para receber e armazenar localmente videos
de treino. A API extrai metadados tecnicos com OpenCV, salva frames, detecta
landmarks com MediaPipe e calcula metricas biomecanicas de Crossfit/squat
considerando o angulo escolhido no upload: frontal ou lateral. A partir delas,
segmenta repeticoes, calcula scores, gera feedback acionavel e permite
consultar o resultado real consolidado.

## Tecnologias

- Python 3.11
- FastAPI
- Uvicorn
- python-multipart
- OpenCV
- MediaPipe
- Pydantic, instalado como dependencia do FastAPI

## Funcionalidades

- Health check da API.
- Upload de videos com identificador UUID, `exerciseType` e `cameraView`.
- Validacao de extensao, content type e limite de 200 MB.
- Armazenamento local em `app/uploads/`.
- Consulta dos dados basicos de um video salvo.
- Processamento inicial para extrair FPS, frames, duracao, resolucao e tamanho.
- Extracao configuravel de frames JPEG para `app/outputs/`.
- Deteccao de pose nos frames e persistencia de landmarks em JSON.
- Calculo de metricas frontais ou laterais do squat conforme `cameraView`.
- Analise temporal para identificar repeticoes e metricas por rep.
- AXON Movement Score versionado com sub-scores, confianca e score type por
  angulo de camera.
- Feedback deterministico com pontos fortes, melhorias e recomendacoes.
- Consulta consolidada da analise real persistida para um video processado.
- CORS habilitado para `http://localhost:3000`.

## Estrutura

```txt
backend/
  app/
    core/
      config.py              # Configuracao de upload e validacoes
    routes/
      videos.py              # Endpoints de videos
      analysis.py            # Consulta consolidada do resultado real
      processing.py          # Endpoint de processamento tecnico
      frames.py              # Endpoint de extracao de frames
      pose.py                # Endpoint de deteccao de pose
      metrics.py             # Endpoint de metricas biomecanicas
      movement.py            # Endpoint de analise temporal
      scoring.py             # Endpoint de score biomecanico
      feedback.py            # Endpoint de feedback acionavel
    schemas/
      video_schema.py        # Modelos de resposta
      analysis_schema.py     # Modelo do relatorio consolidado
      processing_schema.py   # Modelo dos metadados reais
      frame_schema.py        # Modelo da extracao de frames
      pose_schema.py         # Modelo da deteccao de pose
      metrics_schema.py      # Modelo de metricas reais
      movement_schema.py     # Modelo das repeticoes
      scoring_schema.py      # Modelo do score final
      feedback_schema.py     # Modelo do feedback final
    services/
      video_service.py       # Validacao, armazenamento e consulta
      analysis_service.py    # Leitura dos artefatos do relatorio
      video_processing_service.py # Extracao de metadados via OpenCV
      frame_extraction_service.py # Extracao local de JPEGs
      pose_detection_service.py # Landmarks via MediaPipe
      biomechanics_service.py # Angulos e metricas do squat
      movement_analysis_service.py # Segmentacao temporal das reps
      scoring_service.py     # Integracao do score com artefatos persistidos
      feedback_service.py    # Regras de feedback e fadiga
    modules/
      biomechanics/          # Metricas laterais e helpers biometricos
      scoring/               # AXON Movement Score versionado
    uploads/                 # Videos locais, ignorados pelo Git
    outputs/                 # Frames locais, ignorados pelo Git
    main.py                  # Aplicacao FastAPI e health check
  requirements.txt
  requirements-dev.txt
  README.md
```

## Como executar

A partir da pasta `backend`, crie e ative o ambiente virtual no Windows:

```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

Em Linux ou macOS:

```bash
python3.11 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

Para instalar as dependencias de teste e executar a suite automatizada:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest
```

A API estara acessivel em `http://localhost:8000`.

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testes no Postman

Importe o arquivo `Sport-AI-API.postman_collection.json` no Postman. A
collection ja utiliza `http://localhost:8000` como `baseUrl` e contem:

- `Health Check`
- `Upload Video`
- `Get Video Info`
- `Process Video`
- `Process Video - Not Found`
- `Extract Frames`
- `Extract Frames - Invalid Interval`
- `Extract Frames - Not Found`
- `Detect Pose`
- `Detect Pose - Frames Not Found`
- `Detect Pose - Video Not Found`
- `Calculate Metrics`
- `Calculate Metrics - Landmarks Not Found`
- `Analyze Movement`
- `Analyze Movement - Landmarks Not Found`
- `Calculate Score`
- `Calculate Score - Movement Not Found`
- `Generate Feedback`
- `Generate Feedback - Scoring Not Found`
- `Get Analysis`
- `Get Video Info - Not Found`

No request `Upload Video`, selecione um video valido no campo `file` e envie
`cameraView` como `front` ou `side`. Apos o upload, o teste da collection
armazena automaticamente o `videoId` retornado, que sera usado nos requests de
consulta, processamento, frames, pose, metricas, movimento e analise.
Para gerar score, execute `Analyze Movement` antes de `Calculate Score`. Para
gerar feedback, execute `Calculate Score` antes de `Generate Feedback`.
Para consultar a analise consolidada, execute a pipeline ate
`Generate Feedback` antes de `Get Analysis`.

## Endpoints

### Health check

```http
GET /health
```

Resposta:

```json
{
  "status": "ok"
}
```

### Upload de video

```http
POST /videos/upload
Content-Type: multipart/form-data
```

O arquivo deve ser enviado no campo `file`. Tambem envie `exerciseType=squat`
e `cameraView=front` ou `cameraView=side`.

```bash
curl -X POST http://localhost:8000/videos/upload \
  -F "file=@treino.mp4" \
  -F "exerciseType=squat" \
  -F "cameraView=side"
```

Resposta:

```json
{
  "message": "V\u00eddeo recebido com sucesso",
  "videoId": "6d5245c2-c036-43dc-8ee3-db5b5c9143ab",
  "filename": "6d5245c2-c036-43dc-8ee3-db5b5c9143ab.mp4",
  "originalFilename": "treino.mp4",
  "contentType": "video/mp4",
  "size": 1024000,
  "path": "app/uploads/6d5245c2-c036-43dc-8ee3-db5b5c9143ab.mp4",
  "exerciseType": "squat",
  "cameraView": "side"
}
```

Extensoes aceitas: `mp4`, `mov`, `avi`, `mkv` e `webm`.

Content types aceitos: `video/mp4`, `video/quicktime`, `video/x-msvideo`,
`video/x-matroska` e `video/webm`.

Arquivos invalidos, maiores que 200 MB ou `cameraView` ausente/invalido
retornam `400`.

### Consultar video

```http
GET /videos/{video_id}
```

```bash
curl http://localhost:8000/videos/6d5245c2-c036-43dc-8ee3-db5b5c9143ab
```

Resposta:

```json
{
  "videoId": "6d5245c2-c036-43dc-8ee3-db5b5c9143ab",
  "filename": "6d5245c2-c036-43dc-8ee3-db5b5c9143ab.mp4",
  "exists": true,
  "path": "app/uploads/6d5245c2-c036-43dc-8ee3-db5b5c9143ab.mp4",
  "exerciseType": "squat",
  "cameraView": "side"
}
```

Um UUID inexistente ou invalido retorna `404`.

### Processar video

```http
POST /videos/{video_id}/process
```

```bash
curl -X POST http://localhost:8000/videos/6d5245c2-c036-43dc-8ee3-db5b5c9143ab/process
```

O processamento abre o video salvo com OpenCV e retorna metadados tecnicos
reais do arquivo:

```json
{
  "videoId": "6d5245c2-c036-43dc-8ee3-db5b5c9143ab",
  "status": "processed",
  "metadata": {
    "durationSeconds": 18.4,
    "fps": 30.0,
    "totalFrames": 552,
    "resolution": {
      "width": 1920,
      "height": 1080
    },
    "fileSizeMb": 24.8
  }
}
```

Um video inexistente retorna `404`; um arquivo que nao puder ser aberto pelo
OpenCV retorna `400`.

### Extrair frames

```http
POST /videos/{video_id}/frames/extract?interval_seconds=0.5
```

```bash
curl -X POST "http://localhost:8000/videos/6d5245c2-c036-43dc-8ee3-db5b5c9143ab/frames/extract?interval_seconds=0.5"
```

O intervalo e opcional e, por padrao, a API salva um frame a cada `0.5`
segundos. Os JPEGs sao gravados em `app/outputs/{video_id}/frames`; ao repetir
a extracao para o mesmo video, os frames anteriores sao substituidos.

```json
{
  "videoId": "6d5245c2-c036-43dc-8ee3-db5b5c9143ab",
  "status": "frames_extracted",
  "frameIntervalSeconds": 0.5,
  "totalFramesExtracted": 25,
  "outputDir": "app/outputs/6d5245c2-c036-43dc-8ee3-db5b5c9143ab/frames",
  "frames": [
    "frame_000001.jpg",
    "frame_000002.jpg"
  ]
}
```

Um video inexistente retorna `404`. Um intervalo menor ou igual a zero, ou
um video que nao possa ser lido pelo OpenCV, retorna `400`.

### Detectar pose

```http
POST /videos/{video_id}/pose/detect
```

Execute a extracao de frames antes da deteccao. A API percorre os JPEGs com
MediaPipe Pose e salva os landmarks em
`app/outputs/{video_id}/pose/landmarks.json`.

```bash
curl -X POST http://localhost:8000/videos/6d5245c2-c036-43dc-8ee3-db5b5c9143ab/pose/detect
```

Resposta:

```json
{
  "videoId": "6d5245c2-c036-43dc-8ee3-db5b5c9143ab",
  "status": "pose_detected",
  "totalFramesProcessed": 25,
  "framesWithPose": 23,
  "outputFile": "app/outputs/6d5245c2-c036-43dc-8ee3-db5b5c9143ab/pose/landmarks.json"
}
```

O arquivo JSON armazena os landmarks retornados para cada frame, incluindo
ombros, quadris, joelhos, tornozelos e pes. Video inexistente ou ausencia de
frames extraidos retorna `404`.

### Calcular metricas biomecanicas

```http
POST /videos/{video_id}/metrics/calculate
```

Execute a deteccao de pose antes desta requisicao. A API calcula angulos em
2D com base nos landmarks e no `cameraView` salvo no upload. Videos frontais
priorizam simetria/alinhamento; videos laterais priorizam profundidade,
cinematica de joelho/quadril, tronco e controle. O resultado e salvo em
`app/outputs/{video_id}/metrics/metrics.json`.

```bash
curl -X POST http://localhost:8000/videos/6d5245c2-c036-43dc-8ee3-db5b5c9143ab/metrics/calculate
```

Resposta:

```json
{
  "videoId": "6d5245c2-c036-43dc-8ee3-db5b5c9143ab",
  "status": "metrics_calculated",
  "movement": "squat",
  "camera_view": "side",
  "metrics": {
    "averageKneeAngle": 92.4,
    "minKneeAngle": 71.2,
    "averageHipAngle": 85.7,
    "torsoInclination": 18.3,
    "depthClassification": "below_parallel",
    "symmetryScore": 87,
    "stabilityScore": 81,
    "cameraView": "side",
    "visibleSide": "right",
    "squat_depth_ratio": 0.86,
    "knee_rom": 88.0,
    "hip_rom": 72.0,
    "bottom_trunk_inclination": 31.0,
    "movement_smoothness": 81,
    "bottom_control": 78
  }
}
```

As classificacoes de profundidade sao `above_parallel`, `parallel` e
`below_parallel`. Video ou landmarks inexistentes retornam `404`; landmarks
sem pontos corporais utilizaveis retornam `400`.

### Analisar movimento por repeticao

```http
POST /videos/{video_id}/movement/analyze
```

Execute a deteccao de pose antes desta requisicao. A API acompanha o angulo
dos joelhos ao longo dos frames, registra uma rep quando o atleta sai e
retorna ao lockout, e descarta movimentos cujo angulo minimo nao chegue a
`120` graus.

```bash
curl -X POST http://localhost:8000/videos/6d5245c2-c036-43dc-8ee3-db5b5c9143ab/movement/analyze
```

O resultado e salvo em
`app/outputs/{video_id}/movement/movement_analysis.json`.

```json
{
  "videoId": "6d5245c2-c036-43dc-8ee3-db5b5c9143ab",
  "movement": "squat",
  "totalReps": 1,
  "reps": [
    {
      "rep": 1,
      "startFrame": 1,
      "bottomFrame": 5,
      "endFrame": 9,
      "depth": "parallel",
      "minKneeAngle": 71.2,
      "stabilityScore": 88,
      "symmetryScore": 91,
      "durationFrames": 8,
      "averageVelocity": 22.35
    }
  ]
}
```

Landmarks inexistentes retornam `404`; landmarks sem pontos suficientes
retornam `400`. Um vídeo sem uma repeticao completa retorna `totalReps: 0`,
pois o movimento nao e inventado a partir de uma sequencia parcial.

### Calcular score biomecanico

```http
POST /videos/{video_id}/score/calculate
```

Execute pose, metricas e analise de movimento antes desta requisicao. A API
usa metricas, repeticoes, landmarks persistidos e `cameraView` para calcular o
score correto. Videos frontais usam `AXON_FRONTAL_MOVEMENT_SCORE`; videos
laterais usam `AXON_LATERAL_MOVEMENT_SCORE`. O resultado e salvo em
`app/outputs/{video_id}/score/scoring.json`.

```bash
curl -X POST http://localhost:8000/videos/6d5245c2-c036-43dc-8ee3-db5b5c9143ab/score/calculate
```

Resposta:

```json
{
  "videoId": "6d5245c2-c036-43dc-8ee3-db5b5c9143ab",
  "status": "score_calculated",
  "movement": "squat",
  "camera_view": "side",
  "score": {
    "overallScore": 78,
    "depthScore": 82,
    "stabilityScore": 74,
    "symmetryScore": 69,
    "consistencyScore": 80,
    "final_score": 78,
    "movement_quality_score": 76,
    "analysis_confidence": 91,
    "classification": "Bom padrao, com pequenos ajustes",
    "summary": "AXON Movement Score calculado por sub-scores.",
    "components": [
      {
        "name": "mobility",
        "score": 82,
        "weight": 0.2,
        "status": "good",
        "details": []
      }
    ],
    "warnings": [],
    "recommendations": [
      "Observe o alinhamento dos joelhos durante a descida."
    ],
    "score_method": "AXON_LATERAL_MOVEMENT_SCORE",
    "score_type": "AXON_LATERAL_MOVEMENT_SCORE",
    "score_version": "1.0.0"
  }
}
```

O score frontal usa componentes `mobility`, `stability`, `symmetry`,
`motor_control` e `analysis_confidence`, com pesos `20%`, `20%`, `20%`, `25%`
e `15%`. O score lateral usa `amplitude_depth`, `joint_kinematics`,
`trunk_posture`, `motor_control` e `analysis_confidence`, com pesos `25%`,
`20%`, `20%`, `20%` e `15%`.
Campos legados continuam presentes para compatibilidade temporaria. Se a
confianca da analise ficar abaixo de `40`, `final_score` e `overallScore`
retornam `null`, em vez de score `0`. Os thresholds desta versao sao
heuristicos e devem ser calibrados com videos reais.

### Gerar feedback tecnico

```http
POST /videos/{video_id}/feedback/generate
```

Execute o scoring antes desta requisicao. A API le `scoring.json`, considera
movimento e metricas quando disponiveis e gera mensagens deterministicas de
resumo, pontos fortes, melhorias e recomendacoes. O resultado e salvo em
`app/outputs/{video_id}/feedback/feedback.json`.

```bash
curl -X POST http://localhost:8000/videos/6d5245c2-c036-43dc-8ee3-db5b5c9143ab/feedback/generate
```

Resposta:

```json
{
  "videoId": "6d5245c2-c036-43dc-8ee3-db5b5c9143ab",
  "status": "feedback_generated",
  "movement": "squat",
  "summary": "Sua execucao geral foi muito boa, com bom controle tecnico e consistencia.",
  "strengths": [
    "Boa simetria entre os lados esquerdo e direito.",
    "Boa consistencia entre as repeticoes."
  ],
  "improvements": [
    "A profundidade esta aceitavel, mas ainda pode ser mais consistente."
  ],
  "recommendations": []
}
```

Se houver queda de qualidade das primeiras para as ultimas repeticoes, o
feedback adiciona uma observacao de possivel fadiga e orientacao de descanso.
Sem `scoring.json`, o endpoint retorna `404`.

### Consultar analise consolidada

```http
GET /videos/{video_id}/analysis
```

Execute a pipeline ate `POST /videos/{video_id}/feedback/generate` antes
desta consulta. O endpoint le os JSONs persistidos de metricas, movimento,
score e feedback, e obtem novamente os metadados tecnicos do video salvo sem
regenerar os artefatos da analise.

```json
{
  "videoId": "6d5245c2-c036-43dc-8ee3-db5b5c9143ab",
  "status": "completed",
  "movement": "squat",
  "camera_view": "side",
  "metadata": {
    "durationSeconds": 18.4,
    "fps": 30.0,
    "totalFrames": 552,
    "resolution": {
      "width": 1920,
      "height": 1080
    },
    "fileSizeMb": 24.8
  },
  "metrics": {
    "averageKneeAngle": 92.4,
    "minKneeAngle": 71.2,
    "averageHipAngle": 85.7,
    "torsoInclination": 18.3,
    "depthClassification": "below_parallel",
    "symmetryScore": 87,
    "stabilityScore": 81
  },
  "totalReps": 1,
  "reps": [],
  "score": {
    "overallScore": 84,
    "depthScore": 80,
    "stabilityScore": 81,
    "symmetryScore": 86,
    "consistencyScore": 89,
    "final_score": 84,
    "movement_quality_score": 83,
    "analysis_confidence": 91,
    "classification": "Bom padrao, com pequenos ajustes",
    "summary": "AXON Movement Score calculado por sub-scores.",
    "components": [],
    "warnings": [],
    "recommendations": [],
    "score_method": "AXON_MOVEMENT_SCORE",
    "score_version": "1.0.0"
  },
  "feedback": {
    "videoId": "6d5245c2-c036-43dc-8ee3-db5b5c9143ab",
    "status": "feedback_generated",
    "movement": "squat",
    "summary": "Sua execucao geral foi muito boa.",
    "strengths": [],
    "improvements": [],
    "recommendations": []
  }
}
```

Video inexistente ou analise sem todos os artefatos obrigatorios retorna
`404`. Arquivos de resultado invalidos ou corrompidos retornam `400`.

## Limites desta etapa

O dashboard do frontend consulta este endpoint para reabrir relatorios reais
por URL. As metricas, o scoring e o feedback usam geometria 2D e regras
fixas, portanto nao substituem avaliacao tecnica profissional. Nao ha autenticacao,
banco de dados, armazenamento em cloud ou jobs assincronos nesta versao.
