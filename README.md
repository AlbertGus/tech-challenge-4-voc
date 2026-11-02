# 📊 Tech Challenge Fase 4: Voice of Customer (VoC) Intelligence com RAG

Este repositório contém a solução desenvolvida para o Tech Challenge da Fase 4, focada em construir um sistema de **Voice of Customer (VoC)** utilizando Inteligência Artificial Generativa e a arquitetura **Retrieval-Augmented Generation (RAG)**.

O objetivo é transformar os comentários textuais das avaliações do dataset público de e-commerce brasileiro (Olist) em uma base de conhecimento interativa, permitindo que gestores obtenham insights valiosos através de perguntas em linguagem natural.

## 📌 O Problema de Negócio

Empresas de e-commerce recebem milhares de avaliações diariamente. Embora as notas numéricas deem um panorama geral da satisfação, os verdadeiros insights (motivos de atraso, qualidade do material, atendimento) estão nos dados não estruturados (textos).
Analisar manualmente 100 mil pedidos é uma tarefa pouco escalável. Esta solução automatiza a extração de inteligência desses textos, fornecendo respostas baseadas em **evidências reais** e não em suposições do modelo de linguagem.

## 🏗️ A Arquitetura Desenvolvida

O fluxo do sistema foi desenhado da seguinte forma:

1. **Ingestão e Preparação (ETL):** Os dados são lidos, cruzados, limpos e os textos são consolidados.
2. **Embeddings:** Os textos são convertidos em representações matemáticas (vetores) para capturar a semântica.
3. **Vector Database:** Os vetores são armazenados e indexados localmente utilizando o ChromaDB.
4. **Retriever com Metadados:** Ao receber a pergunta do gestor na interface Streamlit, o sistema busca os documentos mais próximos no espaço vetorial, aplicando filtros opcionais (ex: Categoria do Produto).
5. **Geração (LLM):** Os documentos recuperados são formatados e injetados em um *prompt* estrito que obriga o modelo (Google Gemini) a gerar a resposta baseando-se apenas naquele contexto.

## ⚙️ Preparação da Base de Dados

A preparação dos dados (documentada no arquivo `01_preparacao_dados.ipynb` e `01_preparacao_dados_storytelling.ipynb`) incluiu as seguintes estratégias:

* **Seleção:** Filtramos apenas as avaliações que continham texto explícito em `review_comment_message` (avaliações apenas com nota foram descartadas por não agregarem contexto semântico).
* **Limpeza:** Remoção de quebras de linha (`\n`, `\r`) e múltiplos espaços para não prejudicar a vetorização. Textos muito curtos (menos de 15 caracteres) também foram removidos.
* **Enriquecimento (Desafio Adicional):** Realizamos cruzamentos (Joins) entre as tabelas `Reviews`, `Orders`, `Items` e `Products`. Isso nos permitiu atrelar a cada comentário de avaliação a **Categoria do Produto** e a **Nota**, essenciais para análises contextualizadas.

## 🧠 Estratégia do Pipeline RAG

A orquestração do RAG foi construída utilizando **LangChain**:

1. **Recuperação Semântica:** A pergunta do usuário passa pelo modelo de embeddings, e o ChromaDB retorna os documentos (`k=7`) matematicamente mais próximos (com maior similaridade semântica).
2. **Construção do Contexto:** O texto bruto recuperado recebe a injeção dos metadados extraídos no ETL. Cada evidência enviada ao LLM tem o formato: `[Nota: X | Categoria: Y] Comentário: Z`.
3. **Trava Anti-Alucinação:** O *System Prompt* instrui o LLM a atuar como um Analista de VoC. Ele tem uma regra explícita de que, caso a resposta não esteja no contexto injetado, ele deve responder: *"Não possuo evidências suficientes na base de avaliações para responder a esta pergunta."*

## ⚖️ Justificativa das Decisões Técnicas

* **Modelo de Embeddings (`paraphrase-multilingual-MiniLM-L12-v2`):** Escolhido por ser leve, rodar localmente sem custos (via CPU) e possuir um excelente desempenho em capturar nuances semânticas da língua portuguesa.
* **Banco Vetorial (ChromaDB):** Ideal para projetos RAG locais, pois permite salvar os índices diretamente em uma pasta (`chroma_db_olist`), dispensando a configuração de servidores complexos para testes.
* **LLM (Google Gemini 3.5 Flash):** Selecionado devido à sua extrema velocidade e baixo custo. Os modelos da família *Flash* são otimizados para tarefas de RAG e formatação estrita de texto, seguindo as regras do prompt perfeitamente.
* **Interface (Streamlit):** Permite a rápida criação de aplicações web interativas em Python puro, entregando um painel executivo visualmente agradável para os gestores.
* **Desafio Adicional (Filtro de Metadados):** Em vez de colocar a categoria na pergunta (o que confunde o motor de busca), adicionamos um filtro direto no retriever do ChromaDB na interface. Isso impede a poluição de contexto e força a busca apenas nas avaliações pertinentes à categoria escolhida.

## 🛠️ Tecnologias e Bibliotecas Utilizadas

* **Python 3.10+**
* **Pandas** (Tratamento e Joins de Dados)
* **LangChain** (Orquestração do Pipeline RAG)
* **Sentence-Transformers** (Geração de Embeddings HuggingFace)
* **ChromaDB** (Banco de Dados Vetorial Local)
* **Google Generative AI / Gemini** (LLM Gerativo)
* **Streamlit** (Front-end e Deploy Local)

## 💡 Exemplos de Perguntas e Respostas (Casos de Uso)

Aqui estão alguns exemplos práticos de como a solução reage a diferentes intenções de busca:

**1. Investigação de problemas gerais (Extração de Insatisfação)**
* **Pergunta:** "Quais problemas os clientes relatam sobre a entrega?"
* **Resposta do Sistema:** O sistema lista tópicos como "Entregas parciais/incompletas e divergência de status", fundamentando com evidências cruzadas: *[Nota: 1 | Categoria: cool_stuff] Comentário: "consta como produto entregue, porém foi entregue apenas 1 produto..."*

**2. Exploração contextual com Metadados (Desafio Adicional)**
* **Pergunta:** "Quais são os principais problemas relatados?" (Filtro aplicado: `beleza_saude`)
* **Resposta do Sistema:** O modelo isola a base e retorna insights nichados: "Envio de produto divergente e mau atendimento". Evidência: *[Nota: 1 | Categoria: beleza_saude] Comentário: "Produto diferente do pedido..."*

**3. Tratamento de Perguntas sem Evidências Suficientes (Filtro Anti-Alucinação)**
* **Pergunta:** "Qual a receita para fazer um bolo de chocolate?"
* **Resposta do Sistema:** *"Não possuo evidências suficientes na base de avaliações para responder a esta pergunta."* (O modelo reconhece a limitação do escopo e bloqueia a geração de conteúdo irreal).

## 🚀 Instruções de Instalação e Execução

### Pré-requisitos

* Python instalado na máquina.
* Chave de API do Google AI Studio (Gemini).

### Passo a Passo

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git
   cd NOME_DO_REPOSITORIO
   ```

2. **Instale as dependências:**
   Crie um ambiente virtual (opcional, mas recomendado) e instale o arquivo requirements:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure as Variáveis de Ambiente:**
   Crie um arquivo chamado `.env` na raiz do projeto e insira a sua chave da API do Google:
   ```env
   GOOGLE_API_KEY=sua_chave_de_api_aqui
   ```

4. **Prepare os Dados (Opcional):**
   *(Se a pasta `chroma_db_olist` já estiver no repositório, você pode pular esta etapa)*.
   Caso queira recriar o banco vetorial e limpar a base do zero, execute todas as células do arquivo `01_preparacao_dados_storytelling.ipynb`.

5. **Execute a Aplicação Streamlit:**
   ```bash
   streamlit run app.py
   ```
   A aplicação abrirá automaticamente no seu navegador padrão (geralmente em `http://localhost:8501`).