"""
API FastAPI para o Sistema de Deteccao de Fraudes Bancarias.
Funciona localmente sem dependencias de cloud Azure.
"""
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Adicionar paths do projeto
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from monitoring.metrics_collector import MetricsCollector
from ml_models.fraud_model import FraudDetectionModel, train_and_save_model
from utils.data_masker import DataMasker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar app
app = FastAPI(
    title="API de Deteccao de Fraudes Bancarias",
    description=(
        "Sistema de deteccao de fraudes em tempo real para transacoes "
        "bancarias. Utiliza ensemble de Isolation Forest + XGBoost."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Componentes globais
model = FraudDetectionModel()
masker = DataMasker()
metrics = MetricsCollector()

# Armazenamento em memoria para demo
transactions_store: List[Dict[str, Any]] = []
alerts_store: List[Dict[str, Any]] = []


# --------------- Modelos Pydantic ---------------

class TransactionInput(BaseModel):
    """Dados de entrada para analise de transacao."""

    amount: float = Field(..., description="Valor da transacao em BRL", ge=0)
    merchant_category: str = Field(
        default="Outros", description="Categoria do comerciante"
    )
    user_country: str = Field(default="BR", description="Pais do usuario")
    merchant_country: str = Field(
        default="BR", description="Pais do comerciante"
    )
    payment_method: str = Field(
        default="PIX", description="Metodo de pagamento"
    )
    hour: Optional[int] = Field(
        default=None, description="Hora da transacao (0-23)"
    )
    is_weekend: Optional[int] = Field(
        default=None, description="Se e fim de semana (0 ou 1)"
    )
    is_international: Optional[int] = Field(
        default=None, description="Se e transacao internacional (0 ou 1)"
    )
    transaction_id: Optional[str] = Field(
        default=None, description="ID da transacao"
    )
    user_id: Optional[str] = Field(default=None, description="ID do usuario")


class MaskInput(BaseModel):
    """Dados para mascaramento LGPD."""

    cpf: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    name: Optional[str] = None
    card_number: Optional[str] = None
    amount: Optional[float] = None


class HealthResponse(BaseModel):
    """Resposta de health check."""

    status: str
    model_loaded: bool
    transactions_processed: int
    uptime_seconds: float
    timestamp: str


# --------------- Startup ---------------

@app.on_event("startup")
async def startup_event():
    """Carrega ou treina o modelo na inicializacao."""
    global model
    model_path = PROJECT_ROOT / "models" / "fraud_model.pkl"

    try:
        model.load(str(model_path))
        logger.info("Modelo carregado com sucesso")
    except FileNotFoundError:
        logger.info("Modelo nao encontrado. Treinando novo modelo...")
        model = train_and_save_model(5000)
        logger.info("Modelo treinado e salvo com sucesso")


# --------------- Endpoints ---------------

@app.get("/", tags=["Health"])
async def root():
    """Endpoint raiz."""
    return {
        "service": "Fraud Detection API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running",
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Verifica o estado do servico."""
    current_metrics = metrics.get_metrics()
    return HealthResponse(
        status="healthy",
        model_loaded=model.is_trained,
        transactions_processed=current_metrics["transactions_processed"],
        uptime_seconds=current_metrics["uptime_seconds"],
        timestamp=datetime.utcnow().isoformat(),
    )


@app.post("/api/v1/transactions/analyze", tags=["Transactions"])
async def analyze_transaction(transaction: TransactionInput):
    """
    Analisa uma transacao e retorna score de fraude.

    O score varia de 0 (seguro) a 1 (fraude certa).
    - score < 0.3: LOW risk -> APPROVE
    - 0.3 <= score < 0.5: MEDIUM risk -> MONITOR
    - 0.5 <= score < 0.8: HIGH risk -> REVIEW
    - score >= 0.8: CRITICAL risk -> BLOCK
    """
    import time
    import uuid

    start_time = time.time()

    try:
        # Preparar dados para predicao
        now = datetime.utcnow()
        tx_data = {
            "amount": transaction.amount,
            "merchant_category": transaction.merchant_category,
            "payment_method": transaction.payment_method,
            "hour": (
                transaction.hour if transaction.hour is not None else now.hour
            ),
            "is_weekend": (
                transaction.is_weekend
                if transaction.is_weekend is not None
                else int(now.weekday() >= 5)
            ),
            "is_international": (
                transaction.is_international
                if transaction.is_international is not None
                else int(
                    transaction.user_country != transaction.merchant_country
                )
            ),
        }

        # Predicao
        result = model.predict(tx_data)

        processing_time = time.time() - start_time

        # Registrar metricas
        metrics.record_transaction(
            is_fraud=result["is_fraud"],
            processing_time=processing_time,
        )

        # Armazenar para o dashboard
        tx_record = {
            "transaction_id": transaction.transaction_id or str(uuid.uuid4()),
            "user_id": transaction.user_id or "anonymous",
            "amount": transaction.amount,
            "merchant_category": transaction.merchant_category,
            "payment_method": transaction.payment_method,
            "user_country": transaction.user_country,
            "merchant_country": transaction.merchant_country,
            "fraud_score": result["fraud_score"],
            "is_fraud": result["is_fraud"],
            "risk_level": result["risk_level"],
            "recommended_action": result["recommended_action"],
            "processing_time_ms": round(processing_time * 1000, 2),
            "timestamp": now.isoformat(),
        }
        transactions_store.append(tx_record)

        # Criar alerta se fraude
        if result["is_fraud"]:
            alert = {
                "alert_id": str(uuid.uuid4()),
                "transaction_id": tx_record["transaction_id"],
                "fraud_score": result["fraud_score"],
                "risk_level": result["risk_level"],
                "amount": transaction.amount,
                "timestamp": now.isoformat(),
                "status": "OPEN",
            }
            alerts_store.append(alert)

        return {
            "transaction_id": tx_record["transaction_id"],
            **result,
            "processing_time_ms": tx_record["processing_time_ms"],
        }

    except Exception as e:
        metrics.record_error()
        logger.error(f"Erro ao analisar transacao: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/transactions/batch", tags=["Transactions"])
async def analyze_batch(transactions: List[TransactionInput]):
    """Analisa um lote de transacoes."""
    results = []
    for tx in transactions:
        result = await analyze_transaction(tx)
        results.append(result)

    total_frauds = sum(1 for r in results if r["is_fraud"])

    return {
        "total_analyzed": len(results),
        "total_frauds_detected": total_frauds,
        "fraud_rate": round(total_frauds / max(len(results), 1), 4),
        "results": results,
    }


@app.get("/api/v1/transactions", tags=["Transactions"])
async def list_transactions(limit: int = 50):
    """Lista transacoes processadas recentemente."""
    return {
        "total": len(transactions_store),
        "transactions": transactions_store[-limit:],
    }


@app.get("/api/v1/alerts", tags=["Alerts"])
async def list_alerts(limit: int = 50):
    """Lista alertas de fraude."""
    return {
        "total": len(alerts_store),
        "open": sum(1 for a in alerts_store if a["status"] == "OPEN"),
        "alerts": alerts_store[-limit:],
    }


@app.get("/api/v1/model/metrics", tags=["Model"])
async def get_model_metrics():
    """Retorna metricas do modelo de ML."""
    if not model.is_trained:
        raise HTTPException(status_code=503, detail="Modelo nao treinado")
    return model.get_metrics()


@app.get("/api/v1/model/feature-importance", tags=["Model"])
async def get_feature_importance():
    """Retorna importancia das features do modelo."""
    if not model.is_trained:
        raise HTTPException(status_code=503, detail="Modelo nao treinado")
    return model.get_feature_importance()


@app.get("/api/v1/metrics", tags=["Monitoring"])
async def get_system_metrics():
    """Retorna metricas do sistema."""
    return metrics.get_metrics()


@app.post("/api/v1/lgpd/mask", tags=["LGPD"])
async def mask_pii_data(data: MaskInput):
    """
    Mascara dados pessoais conforme LGPD.

    Campos suportados: cpf, email, phone, name, card_number.
    Campos nao-PII (como amount) sao retornados sem alteracao.
    """
    input_dict = data.model_dump(exclude_none=True)
    masked = masker.mask_pii(input_dict)

    return {
        "original_fields": list(input_dict.keys()),
        "masked_data": masked,
        "masked_at": datetime.utcnow().isoformat(),
    }


@app.get("/api/v1/data-quality/report", tags=["Data Quality"])
async def get_data_quality_report():
    """Retorna relatorio de qualidade dos dados processados."""
    if not transactions_store:
        return {
            "status": "no_data",
            "message": "Nenhuma transacao processada ainda",
        }

    import statistics

    amounts = [t["amount"] for t in transactions_store]
    scores = [t["fraud_score"] for t in transactions_store]

    # Validacoes
    checks = []

    # Check 1: Nao nulos
    null_amounts = sum(1 for t in transactions_store if t["amount"] is None)
    checks.append(
        {
            "rule": "amount_not_null",
            "passed": null_amounts == 0,
            "details": f"{null_amounts} valores nulos encontrados",
        }
    )

    # Check 2: Range de valores
    out_of_range = sum(
        1
        for t in transactions_store
        if t["amount"] < 0 or t["amount"] > 1000000
    )
    checks.append(
        {
            "rule": "amount_range_0_1M",
            "passed": out_of_range == 0,
            "details": f"{out_of_range} valores fora do range",
        }
    )

    # Check 3: Unicidade de transaction_id
    tx_ids = [t["transaction_id"] for t in transactions_store]
    duplicates = len(tx_ids) - len(set(tx_ids))
    checks.append(
        {
            "rule": "transaction_id_unique",
            "passed": duplicates == 0,
            "details": f"{duplicates} IDs duplicados",
        }
    )

    # Check 4: Distribuicao de fraude
    fraud_rate = sum(
        1 for t in transactions_store if t["is_fraud"]
    ) / max(len(transactions_store), 1)
    checks.append(
        {
            "rule": "fraud_rate_below_50pct",
            "passed": fraud_rate < 0.5,
            "details": f"Taxa de fraude: {fraud_rate:.2%}",
        }
    )

    return {
        "report_timestamp": datetime.utcnow().isoformat(),
        "total_records": len(transactions_store),
        "all_passed": all(c["passed"] for c in checks),
        "checks": checks,
        "statistics": {
            "amount_mean": round(statistics.mean(amounts), 2),
            "amount_median": round(statistics.median(amounts), 2),
            "amount_stddev": (
                round(statistics.stdev(amounts), 2)
                if len(amounts) > 1
                else 0
            ),
            "amount_min": round(min(amounts), 2),
            "amount_max": round(max(amounts), 2),
            "fraud_score_mean": round(statistics.mean(scores), 4),
            "fraud_rate": round(fraud_rate, 4),
        },
    }


@app.get("/api/v1/dashboard/summary", tags=["Dashboard"])
async def get_dashboard_summary():
    """Retorna resumo para o dashboard."""
    current_metrics = metrics.get_metrics()

    # Distribuicao por categoria
    category_counts: Dict[str, int] = {}
    category_frauds: Dict[str, int] = {}
    for t in transactions_store:
        cat = t.get("merchant_category", "Outros")
        category_counts[cat] = category_counts.get(cat, 0) + 1
        if t.get("is_fraud"):
            category_frauds[cat] = category_frauds.get(cat, 0) + 1

    # Distribuicao por metodo de pagamento
    payment_counts: Dict[str, int] = {}
    for t in transactions_store:
        pm = t.get("payment_method", "Outros")
        payment_counts[pm] = payment_counts.get(pm, 0) + 1

    # Scores
    scores = [t["fraud_score"] for t in transactions_store]
    score_distribution = {
        "low_0_30": sum(1 for s in scores if s < 0.3),
        "medium_30_50": sum(1 for s in scores if 0.3 <= s < 0.5),
        "high_50_80": sum(1 for s in scores if 0.5 <= s < 0.8),
        "critical_80_100": sum(1 for s in scores if s >= 0.8),
    }

    return {
        "kpis": {
            "total_transactions": current_metrics["transactions_processed"],
            "total_frauds": current_metrics["frauds_detected"],
            "fraud_rate": current_metrics.get("fraud_rate", 0),
            "avg_processing_time_ms": round(
                current_metrics.get("processing_time_avg", 0) * 1000, 2
            ),
            "error_rate": current_metrics.get("error_rate", 0),
        },
        "score_distribution": score_distribution,
        "category_distribution": category_counts,
        "category_fraud_counts": category_frauds,
        "payment_distribution": payment_counts,
        "recent_transactions": transactions_store[-10:],
        "recent_alerts": alerts_store[-5:],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
