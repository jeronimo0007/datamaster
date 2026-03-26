# Apresentacao para Banca - Sistema de Deteccao de Fraudes Bancarias

## Informacoes Gerais
- **Duracao Total:** 90 minutos
- **Formato:** Apresentacao + Demonstracao Pratica + Perguntas
- **Ferramentas:** Este documento + Demo local rodando via Docker

---

## PARTE 1: INTRODUCAO (15 minutos)

---

### Slide 1: Capa (1 min)
**Titulo:** Sistema de Deteccao de Fraudes Bancarias - Arquitetura Cloud-Native com Azure

**Notas do apresentador:**
- Cumprimente a banca
- Apresente-se brevemente
- Mencione que a apresentacao tera demonstracao pratica ao vivo

---

### Slide 2: Agenda (1 min)
**Conteudo:**
1. Contexto e Problema (5 min)
2. Visao Geral da Solucao (5 min)
3. Demonstracao Rapida (5 min)
4. Arquitetura Detalhada (30 min)
5. Demonstracao Tecnica (30 min)
6. Perguntas e Respostas (15 min)

---

### Slide 3: O Problema - Fraudes Bancarias no Brasil (3 min)
**Conteudo:**
- Em 2023, fraudes bancarias digitais causaram perdas de **R$ 2,5 bilhoes** no Brasil (Febraban)
- Aumento de **165%** em tentativas de fraude nos ultimos 3 anos
- PIX: 1,7 milhao de golpes registrados em 2023
- Tempo medio de deteccao manual: **72 horas** (vs. < 2 segundos com automacao)
- Falsos positivos bloqueiam transacoes legitimas e prejudicam a experiencia do cliente

**O que falar:**
> "Fraudes bancarias sao um problema crescente no Brasil. Com a digitalizacao dos meios de pagamento, especialmente o PIX, o volume de tentativas de fraude cresceu exponencialmente. O desafio nao e apenas detectar fraudes, mas detecta-las em tempo real, minimizando falsos positivos que bloqueiam clientes legitimos. Foi esse problema que motivou este projeto."

---

### Slide 4: Requisitos do Sistema (2 min)
**Conteudo:**
| Requisito | Meta |
|-----------|------|
| Latencia | < 2 segundos para deteccao |
| Precisao | > 95% recall em fraudes |
| Escala | 10M+ transacoes/dia |
| Disponibilidade | 99.9% SLA |
| Conformidade | LGPD completa |
| Custo | ~R$ 3.000/mes para producao |

**O que falar:**
> "Definimos requisitos claros e mensuráveis para o sistema. A latencia de menos de 2 segundos e critica - uma fraude em PIX precisa ser bloqueada antes da compensacao. O recall acima de 95% garante que quase nenhuma fraude passe despercebida."

---

### Slide 5: Visao Geral da Solucao (3 min)
**Conteudo - Diagrama de alto nivel:**
```
[Fontes de Dados] --> [Ingestao (Event Hubs/Kafka)]
                          |
                    [Processamento (Spark/Databricks)]
                          |
              +-----------+-----------+
              |           |           |
        [Data Lake]  [Warehouse]  [ML Models]
              |           |           |
        [Data Quality] [Dashboard] [API de Predicao]
              |           |           |
        [Governanca]  [Power BI]  [Alertas]
```

**O que falar:**
> "A solucao segue uma arquitetura cloud-native na Azure, com processamento em tempo real e batch. Os dados fluem desde as fontes, passam por ingestao via Event Hubs, sao processados no Databricks, armazenados em multiplas camadas no Data Lake, e alimentam tanto dashboards quanto modelos de machine learning para deteccao automatica."

---

### Slide 6: Stack Tecnologica (2 min)
**Conteudo:**
- **Cloud:** Azure (Event Hubs, Databricks, Data Lake Gen2, Synapse, Cosmos DB, ML)
- **Linguagens:** Python (Data/ML), Java (APIs Spring Boot)
- **Processamento:** Apache Spark, PySpark
- **ML:** Scikit-learn, XGBoost, MLflow
- **Infraestrutura:** Terraform (IaC), Docker
- **Monitoramento:** Prometheus, Grafana, Azure Monitor
- **Data Quality:** Great Expectations, Evidently
- **Seguranca:** Azure Key Vault, RBAC, Mascaramento LGPD

---

### Slide 7: Demo Rapida - Sistema Rodando (3 min)
**DEMONSTRACAO AO VIVO:**
1. Abra o terminal e execute: `docker-compose up -d`
2. Mostre o dashboard Streamlit em http://localhost:8501
3. Envie uma transacao via API: `curl -X POST http://localhost:8000/api/v1/transactions/analyze -H "Content-Type: application/json" -d '{"amount": 15000, "merchant_category": "Eletronicos", "user_country": "BR", "merchant_country": "US"}'`
4. Mostre o resultado da deteccao de fraude na resposta
5. Mostre o dashboard atualizando com a nova transacao

**O que falar:**
> "Antes de entrar nos detalhes, vou mostrar rapidamente o sistema funcionando. Temos uma API que recebe transacoes, um modelo de ML que analisa em tempo real, e um dashboard que visualiza tudo. Vamos ver isso na pratica."

---

## PARTE 2: ARQUITETURA DETALHADA (30 minutos)

---

### Slide 8: Arquitetura em Camadas (5 min)
**Conteudo - Diagrama Mermaid:**
```
Camada 1: INGESTAO
  - Azure Event Hubs (streaming em tempo real)
  - Azure Data Factory (batch historico)
  - Azure Functions (processamento serverless)

Camada 2: PROCESSAMENTO E ARMAZENAMENTO
  - Azure Databricks (Spark)
  - Data Lake Gen2 (Raw -> Processed -> Curated)
  - Azure Synapse (Data Warehouse)
  - Cosmos DB (operacional)

Camada 3: MACHINE LEARNING
  - Jupyter Notebooks (experimentacao)
  - Azure ML AutoML (treinamento)
  - MLflow (versionamento)
  - AKS endpoints (deploy)

Camada 4: SERVICOS E APIs
  - Spring Boot (Java API)
  - FastAPI (Python API)
  - Swagger/OpenAPI

Camada 5: OBSERVABILIDADE
  - Azure Monitor + Application Insights
  - Prometheus + Grafana
  - Log Analytics
```

**O que falar:**
> "A arquitetura foi organizada em 5 camadas bem definidas. Cada camada tem responsabilidades claras e pode escalar independentemente. Isso segue o principio de separacao de responsabilidades e facilita a manutencao."

---

### Slide 9: Data Lake Architecture - Medallion (5 min)
**Conteudo:**
```
BRONZE (Raw)          SILVER (Processed)       GOLD (Curated)
+-----------+         +---------------+         +-----------+
| JSON/CSV  |  ETL    | Parquet       |  Enrich | Features  |
| Sem schema| ------> | Schema valido | ------> | ML-ready  |
| Duplicatas|         | Limpo         |         | Agregados |
+-----------+         +---------------+         +-----------+
     |                       |                       |
  30 dias               90 dias                 Permanente
  retention             retention               retention
```

**O que falar:**
> "Adotamos a arquitetura Medallion com tres camadas. Os dados brutos chegam na camada Bronze sem transformacao. Na Silver, aplicamos limpeza, deduplicacao e validacao de schema. Na Gold, temos os dados prontos para consumo - features para ML, dados agregados para dashboards. Cada camada tem politicas diferentes de retencao e acesso."

**Ponto chave - MOSTRAR NO CODIGO:**
- Abra `notebooks/01_dataprep_dq.py` e mostre a classe `AzureDataPrep`
- Destaque os metodos `clean_transactions()` e `enrich_data()`

---

### Slide 10: Pipeline de Ingestao - Streaming (5 min)
**Conteudo:**
```
Transacao --> Event Hub --> Consumer --> Processamento --> Data Lake
   |              |            |              |              |
 <1ms          <10ms       <100ms         <500ms         <1s
```

**O que falar:**
> "O pipeline de streaming usa Azure Event Hubs, que e equivalente ao Kafka gerenciado. Ele suporta milhoes de eventos por segundo com latencia de milissegundos. O consumer processa cada evento, aplica o modelo de ML, e armazena no Data Lake. Todo o fluxo leva menos de 2 segundos."

**MOSTRAR NO CODIGO:**
- Abra `src/data_ingestion/event_hub_producer.py` - mostrando como enviamos eventos
- Abra `src/data_ingestion/event_hub_consumer.py` - mostrando como processamos

---

### Slide 11: Comparativo Azure vs AWS (5 min)
**Conteudo:**
| Funcionalidade | Azure | AWS |
|---------------|-------|-----|
| Streaming | Event Hubs | Kinesis |
| Data Lake | ADLS Gen2 | S3 |
| Processing | Databricks | EMR |
| Warehouse | Synapse | Redshift |
| NoSQL | Cosmos DB | DynamoDB |
| ML | Azure ML | SageMaker |
| Monitoring | Azure Monitor | CloudWatch |
| IaC | Terraform | Terraform/CDK |

**Justificativa Azure:**
1. Data centers no Brasil (compliance LGPD)
2. Integracao nativa com ecossistema Microsoft (Office 365, AD)
3. Databricks como servico gerenciado de primeira classe
4. Cosmos DB com multi-model e distribuicao global

**O que falar:**
> "Escolhemos Azure por tres razoes principais: data centers em Sao Paulo garantem compliance LGPD, a integracao com o ecossistema Microsoft que muitos bancos ja usam, e o Databricks como servico gerenciado de primeira classe. Mas a arquitetura e multi-cloud ready - todos os componentes tem equivalentes em AWS e GCP."

---

### Slide 12: Data Quality e Governanca (5 min)
**Conteudo:**
- **Great Expectations:** Validacoes automaticas nos dados
  - Schema validation (colunas obrigatorias)
  - Range checks (amount entre 0 e 1M)
  - Uniqueness (transaction_id unico)
  - Statistical checks (media de amount dentro do esperado)
- **Evidently:** Deteccao de data drift
- **Azure Purview:** Catalogo e linhagem de dados
- **Governanca YAML:** Regras declarativas em `governanca.yaml`

**MOSTRAR NO CODIGO:**
- Abra `notebooks/01_dataprep_dq.py` - classe `AzureDataQuality`
- Abra `governanca.yaml` - regras declarativas

**O que falar:**
> "Data Quality nao e opcional - dados ruins geram modelos ruins. Implementamos validacoes em multiplos niveis: schema, ranges, unicidade e estatisticas. O Great Expectations roda a cada ingestao e gera relatorios automaticos. Se detectarmos anomalias, alertas sao disparados antes que dados problematicos contaminem as camadas superiores."

---

### Slide 13: Seguranca e LGPD (5 min)
**Conteudo:**
1. **Mascaramento de Dados (PII):**
   - CPF: `123.456.789-00` -> `***.456.***-00`
   - Email: `usuario@email.com` -> `u*****@e***.com`
   - Telefone: `(11) 98765-4321` -> `(11) 9****-4321`
   - Cartao: `1234 5678 9012 3456` -> `**** **** **** 3456`

2. **Criptografia:** AES-256 em transito e repouso
3. **Azure Key Vault:** Gerenciamento seguro de secrets
4. **RBAC:** Controle de acesso baseado em papeis
5. **Audit Logs:** Todos os acessos registrados
6. **Data Retention:** Politicas automaticas de exclusao

**DEMONSTRACAO AO VIVO:**
```python
python -c "
from src.utils.data_masker import DataMasker
m = DataMasker()
print(m.mask_cpf('123.456.789-00'))
print(m.mask_email('joao.silva@banco.com.br'))
print(m.mask_card_number('1234 5678 9012 3456'))
"
```

**O que falar:**
> "A LGPD exige que dados pessoais sejam protegidos. Implementamos mascaramento para todos os campos PII - CPF, email, telefone, cartao. Em ambientes nao-produtivos, usamos anonimizacao via hash. Vou demonstrar o mascaramento funcionando."

---

## PARTE 3: DEMONSTRACAO TECNICA (30 minutos)

---

### Slide 14: Preparacao da Demo (2 min)
**Passos:**
1. Confirme que o Docker Compose esta rodando: `docker-compose ps`
2. Abra o dashboard: http://localhost:8501
3. Abra o Swagger da API: http://localhost:8000/docs
4. Tenha o terminal pronto para comandos

---

### Slide 15: Demo 1 - Geracao e Ingestao de Dados (5 min)
**Executar:**
```bash
# Gerar 100 transacoes de teste
python scripts/generate_data.py -n 100 -o data/transactions.json

# Mostrar os dados gerados
python -c "import json; data=json.load(open('data/transactions.json')); print(f'Total: {len(data)} transacoes'); print(f'Fraudes: {sum(1 for t in data if t[\"is_fraud\"])}'); print(json.dumps(data[0], indent=2))"
```

**O que falar:**
> "Primeiro, geramos dados simulados. O script cria transacoes com distribuicao realista - cerca de 5% sao fraudes, com valores mais altos e padroes anomalos. Vamos ver a estrutura de uma transacao."

---

### Slide 16: Demo 2 - API de Deteccao de Fraude (8 min)
**Executar:**
```bash
# Transacao normal (baixo risco)
curl -s -X POST http://localhost:8000/api/v1/transactions/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 150.00,
    "merchant_category": "Alimentacao",
    "user_country": "BR",
    "merchant_country": "BR",
    "payment_method": "PIX",
    "hour": 14,
    "is_weekend": 0,
    "is_international": 0
  }' | python -m json.tool

# Transacao suspeita (alto risco)
curl -s -X POST http://localhost:8000/api/v1/transactions/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 45000.00,
    "merchant_category": "Eletronicos",
    "user_country": "BR",
    "merchant_country": "US",
    "payment_method": "CREDIT_CARD",
    "hour": 3,
    "is_weekend": 1,
    "is_international": 1
  }' | python -m json.tool

# Processar lote de transacoes
curl -s -X POST http://localhost:8000/api/v1/transactions/batch \
  -H "Content-Type: application/json" \
  -d @data/transactions.json | python -m json.tool
```

**O que falar:**
> "Agora vamos usar a API. Primeiro envio uma transacao normal - um PIX de R$150 em alimentacao, mesmo pais. Veja que o score de fraude e baixo. Agora envio uma transacao suspeita - R$45.000 em eletronicos, cartao de credito, transacao internacional, de madrugada, no fim de semana. Veja como o score dispara. O modelo combina multiplas features para essa decisao."

---

### Slide 17: Demo 3 - Modelo de Machine Learning (5 min)
**Executar:**
```bash
# Mostrar metricas do modelo
curl -s http://localhost:8000/api/v1/model/metrics | python -m json.tool

# Mostrar importancia das features
curl -s http://localhost:8000/api/v1/model/feature-importance | python -m json.tool
```

**O que falar:**
> "O modelo usa um ensemble de Isolation Forest para deteccao de anomalias e XGBoost para classificacao supervisionada. As features mais importantes sao: valor da transacao, se e internacional, hora do dia e categoria do comerciante. O modelo e retreinado periodicamente com novos dados."

**Pontos para destacar:**
- Isolation Forest: detecta anomalias sem labels
- XGBoost: classificacao supervisionada com alto recall
- Ensemble: combina ambos para melhor performance
- Feature engineering: features temporais, comportamentais e de merchant

---

### Slide 18: Demo 4 - Dashboard de Monitoramento (5 min)
**DEMONSTRACAO AO VIVO:**
1. Abra http://localhost:8501
2. Mostre o painel com metricas gerais (total transacoes, fraudes, taxa)
3. Mostre o grafico de distribuicao de scores
4. Mostre a tabela de transacoes recentes com status
5. Mostre o grafico de fraudes por categoria
6. Envie novas transacoes e mostre atualizacao

**O que falar:**
> "O dashboard em Streamlit mostra tudo em tempo real. Temos KPIs no topo - total de transacoes, fraudes detectadas, taxa de fraude, tempo medio de processamento. Abaixo, graficos de distribuicao e a tabela de transacoes. Quando envio novas transacoes pela API, o dashboard atualiza automaticamente."

---

### Slide 19: Demo 5 - Data Quality (3 min)
**Executar:**
```bash
# Executar verificacao de qualidade
curl -s http://localhost:8000/api/v1/data-quality/report | python -m json.tool
```

**O que falar:**
> "A cada ingestao, executamos verificacoes automaticas de qualidade. O relatorio mostra quais regras passaram, quais falharam, e estatisticas dos dados. Isso garante que dados problematicos nao contaminem nossos modelos."

---

### Slide 20: Demo 6 - Mascaramento LGPD (2 min)
**Executar:**
```bash
# Demonstrar mascaramento
curl -s -X POST http://localhost:8000/api/v1/lgpd/mask \
  -H "Content-Type: application/json" \
  -d '{
    "cpf": "123.456.789-00",
    "email": "joao.silva@banco.com.br",
    "phone": "(11) 98765-4321",
    "name": "Joao Silva Santos",
    "card_number": "1234 5678 9012 3456",
    "amount": 1500.00
  }' | python -m json.tool
```

**O que falar:**
> "Para conformidade LGPD, implementamos mascaramento automatico de dados pessoais. Veja como o CPF, email, telefone e cartao sao mascarados, mas o campo amount que nao e PII permanece inalterado."

---

### Slide 21: Infraestrutura como Codigo - Terraform (2 min)
**MOSTRAR NO CODIGO:**
- Abra `infrastructure/terraform/environments/dev/main.tf`
- Destaque os recursos criados:
  - Resource Group
  - Storage Account (Data Lake Gen2)
  - Event Hubs
  - Cosmos DB
  - Key Vault
  - PostgreSQL

**O que falar:**
> "Toda a infraestrutura e definida como codigo com Terraform. Com um unico `terraform apply`, criamos todos os 8 recursos necessarios na Azure. Isso garante reproducibilidade - posso destruir e recriar o ambiente inteiro em minutos."

---

## PARTE 4: PERGUNTAS E RESPOSTAS (15 minutos)

---

### Perguntas Esperadas e Respostas Preparadas

#### P1: "Como o sistema escala para milhoes de transacoes?"
**Resposta:**
> "A escalabilidade e garantida em todas as camadas. Event Hubs escala por Throughput Units - cada TU suporta 1MB/s de entrada. Databricks tem auto-scaling de clusters. O Data Lake e virtualmente ilimitado. Cosmos DB escala por RU/s. Podemos ir de 1.000 a 10 milhoes de transacoes/dia ajustando apenas parametros, sem mudar codigo."

#### P2: "Qual o custo estimado para producao?"
**Resposta:**
> "Estimamos cerca de R$ 3.000/mes para 10 milhoes de transacoes/dia. O maior custo e o Databricks (~40%). Usamos otimizacoes como auto-pause, spot instances e reserved capacity. Em desenvolvimento, o custo cai para ~R$ 500/mes."

#### P3: "Como garantir conformidade com LGPD?"
**Resposta:**
> "Tres pilares: mascaramento automatico de PII em todas as camadas, criptografia AES-256 em transito e repouso, e audit logs de todos os acessos. Usamos Azure Key Vault para secrets e RBAC para controle de acesso. Dados pessoais tem politicas de retencao automatica."

#### P4: "Como os modelos de ML sao atualizados?"
**Resposta:**
> "Seguimos uma pipeline MLOps completa. O modelo e retreinado semanalmente com dados novos. Usamos MLflow para versionamento. A transicao usa canary deployment - o novo modelo recebe 10% do trafego inicialmente. Monitoramos data drift com Evidently para detectar quando o modelo precisa ser atualizado."

#### P5: "Qual a estrategia de disaster recovery?"
**Resposta:**
> "Backup automatico do Data Lake com replicacao cross-region para dados criticos. RTO de 4 horas para recuperacao completa e RPO de 15 minutos. O Terraform permite recriar toda a infraestrutura em uma nova regiao se necessario."

#### P6: "Por que Azure e nao AWS?"
**Resposta:**
> "Tres razoes: data centers em Sao Paulo para compliance LGPD, integracao nativa com ecossistema Microsoft que bancos ja usam, e Databricks como servico gerenciado de primeira classe. Porem, a arquitetura e multi-cloud ready - todos os componentes tem equivalentes diretos."

#### P7: "Como voce lidaria com falsos positivos?"
**Resposta:**
> "Falsos positivos sao tao prejudiciais quanto falsos negativos - bloqueiam clientes legitimos. Usamos um threshold ajustavel no modelo. Para transacoes com score entre 0.5 e 0.8, aplicamos verificacao adicional (SMS, biometria) em vez de bloquear. Acima de 0.8, bloqueamos automaticamente. O feedback dos analistas retroalimenta o modelo."

#### P8: "O que voce faria diferente se comecasse de novo?"
**Resposta:**
> "Investiria mais tempo em feature engineering com dados historicos reais. Tambem consideraria uma arquitetura baseada em feature store dedicado (como Feast ou Tecton) para desacoplar a engenharia de features do treinamento do modelo."

---

## CHECKLIST PRE-APRESENTACAO

### No dia anterior:
- [ ] Testar `docker-compose up` no ambiente da apresentacao
- [ ] Verificar que API responde em http://localhost:8000/docs
- [ ] Verificar que Dashboard abre em http://localhost:8501
- [ ] Gerar dados de teste: `python scripts/generate_data.py -n 500`
- [ ] Testar todos os comandos curl desta apresentacao
- [ ] Cronometrar a apresentacao (alvo: 75 min + 15 min Q&A)

### No dia:
- [ ] Executar `docker-compose up -d` 30 minutos antes
- [ ] Abrir todas as abas do navegador necessarias
- [ ] Ter terminal pronto com os comandos copiados
- [ ] Backup: ter screenshots das demos caso algo falhe
- [ ] Garrafa de agua

### Plano B (se a demo falhar):
- Tenha screenshots de cada tela do dashboard
- Tenha as respostas JSON salvas em arquivos
- Mostre o codigo fonte diretamente e explique a logica
- Foque nos diagramas de arquitetura e no codigo

---

## DICAS FINAIS

1. **Comece forte:** A demo rapida no inicio gera impacto e curiosidade
2. **Mostre codigo:** A banca quer ver que voce entende o codigo, nao so slides
3. **Use numeros:** Latencia, custos, throughput - numeros concretos impressionam
4. **Admita limitacoes:** Se algo nao foi implementado completamente, diga e explique o plano
5. **Conecte teoria e pratica:** Para cada conceito, mostre o codigo correspondente
6. **Controle o tempo:** Use um timer discreto; melhor terminar 5 min antes do que correr
7. **Respire:** Em perguntas dificeis, repita a pergunta, pense 3 segundos, depois responda
