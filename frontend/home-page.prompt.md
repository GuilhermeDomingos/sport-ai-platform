# Prompt — Criação da Home da Plataforma

## Contexto

Estou criando uma plataforma web de análise esportiva por vídeo com IA.

A ideia inicial é permitir que atletas amadores que levam o treino a sério possam fazer upload de vídeos dos seus treinos e, futuramente, receber métricas, insights e acompanhamento de evolução com auxílio de IA.

O projeto está sendo desenvolvido em:

- Next.js
- TypeScript
- Tailwind CSS
- App Router

## Objetivo

Criar a primeira versão da Home da aplicação.

A Home deve transmitir uma proposta moderna, esportiva, tecnológica e premium.

## Nome temporário da plataforma

Use um nome provisório como:

**Athlete Vision AI**

## Público-alvo

Pessoas que treinam com seriedade, como:

- praticantes de Crossfit
- musculação
- funcional
- corrida
- atletas amadores de alta performance
- pessoas que gostam de acompanhar métricas e evolução

## Proposta de valor

A plataforma permite que o usuário envie vídeos dos seus treinos para acompanhar execução, evolução e performance com apoio de IA.

## Estrutura desejada da Home

Criar uma página com as seguintes seções:

### 1. Header

Deve conter:

- Logo/nome da plataforma
- Links:
  - Como funciona
  - Benefícios
  - Upload
- Botão CTA:
  - Começar agora

### 2. Hero Section

Deve conter:

- Título forte
- Subtítulo explicando o produto
- Botão principal:
  - Analisar meu treino
- Botão secundário:
  - Ver como funciona
- Um card visual simulando uma análise de treino

Exemplo de título:

> Transforme seus vídeos de treino em métricas inteligentes de performance.

Exemplo de subtítulo:

> Envie seus vídeos, acompanhe sua evolução e receba insights com IA para treinar com mais inteligência.

### 3. Seção “Como funciona”

Mostrar 3 passos:

1. Faça upload do vídeo
2. A IA analisa seus movimentos
3. Receba métricas e insights

### 4. Seção de benefícios

Criar cards com benefícios como:

- Acompanhe sua evolução
- Identifique pontos de melhoria
- Analise sua execução
- Tome decisões baseadas em dados
- Treine com mais consciência

### 5. Seção de métricas

Mostrar exemplos de métricas futuras:

- Score de performance
- Estabilidade
- Amplitude de movimento
- Consistência
- Velocidade de execução
- Evolução semanal

### 6. Seção de upload

Criar uma área visual para upload de vídeo.

Por enquanto, essa área pode ser estática ou usar o componente `VideoUpload`, caso ele já exista no projeto.

Se existir o componente:

```tsx
import { VideoUpload } from "@/components/VideoUpload";