# Configuração do Sistema: Especialista em Segurança de Veículos Elétricos e Eletrificados

## Visão Geral

Este sistema foi configurado para atuar como um **especialista em segurança com veículos elétricos e eletrificados**, capaz de responder qualquer pergunta sobre este tema.

## Características Principais

### 1. Especialização em Segurança de Veículos Elétricos
O sistema está configurado para:
- Fornecer respostas especializadas sobre segurança de veículos elétricos e eletrificados
- Priorizar aspectos de segurança em todas as interações
- Combinar conhecimento especializado com documentos técnicos indexados
- Manter uma abordagem técnica e precisa nas respostas

### 2. Sistema RAG (Retrieval-Augmented Generation)
O sistema utiliza tecnologia RAG para:
- Buscar documentos relevantes sobre veículos elétricos
- Combinar informações dos documentos com conhecimento especializado
- Citar fontes quando apropriado
- Fornecer respostas contextualizadas e precisas

## Configuração

### Variável de Ambiente Chave

```bash
SYSTEM_ROLE_DESCRIPTION="VOCÊ É UM ESPECIALISTA EM SEGURANÇA COM VEÍCULOS ELÉTRICOS E ELETRIFICADOS, E PRECISA SER APTO PARA RESPONDER QUALQUER PERGUNTA SOBRE ESSE TEMA."
```

Esta variável define o papel do sistema e pode ser personalizada no arquivo `.env`.

### Exemplo de Arquivo .env

```bash
# System Behavior Configuration
SYSTEM_ROLE_DESCRIPTION=VOCÊ É UM ESPECIALISTA EM SEGURANÇA COM VEÍCULOS ELÉTRICOS E ELETRIFICADOS, E PRECISA SER APTO PARA RESPONDER QUALQUER PERGUNTA SOBRE ESSE TEMA.
```

## Como Usar

### 1. Upload de Documentos
Faça upload de documentos técnicos sobre veículos elétricos:

```bash
POST /v1/rag/documents/upload-and-index
```

### 2. Consultas RAG
Faça perguntas especializadas sobre segurança de veículos elétricos:

```bash
POST /v1/rag/chat
{
  "query": "Quais são os principais riscos de segurança em baterias de íons de lítio?",
  "use_rag": true,
  "max_context_chunks": 5
}
```

### 3. Chat Stream
Para respostas em streaming:

```bash
POST /v1/rag/chat/stream
{
  "query": "Explique os sistemas de segurança em veículos elétricos",
  "use_rag": true
}
```

## Comportamento do Sistema

### Com Documentos Disponíveis (RAG Ativado)
Quando há documentos relevantes indexados, o sistema:
1. Busca informações relevantes nos documentos
2. Combina com conhecimento especializado
3. Cita as fontes apropriadamente
4. Prioriza aspectos de segurança

### Sem Documentos (Conhecimento Especializado)
Mesmo sem documentos indexados, o sistema:
1. Utiliza seu conhecimento especializado em veículos elétricos
2. Mantém foco em segurança
3. Fornece respostas técnicas e precisas
4. Sugere quando documentos adicionais seriam úteis

## Tópicos de Especialização

O sistema está apto para responder sobre:

### Segurança de Baterias
- Sistemas de gerenciamento de bateria (BMS)
- Riscos de incêndio e explosão
- Thermal runaway
- Protocolos de segurança

### Segurança Elétrica
- Isolamento elétrico
- Proteção contra choques elétricos
- Sistemas de alta tensão
- Aterramento e blindagem

### Segurança Estrutural
- Proteção da bateria em colisões
- Integridade estrutural
- Crash tests específicos para EVs
- Proteção de componentes críticos

### Segurança Operacional
- Carregamento seguro
- Manutenção de sistemas elétricos
- Procedimentos de emergência
- Treinamento de equipes

### Regulamentações e Normas
- Normas de segurança internacionais
- Certificações obrigatórias
- Requisitos regulatórios
- Padrões de qualidade

## Testes

Execute os testes para verificar a configuração:

```bash
pytest tests/test_ev_security_config.py -v
```

## Personalização

Para alterar a especialização do sistema, modifique a variável `SYSTEM_ROLE_DESCRIPTION` no arquivo `.env` e reinicie o servidor.

## Suporte

Para questões técnicas ou sugestões, consulte a documentação completa da API ou entre em contato com a equipe de desenvolvimento.
