# Plano de Estudo - Sistema de Deteccao de Fraudes Bancarias

## Como usar este plano
- **Prioridade Alta**: Estude PRIMEIRO - sao os topicos mais cobrados em banca
- **Prioridade Media**: Estude SEGUNDO - complementam e aprofundam
- **Prioridade Baixa**: Estude se sobrar tempo - diferenciais
- **Tempo total estimado:** 40-50 horas de estudo

---

## TOPICO 1: Arquitetura de Dados e Data Lake
**Prioridade: ALTA | Tempo estimado: 6 horas**

### O que estudar:
1. **Arquitetura Medallion (Bronze/Silver/Gold)**
   - O que e cada camada e por que separar
   - Que transformacoes acontecem entre camadas
   - Politicas de retencao por camada
   - Como isso se aplica ao projeto (Raw -> Processed -> Curated)

2. **Data Lake vs Data Warehouse vs Lakehouse**
   - Diferencas fundamentais (schema-on-read vs schema-on-write)
   - Quando usar cada um
   - Como combinamos Data Lake Gen2 + Synapse neste projeto
   - Conceito de Lakehouse (Delta Lake)

3. **Formatos de Armazenamento**
   - Parquet vs CSV vs JSON vs Avro vs ORC
   - Por que usamos Parquet (colunar, compressao, schema evolution)
   - Delta Lake (ACID em Data Lake, time travel)

4. **Particionamento de Dados**
   - Por que particionar (performance de leitura)
   - Estrategias: por data, por regiao, por usuario
   - No projeto: `partitionBy("transaction_date")`

### Onde estudar:
- Microsoft Learn: "Azure Data Lake Storage Gen2" (gratuito)
- Artigo: "Medallion Architecture" no site da Databricks
- Video: "Data Lake vs Data Warehouse" - Alex The Analyst (YouTube)
- Capitulo 3 do livro "Fundamentals of Data Engineering" (Joe Reis)

### Exercicio pratico:
- Abra `notebooks/01_dataprep_dq.py` e trace o fluxo de dados:
  - `read_raw_data()` -> Bronze
  - `clean_transactions()` -> Silver
  - `enrich_data()` -> Gold
- Modifique o particionamento para `partitionBy("transaction_date", "user_country")`

### Perguntas que a banca pode fazer:
- "Por que 3 camadas e nao 2?"
- "O que acontece se um dado chegar corrompido na camada Raw?"
- "Como voce garante consistencia entre as camadas?"

---

## TOPICO 2: Streaming e Ingestao de Dados
**Prioridade: ALTA | Tempo estimado: 5 horas**

### O que estudar:
1. **Azure Event Hubs / Apache Kafka**
   - Conceitos: topicos, particoes, consumer groups, offsets
   - Garantias de entrega: at-least-once, at-most-once, exactly-once
   - Event Hubs vs Kafka vs Kinesis (diferencas e similaridades)
   - Throughput Units e escalabilidade

2. **Arquitetura Lambda vs Kappa**
   - Lambda: batch + streaming em paralelo (nosso projeto)
   - Kappa: so streaming (mais simples mas limitada)
   - Quando usar cada uma e trade-offs

3. **Processamento de Eventos**
   - Checkpoint: por que e necessario (exatamente no nosso consumer)
   - Dead Letter Queue: tratamento de erros
   - Backpressure: o que fazer quando o consumer nao acompanha

### Onde estudar:
- Microsoft Learn: "Azure Event Hubs" (gratuito, ~2h)
- Confluent: "Kafka 101" (gratuito, ~3h)
- Video: "Lambda vs Kappa Architecture" - Seattle Data Guy (YouTube)
- Documentacao: `src/data_ingestion/event_hub_producer.py` e `event_hub_consumer.py`

### Exercicio pratico:
- Leia o `event_hub_producer.py` e entenda:
  - Como um batch e criado e enviado
  - O que acontece quando o batch fica cheio (linhas 89-95)
- Leia o `event_hub_consumer.py` e entenda:
  - O que e `checkpoint` e por que fazemos `update_checkpoint` (linha 89)
  - O que `starting_position="-1"` significa

### Perguntas que a banca pode fazer:
- "O que acontece se o consumer cair no meio do processamento?"
- "Como garantir que nenhuma transacao seja perdida?"
- "Qual a diferenca entre Event Hubs e Kafka?"

---

## TOPICO 3: Machine Learning para Deteccao de Fraudes
**Prioridade: ALTA | Tempo estimado: 8 horas**

### O que estudar:
1. **Algoritmos utilizados:**
   - **Isolation Forest**: Como funciona (isolamento de anomalias), quando usar, hiperparametros (n_estimators, contamination)
   - **XGBoost**: Gradient boosting, por que e bom para dados tabulares, hiperparametros principais
   - **Ensemble**: Como combinar modelos, voting vs stacking

2. **Feature Engineering para Fraude:**
   - Features temporais: hora do dia, dia da semana, fim de semana
   - Features comportamentais: media do usuario, desvio padrao
   - Features de merchant: volume, media
   - Features geograficas: transacao internacional
   - Entender cada feature no `enrich_data()` do notebook

3. **Metricas de Avaliacao:**
   - **Recall** (sensibilidade): % de fraudes detectadas - MAIS IMPORTANTE
   - **Precision**: % de alertas que sao realmente fraude
   - **F1-Score**: media harmonica
   - **AUC-ROC**: area sob a curva
   - Por que recall > precision em deteccao de fraudes
   - Trade-off precision/recall e como ajustar o threshold

4. **Dados Desbalanceados:**
   - O problema: 95% normal, 5% fraude
   - Tecnicas: SMOTE, undersampling, class weights
   - imbalanced-learn (biblioteca do projeto)

5. **MLOps:**
   - MLflow: experiment tracking, model registry
   - Model versioning e rollback
   - A/B testing em producao
   - Data drift e model drift

### Onde estudar:
- Scikit-learn docs: "Isolation Forest" e "XGBoost"
- Curso: "Machine Learning for Fraud Detection" - DataCamp
- Video: "Imbalanced Classification" - StatQuest (YouTube)
- Artigo: "MLOps Principles" - Google Cloud (aplica-se a qualquer cloud)
- MLflow docs: "Quickstart" tutorial

### Exercicio pratico:
- Rode o demo local e analise:
  - Por que transacoes de alto valor + internacional + madrugada = alto score?
  - Mude o threshold e veja como muda o numero de fraudes detectadas
- Treine o modelo com dados diferentes: `python scripts/generate_data.py -n 10000`
- Analise a feature importance e explique por que cada feature e relevante

### Perguntas que a banca pode fazer:
- "Por que Isolation Forest e nao outro algoritmo de anomalia?"
- "Como voce lida com o desbalanceamento de classes?"
- "O que acontece quando o padrao de fraude muda?"
- "Qual a diferenca entre recall e precision e por que recall e mais importante aqui?"

---

## TOPICO 4: Infraestrutura como Codigo (Terraform)
**Prioridade: MEDIA | Tempo estimado: 4 horas**

### O que estudar:
1. **Conceitos de IaC:**
   - O que e Infrastructure as Code e por que importa
   - Terraform vs ARM Templates vs Bicep vs Pulumi
   - State management: o que e terraform.tfstate e por que e critico
   - Plan -> Apply -> Destroy ciclo de vida

2. **Terraform no projeto:**
   - `main.tf`: recursos criados (Resource Group, Storage, Event Hub, Cosmos DB, Key Vault, PostgreSQL)
   - `variables.tf`: parametrizacao
   - `outputs.tf`: informacoes de saida
   - Backend remoto para state (Azure Storage)

3. **Boas praticas:**
   - Ambientes separados (dev/staging/prod)
   - Modulos reutilizaveis
   - Variáveis sensíveis (sensitive = true)
   - Tags para organizacao e custos

### Onde estudar:
- HashiCorp Learn: "Get Started - Azure" (gratuito, ~2h)
- Microsoft Learn: "Deploy Azure infrastructure with Terraform"
- Arquivo do projeto: `infrastructure/terraform/environments/dev/main.tf`

### Exercicio pratico:
- Leia o `main.tf` e desenhe um diagrama dos recursos e suas dependencias
- Identifique quais recursos dependem de quais (ex: Event Hub depende do Namespace)
- Entenda por que `is_hns_enabled = true` no Storage Account (habilita Data Lake Gen2)

### Perguntas que a banca pode fazer:
- "O que acontece se voce rodar terraform apply duas vezes?"
- "Como gerenciar secrets no Terraform?"
- "Qual a vantagem de IaC vs criar recursos manualmente no portal?"

---

## TOPICO 5: Data Quality e Governanca
**Prioridade: MEDIA | Tempo estimado: 4 horas**

### O que estudar:
1. **Great Expectations:**
   - O que sao Expectations (regras de validacao)
   - Tipos: schema, range, uniqueness, statistical
   - Suites e Checkpoints
   - Como integrar no pipeline (nosso `AzureDataQuality`)

2. **Data Drift:**
   - O que e drift (mudanca na distribuicao dos dados)
   - Por que e perigoso para ML
   - Como detectar com Evidently
   - Acoes quando drift e detectado

3. **Azure Purview:**
   - Catalogo de dados
   - Linhagem (data lineage): de onde vem cada dado
   - Classificacao automatica de PII

4. **Governanca declarativa:**
   - Regras em YAML (`governanca.yaml`)
   - Severidade: error vs warning
   - Automacao de validacoes

### Onde estudar:
- Great Expectations docs: "Getting Started" tutorial
- Evidently AI docs: "Data Drift" tutorial
- Microsoft Learn: "Azure Purview" overview
- Arquivo: `notebooks/01_dataprep_dq.py` (classe AzureDataQuality)
- Arquivo: `governanca.yaml`

### Exercicio pratico:
- Leia cada expectation em `create_expectation_suite()` e explique o que valida
- Pense em 3 novas regras que adicionaria (ex: validar formato de email, checar timezone)
- Entenda o relatorio de DQ: o que cada campo do report significa

### Perguntas que a banca pode fazer:
- "O que acontece se uma validacao de DQ falhar em producao?"
- "Como voce detecta data drift?"
- "Qual a diferenca entre data quality e data governance?"

---

## TOPICO 6: Seguranca e LGPD
**Prioridade: MEDIA | Tempo estimado: 4 horas**

### O que estudar:
1. **LGPD (Lei Geral de Protecao de Dados):**
   - O que sao dados pessoais e dados sensiveis
   - Principios: finalidade, adequacao, necessidade, minimizacao
   - Direitos do titular: acesso, correcao, eliminacao, portabilidade
   - Papel do DPO (Data Protection Officer)
   - Penalidades: ate 2% do faturamento ou R$ 50M

2. **Mascaramento vs Anonimizacao vs Pseudonimizacao:**
   - Mascaramento: CPF `***456***00` (reversivel com chave)
   - Anonimizacao: hash SHA-256 (irreversivel)
   - Pseudonimizacao: token substituindo o dado real
   - Quando usar cada tecnica

3. **Seguranca na Azure:**
   - Azure Key Vault: gerenciamento de secrets e chaves
   - Managed Identities: autenticacao sem senhas
   - RBAC: controle de acesso baseado em papeis
   - Network Security: VNets, Private Endpoints
   - Criptografia: at-rest (AES-256) e in-transit (TLS 1.2+)

### Onde estudar:
- Site oficial: lgpd.gov.br - texto completo da lei
- Microsoft Learn: "Azure Key Vault" e "Azure AD RBAC"
- Artigo: "LGPD para engenheiros de dados" - Medium
- Arquivo: `src/utils/data_masker.py`

### Exercicio pratico:
- Execute o `data_masker.py` diretamente e teste com diferentes dados
- Identifique no projeto todos os pontos onde dados PII aparecem
- Para cada ponto, verifique se ha mascaramento antes de log/armazenamento
- Pense: quais dados no `generate_data.py` sao PII? (ip_address, device_id)

### Perguntas que a banca pode fazer:
- "Quais dados neste sistema sao considerados PII pela LGPD?"
- "Qual a diferenca entre mascaramento e anonimizacao?"
- "Se um usuario pedir para deletar seus dados, como voce faz?"

---

## TOPICO 7: Apache Spark e Processamento Distribuido
**Prioridade: MEDIA | Tempo estimado: 5 horas**

### O que estudar:
1. **Fundamentos do Spark:**
   - Arquitetura: Driver, Executors, Cluster Manager
   - RDD vs DataFrame vs Dataset
   - Lazy evaluation: transformacoes vs acoes
   - Particionamento e shuffling

2. **PySpark no projeto:**
   - Leitura de dados: `spark.read.parquet()`, `spark.read.json()`
   - Transformacoes: `withColumn()`, `filter()`, `groupBy()`, `join()`
   - Escrita: `df.write.partitionBy().parquet()`
   - UDFs (User Defined Functions)

3. **Azure Databricks:**
   - O que e (Spark gerenciado + notebooks + colaboracao)
   - Clusters: auto-scaling, spot instances
   - Delta Lake: ACID transactions em Data Lake
   - Unity Catalog: governanca

4. **Otimizacao:**
   - Adaptive Query Execution (AQE)
   - Coalesce vs Repartition
   - Broadcast joins vs Sort-merge joins
   - Caching e persist

### Onde estudar:
- Databricks Academy: "Apache Spark Programming" (gratuito)
- Video: "Spark in 15 Minutes" - Data Engineering (YouTube)
- Arquivo: `notebooks/01_dataprep_dq.py` - todo o processamento usa PySpark

### Exercicio pratico:
- Trace cada transformacao no `clean_transactions()`:
  - `dropDuplicates` -> por que? (remover transacoes duplicadas)
  - `fillna` -> por que? (tratar nulos antes de ML)
  - `withColumn("transaction_date")` -> por que? (feature para particionamento)
- Trace o `enrich_data()`: quais joins sao feitos e por que

### Perguntas que a banca pode fazer:
- "O que e lazy evaluation e por que o Spark usa?"
- "Como o Spark distribui o processamento entre nos?"
- "O que e um shuffle e por que e custoso?"

---

## TOPICO 8: APIs e Microservicos
**Prioridade: MEDIA | Tempo estimado: 4 horas**

### O que estudar:
1. **REST API Design:**
   - Verbos HTTP: GET, POST, PUT, DELETE
   - Status codes: 200, 201, 400, 401, 404, 500
   - Versionamento: `/api/v1/` (nosso caso)
   - Paginacao, filtragem, ordenacao

2. **Spring Boot (Java API):**
   - Arquitetura: Controller -> Service -> Repository
   - Dependency Injection (IoC)
   - JPA/Hibernate para banco de dados
   - Spring Security para autenticacao
   - Actuator para health checks e metricas

3. **FastAPI (Python API):**
   - Async/await para performance
   - Pydantic para validacao
   - Swagger automatico (/docs)
   - Dependency injection

4. **Swagger/OpenAPI:**
   - O que e e por que usar
   - Como ler a documentacao interativa
   - Como testar endpoints pelo Swagger UI

### Onde estudar:
- FastAPI docs: "First Steps" tutorial (15 min)
- Spring Boot docs: "Building REST services"
- Arquivo Java: `api-java/src/main/java/com/fraud/controller/TransactionController.java`
- Demo local: http://localhost:8000/docs (Swagger UI da API Python)

### Exercicio pratico:
- Acesse http://localhost:8000/docs e teste cada endpoint
- Leia o codigo Java do controller e trace o fluxo: request -> controller -> service -> response
- Compare a API Java (Spring Boot) com a API Python (FastAPI): diferencas e similaridades

### Perguntas que a banca pode fazer:
- "Por que voce tem duas APIs (Java e Python)?"
- "Como voce garantiria autenticacao na API?"
- "O que acontece se a API receber uma requisicao invalida?"

---

## TOPICO 9: Observabilidade e Monitoramento
**Prioridade: BAIXA | Tempo estimado: 3 horas**

### O que estudar:
1. **Tres pilares da observabilidade:**
   - **Metricas**: numeros (latencia, throughput, error rate)
   - **Logs**: eventos textuais (erros, warnings)
   - **Traces**: rastreamento de requests end-to-end

2. **Stack de monitoramento:**
   - Prometheus: coleta de metricas
   - Grafana: dashboards e visualizacao
   - Azure Monitor: metricas da nuvem
   - Application Insights: APM (Application Performance Monitoring)

3. **Metricas do projeto:**
   - `transactions_processed`: total processado
   - `frauds_detected`: fraudes encontradas
   - `processing_time_avg`: tempo medio de processamento
   - `error_rate`: taxa de erros
   - `fraud_rate`: taxa de fraude

### Onde estudar:
- Artigo: "Three Pillars of Observability" - Charity Majors
- Grafana docs: "Getting Started"
- Arquivo: `src/monitoring/metrics_collector.py`

### Exercicio pratico:
- Leia o `MetricsCollector` e entenda cada metrica
- Pense em 3 alertas criticos que configuraria (ex: error_rate > 5%, fraud_rate > 20%, latency > 5s)
- Acesse Grafana em http://localhost:3000 (admin/admin) no docker-compose

### Perguntas que a banca pode fazer:
- "Como voce detecta que o sistema esta com problemas antes dos usuarios perceberem?"
- "Qual a diferenca entre metricas e logs?"

---

## TOPICO 10: Docker e Containerizacao
**Prioridade: BAIXA | Tempo estimado: 2 horas**

### O que estudar:
1. **Docker basico:**
   - Imagem vs Container
   - Dockerfile: FROM, COPY, RUN, CMD, EXPOSE
   - Docker Compose: orquestracao de multiplos containers
   - Volumes: persistencia de dados
   - Networks: comunicacao entre containers

2. **Docker Compose do projeto:**
   - 10 servicos: API, Dashboard, MongoDB, Kafka, MinIO, PostgreSQL, Redis, Spark, Prometheus, Grafana
   - Como os servicos se comunicam (fraud-network)
   - Volumes para persistencia

### Onde estudar:
- Docker docs: "Get Started" (30 min)
- Arquivo: `docker-compose.yaml`
- Arquivo: `Dockerfile.api` e `Dockerfile.dashboard` (novos)

### Exercicio pratico:
- Execute `docker-compose up -d` e `docker-compose ps` para ver os servicos
- Acesse cada servico e entenda seu papel
- Pare um servico e veja o que acontece: `docker-compose stop mongodb`

---

## TOPICO 11: CI/CD e DevOps
**Prioridade: BAIXA | Tempo estimado: 2 horas**

### O que estudar:
1. **GitHub Actions:**
   - Workflows, jobs, steps
   - Triggers: push, pull_request, schedule
   - Arquivo: `gitactions.yaml`

2. **Pipeline ideal:**
   - Lint -> Test -> Build -> Deploy -> Smoke Test
   - Ambientes: dev -> staging -> production
   - Blue/green deployment

### Onde estudar:
- GitHub Actions docs: "Quickstart"
- Arquivo: `gitactions.yaml`

---

## CRONOGRAMA DE ESTUDO SUGERIDO

### Semana 1 (15h) - Fundamentos
| Dia | Topico | Horas |
|-----|--------|-------|
| Seg | Arquitetura de Dados (Topico 1) | 3h |
| Ter | Arquitetura de Dados (Topico 1) | 3h |
| Qua | Streaming e Ingestao (Topico 2) | 3h |
| Qui | Streaming e Ingestao (Topico 2) | 2h |
| Sex | ML para Fraude (Topico 3) | 4h |

### Semana 2 (15h) - Aprofundamento
| Dia | Topico | Horas |
|-----|--------|-------|
| Seg | ML para Fraude (Topico 3) | 4h |
| Ter | Terraform (Topico 4) | 4h |
| Qua | Data Quality (Topico 5) | 4h |
| Qui | LGPD e Seguranca (Topico 6) | 4h |
| Sex | Revisao semana 1 e 2 | 3h |

### Semana 3 (12h) - Complementos e Pratica
| Dia | Topico | Horas |
|-----|--------|-------|
| Seg | Spark (Topico 7) | 3h |
| Ter | APIs (Topico 8) | 3h |
| Qua | Observabilidade + Docker (Topicos 9 e 10) | 3h |
| Qui | Pratica: rodar demo completa e cronometrar apresentacao | 3h |
| Sex | Simulacao de perguntas da banca com um colega | 2h |

### Semana 4 (5h) - Revisao Final
| Dia | Topico | Horas |
|-----|--------|-------|
| Seg | Revisao de todos os pontos fracos | 2h |
| Ter | Ensaio geral da apresentacao (cronometrado) | 2h |
| Qua | **DIA DA APRESENTACAO** | - |

---

## FLASHCARDS - CONCEITOS CHAVE

Use estes para revisao rapida:

1. **Medallion Architecture:** Bronze (raw) -> Silver (limpo) -> Gold (enriquecido)
2. **Event Hubs:** Kafka gerenciado da Azure, escala por Throughput Units
3. **Isolation Forest:** Detecta anomalias isolando pontos em arvores aleatorias
4. **XGBoost:** Gradient boosting otimizado, excelente para dados tabulares
5. **Recall:** TP / (TP + FN) - fraudes detectadas sobre total de fraudes reais
6. **LGPD:** Lei 13.709/2018 - protecao de dados pessoais no Brasil
7. **Terraform:** IaC declarativo - descreve o estado desejado, nao os passos
8. **Great Expectations:** Framework Python para validacao de dados
9. **Data Drift:** Mudanca na distribuicao dos dados que degrada modelos ML
10. **Lazy Evaluation:** Spark so executa quando uma acao e chamada (collect, count, write)
11. **Checkpoint:** Marca ate onde o consumer processou no Event Hub
12. **RBAC:** Role-Based Access Control - permissoes por papel
13. **MLflow:** Plataforma para tracking de experimentos e registro de modelos
14. **Delta Lake:** Camada ACID sobre Data Lake (transactions, time travel)
15. **Feature Store:** Repositorio centralizado de features para ML
