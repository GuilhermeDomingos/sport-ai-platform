# Contexto do Projeto - Sport AI Platform / AXON

## Objetivo deste documento

Este arquivo consolida o estado atual do projeto para orientar implementacoes
futuras. Ele deve ser lido antes de alterar fluxos de produto, contratos da
API, persistencia de resultados ou componentes do frontend.

O conteudo abaixo foi levantado diretamente do codigo em 26/05/2026. Quando
houver divergencia entre este documento, o `README.md` e a implementacao, o
codigo em execucao deve ser validado primeiro e a documentacao atualizada na
mesma entrega.

## Visao geral do produto

A Sport AI Platform, apresentada na interface como **AXON Sport AI**, e um MVP
de analise biomecanica de videos esportivos. O caso de uso implementado hoje e
o envio de um video de **Crossfit / Back Squat**, seguido de:

1. upload do arquivo com selecao de `cameraView` (`front` ou `side`);
2. leitura de metadados tecnicos;
3. extracao de frames;
4. deteccao de pose;
5. calculo de metricas biomecanicas 2D;
6. identificacao de repeticoes;
7. calculo de score;
8. geracao de feedback textual;
9. exibicao do relatorio no frontend.

Embora a comunicacao de produto use o termo IA, o pipeline atual combina
MediaPipe para landmarks corporais com regras e heuristicas deterministicas
para metricas, repeticoes, score e feedback. Nao ha treinamento ou inferencia
de um modelo proprio.

## Estado atual em uma frase

O projeto e um monorepo local com frontend Next.js e backend FastAPI; o
frontend aciona uma pipeline sincrona completa para squat, o backend grava
videos e artefatos processados no disco, escolhe metricas/score por angulo de
camera, expoe o relatorio real consolidado, e o dashboard recupera resultados
reais pela API a partir da URL.

## Arquitetura

```txt
sport-ai-platform/
  frontend/                       # Web app AXON
    src/app/                      # App Router: home e results/[videoId]
    src/components/               # Landing, upload, dashboard e UI
    src/services/sportAiApi.ts    # Cliente HTTP do pipeline real
    src/types/analysis.ts         # Contratos usados na UI
    src/lib/formatters.ts         # Formatacao, storage key e demo data
  backend/
    app/main.py                   # FastAPI, CORS e registro de rotas
    app/core/config.py            # Limites e diretorios locais
    app/routes/                   # Endpoints HTTP
    app/schemas/                  # Response models Pydantic
    app/services/                 # Processamento e regras de dominio
    app/modules/biomechanics/     # Metricas laterais e helpers biometricos
    app/modules/scoring/          # AXON Movement Score por exercicio/camera
    app/uploads/                  # Videos locais gerados em runtime
    app/outputs/                  # Frames e JSONs gerados em runtime
    requirements.txt
  package.json                    # npm workspaces e comandos do frontend
  README.md                       # Apresentacao e instrucoes gerais
  AGENTS.md                       # Regra obrigatoria sobre Next.js local
```

Existe tambem uma pasta `src/` na raiz sem codigo funcional identificado no
levantamento atual. As aplicacoes ativas estao em `frontend/` e `backend/`.

## Tecnologias e execucao

### Frontend

- Next.js `16.2.6` com App Router.
- React `19.2.4` e React DOM `19.2.4`.
- TypeScript em modo `strict`.
- Tailwind CSS `4`.
- Recharts para graficos.
- Framer Motion instalado como dependencia.
- React Compiler habilitado em `frontend/next.config.ts`.

O projeto possui uma regra importante em `AGENTS.md`: antes de implementar
codigo Next.js, e obrigatorio consultar o guia pertinente instalado em
`node_modules/next/dist/docs/`, pois esta versao pode divergir de convencoes
anteriores.

### Backend

- Python `3.11`.
- FastAPI e Uvicorn.
- `python-multipart` para uploads.
- OpenCV (`opencv-contrib-python`) para metadados e extracao de frames.
- MediaPipe `0.10.21` para deteccao de pose.
- Pydantic por meio do FastAPI para contratos de resposta.

### Comandos locais

Na raiz, os scripts npm atualmente operam somente o frontend:

```bash
npm install
npm run dev
npm run build
npm run lint
```

O backend deve ser iniciado separadamente:

```powershell
cd backend
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

URLs padrao:

- Frontend: `http://localhost:3000`
- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Frontend

### Rotas e experiencia

| Rota | Responsabilidade |
| --- | --- |
| `/` | Landing page AXON, explicacao do produto e formulario de upload. |
| `/results/[videoId]` | Dashboard de resultados reais ou demonstracao local. |

A home combina `Header`, `HeroSection`, `HowItWorks`, `FeatureCards`,
`VideoUploadCard` e `Footer`. O upload aceita selecao ou drag-and-drop, exige
o tipo do video (`Frontal` ou `Lateral`), mostra preview local do video e
exibe o andamento da pipeline.

O dashboard mostra score geral, feedback, metricas, graficos e tabela de
repeticoes. A rota `/results/demo-back-squat` e acessivel pela home e utiliza
dados demonstrativos definidos em `src/lib/formatters.ts`.

### Fluxo de analise real no navegador

`VideoUploadCard.tsx` orquestra as requisicoes de forma sequencial:

```txt
uploadVideo(file, cameraView)
  -> processVideo
  -> extractFrames
  -> detectPose
  -> calculateMetrics
  -> analyzeMovement
  -> calculateScore
  -> generateFeedback
  -> /results/{videoId}
```

Os estados visuais correspondentes sao:

```txt
idle -> uploading -> processing -> extracting_frames -> detecting_pose
     -> calculating_metrics -> analyzing_movement -> calculating_score
     -> generating_feedback -> completed | error
```

### Cliente da API e configuracao

O cliente esta em `frontend/src/services/sportAiApi.ts`. A URL base e:

```txt
NEXT_PUBLIC_API_BASE_URL ?? http://localhost:8000
```

Erros HTTP sao convertidos em `Error` com o campo `detail` retornado pelo
backend, quando disponivel.

### Carregamento do resultado na UI

Depois do pipeline, o frontend navega para `/results/{videoId}`. A pagina de
resultados consulta `GET /videos/{id}/analysis` no servidor e entrega o
relatorio real ao dashboard; a rota `/results/demo-back-squat` continua usando
dados demonstrativos locais de forma explicita.

Consequencias importantes:

- recarregar ou abrir a URL de uma analise real em nova aba recupera o
  relatorio persistido no backend;
- IDs reais sem relatorio completo exibem estado de indisponibilidade, sem
  fallback silencioso para demo;
- ainda nao ha historico de analises ou associacao com usuario.

## Backend

### Organizacao interna

O backend adota uma separacao simples:

- `routes/`: definicao de URLs e response models;
- `schemas/`: formatos Pydantic expostos pela API;
- `services/`: regras, acesso ao filesystem e processamento;
- `core/config.py`: armazenamento local e validacoes de upload.

O CORS permite atualmente apenas `http://localhost:3000`.

### Pipeline real

| Ordem | Endpoint | Implementacao principal | Artefato persistido |
| --- | --- | --- | --- |
| 1 | `POST /videos/upload` | valida e salva o arquivo enviado, `exerciseType` e `cameraView` | `app/uploads/{videoId}.{ext}` e `app/outputs/{videoId}/video.json` |
| 2 | `POST /videos/{id}/process` | le FPS, duracao, frames, resolucao e tamanho | nenhum JSON |
| 3 | `POST /videos/{id}/frames/extract` | extrai imagens com OpenCV | `app/outputs/{id}/frames/*.jpg` |
| 4 | `POST /videos/{id}/pose/detect` | executa MediaPipe Pose nos frames | `app/outputs/{id}/pose/landmarks.json` |
| 5 | `POST /videos/{id}/metrics/calculate` | calcula metricas globais do squat | `app/outputs/{id}/metrics/metrics.json` |
| 6 | `POST /videos/{id}/movement/analyze` | segmenta repeticoes completas | `app/outputs/{id}/movement/movement_analysis.json` |
| 7 | `POST /videos/{id}/score/calculate` | calcula o AXON Movement Score por `exerciseType + cameraView` | `app/outputs/{id}/score/scoring.json` |
| 8 | `POST /videos/{id}/feedback/generate` | aplica regras textuais e fadiga | `app/outputs/{id}/feedback/feedback.json` |

Apos a ultima etapa, `GET /videos/{id}/analysis` le os quatro artefatos
finais (`metrics`, `movement`, `score` e `feedback`), recomputa os metadados
tecnicos do video salvo e retorna um relatorio consolidado real. A consulta
nao regenera artefatos e retorna erro se a pipeline ainda nao estiver completa.

Cada etapa depende dos artefatos ou do video da etapa anterior. O frontend
executa todas elas de forma sincrona; ainda nao ha fila, processamento em
background, polling ou websocket.

### Upload e arquivos

Configuracao atual:

| Regra | Valor |
| --- | --- |
| Limite de upload | `200 MB` |
| Extensoes | `mp4`, `mov`, `avi`, `mkv`, `webm` |
| MIME types | `video/mp4`, `video/quicktime`, `video/x-msvideo`, `video/x-matroska`, `video/webm` |
| Identificador | UUID gerado no upload |
| Armazenamento | filesystem local, sem banco de dados |

O nome original e devolvido na resposta, mas o arquivo e salvo sob o UUID. Os
diretorios `backend/app/uploads/` e `backend/app/outputs/` estao ignorados no
Git, exceto por arquivos `.gitkeep`.

### Processamento biomecanico implementado

O movimento suportado e fixo como `squat`.

`pose_detection_service.py` usa os 33 landmarks do MediaPipe e registra para
cada frame se houve deteccao, alem de coordenadas `x`, `y`, `z` e
`visibility`.

`biomechanics_service.py` usa o `cameraView` persistido no upload para separar
analise frontal e lateral.

Para videos frontais, usa ombros, quadris, joelhos e tornozelos para calcular:

- angulo medio dos joelhos;
- menor angulo dos joelhos;
- angulo medio dos quadris;
- inclinacao media do tronco;
- profundidade (`above_parallel`, `parallel`, `below_parallel`);
- score heuristico de simetria;
- score heuristico de estabilidade.

Para videos laterais, `app/modules/biomechanics/lateral_metrics.py` escolhe
automaticamente o lado mais visivel (`left` ou `right`) e calcula metricas de
profundidade/amplitude, angulo de joelho, angulo de quadril, inclinacao de
tronco, suavidade, controle no ponto mais baixo e confianca dos landmarks do
lado analisado.

`movement_analysis_service.py` identifica repeticoes a partir do angulo medio
dos joelhos:

| Parametro | Valor atual |
| --- | --- |
| Lockout para iniciar/finalizar rep | angulo `>= 160` graus |
| Profundidade minima para validar rep | angulo minimo `< 120` graus |
| Tolerancia para classificar paralelo | `0.03` em coordenadas normalizadas |

Uma repeticao so e registrada quando ha saida do lockout e retorno ao lockout.
Movimentos incompletos nao geram uma rep artificial.

### Scoring e feedback

O score atual e o **AXON Movement Score**, implementado em
`backend/app/modules/scoring/` com engine extensivel por exercicio e camera.
A primeira regra suportada e `squat` com duas configuracoes:
`("squat", "front")` e `("squat", "side")`.

O score frontal (`AXON_FRONTAL_MOVEMENT_SCORE`) combina cinco componentes, com
pesos centralizados em configuracao:

```txt
final_score =
  mobility * 0.20 +
  stability * 0.20 +
  symmetry * 0.20 +
  motor_control * 0.25 +
  analysis_confidence * 0.15
```

O score lateral (`AXON_LATERAL_MOVEMENT_SCORE`) combina:

```txt
final_score =
  amplitude_depth * 0.25 +
  joint_kinematics * 0.20 +
  trunk_posture * 0.20 +
  motor_control * 0.20 +
  analysis_confidence * 0.15
```

O metodo retorna `final_score`, `movement_quality_score`,
`analysis_confidence`, `classification`, `summary`, `components`, `warnings`,
`recommendations`, `score_method`, `score_type` e `score_version`. Os campos
legados `overallScore`, `depthScore`, `stabilityScore`, `symmetryScore` e
`consistencyScore` permanecem no JSON para compatibilidade temporaria.

Se `analysis_confidence < 40`, o resultado e inconclusivo e `final_score` e
`overallScore` ficam `null`, evitando mostrar score `0` para video ruim. Os
thresholds iniciais sao heuristicas 2D e devem ser calibrados com videos reais.

O feedback e deterministico: prefere os componentes e recomendacoes do AXON
Movement Score, com fallback para artefatos legados. Ha tambem uma regra de
possivel fadiga, acionada quando a qualidade media da metade final das
repeticoes e menor do que a da metade inicial.

### Consulta consolidada do resultado

| Endpoint | Comportamento |
| --- | --- |
| `GET /videos/{id}/analysis` | devolve metricas, repeticoes, score e feedback persistidos pelo pipeline real. |

O antigo `POST /videos/{id}/analyze`, que devolvia uma analise fixa, foi
removido. A consulta real exige os quatro artefatos finais; video ou analise
incompleta retorna `404`, e artefato invalido retorna `400`.

## Contratos principais consumidos pelo frontend

O arquivo `frontend/src/types/analysis.ts` espelha as respostas utilizadas na
interface:

| Tipo | Conteudo essencial |
| --- | --- |
| `UploadResponse` | ID, nomes, MIME type, tamanho e caminho do upload. |
| `ProcessingResponse` | duracao, FPS, total de frames, resolucao e MB. |
| `MetricsResponse` | metricas globais e scores iniciais do squat. |
| `MovementAnalysisResponse` | total de reps e metricas por repeticao. |
| `ScoreResponse` | AXON Movement Score, componentes, confianca e campos legados de compatibilidade. |
| `FeedbackResponse` | resumo, pontos fortes, melhorias e recomendacoes. |
| `AnalysisResult` | relatorio consolidado recuperado da API e exibido pelo dashboard. |

`UploadResponse` tambem inclui `exerciseType` e `cameraView`; `AnalysisResult`
inclui `camera_view` para o dashboard exibir se a analise foi frontal ou
lateral.

Ao evoluir um schema no backend, tambem devem ser revisados os tipos, o
cliente HTTP e os componentes que exibem o dado no frontend.

O backend expoe `AnalysisResponse` consolidado em
`GET /videos/{id}/analysis`; ele inclui metadados tecnicos recomputados na
consulta e e consumido pela pagina de resultados do frontend.

## Pontos de atencao confirmados

- A API e a interface assumem analise de `squat`; existe selecao de angulo de
  camera, mas ainda nao ha selecao real de esporte ou movimento.
- A pipeline processa arquivos no request HTTP e pode ficar lenta para videos
  grandes; nao existe job assincrono ou indicador de progresso do backend.
- Uploads, frames e resultados sao locais, sem politicas de expiracao ou
  limpeza automatica.
- Nao existe autenticacao, autorizacao, banco de dados ou isolamento por
  usuario.
- O relatorio real pode ser recuperado por URL, mas continua dependente de
  video e artefatos locais existentes no backend.
- Os scores sao heuristicas 2D e nao devem ser tratados como avaliacao clinica
  ou tecnica profissional.
- A consulta consolidada possui testes backend de contrato e cenarios de
  artefato ausente ou invalido; as demais partes do pipeline seguem sem
  cobertura automatizada identificada.
- O valor default do intervalo de extracao deve ser tratado com cuidado: a
  rota HTTP atual define `0.3` segundos, o servico tem fallback direto de
  `0.1`, e o `backend/README.md` descreve `0.5`. Pelo fluxo HTTP do frontend,
  o comportamento efetivo atual e `0.3` segundos.

## Diretrizes para implementacoes futuras

### Antes de alterar o frontend

1. Ler `AGENTS.md` e o guia pertinente de Next.js em
   `node_modules/next/dist/docs/`.
2. Verificar se a mudanca afeta componentes client-side, rotas App Router ou
   o contrato de dados em `src/types/analysis.ts`.
3. Preservar a rota demo explicita e o carregamento real via API.

### Antes de alterar o backend

1. Definir se a mudanca pertence a geracao do pipeline real ou a consulta
   consolidada.
2. Manter schemas Pydantic e tipos TypeScript coerentes.
3. Revisar pre-condicoes entre etapas e mensagens de erro expostas a UI.
4. Considerar a persistencia de artefatos e a compatibilidade com resultados
   ja gerados localmente.

### Evolucoes naturais do produto

Os proximos passos arquiteturais mais provaveis sao:

- persistir videos, status e resultados em banco de dados;
- mover processamento custoso para jobs assincronos;
- adicionar autenticacao e propriedade das analises;
- suportar outros movimentos com configuracao e contratos explicitos;
- padronizar thresholds e scores com validacao tecnica;
- incluir testes de servicos backend e testes de fluxo frontend/API;
- definir armazenamento externo e politica de retencao de videos.

## Arquivos de referencia

| Assunto | Arquivo principal |
| --- | --- |
| Visao geral existente | `README.md` |
| Regra de desenvolvimento Next.js | `AGENTS.md` |
| Roteamento e CORS da API | `backend/app/main.py` |
| Limites de upload | `backend/app/core/config.py` |
| Servicos do pipeline | `backend/app/services/*.py` |
| Contratos da API | `backend/app/schemas/*.py` |
| Orquestracao do upload | `frontend/src/components/upload/VideoUploadCard.tsx` |
| Cliente HTTP | `frontend/src/services/sportAiApi.ts` |
| Tipos do dashboard | `frontend/src/types/analysis.ts` |
| Persistencia/dados demo | `frontend/src/lib/formatters.ts` |
| Exibicao de resultados | `frontend/src/components/results/ResultsDashboard.tsx` |

## Como manter este documento atualizado

Atualize este arquivo sempre que houver mudanca em pelo menos um dos pontos:

- objetivo do produto ou movimento analisado;
- stack, comandos de execucao ou variaveis de ambiente;
- endpoints, schemas ou ordem do pipeline;
- armazenamento de videos/resultados;
- estrategia de score ou feedback;
- rotas e comportamento do frontend;
- decisoes arquiteturais que afetem implementacoes futuras.
