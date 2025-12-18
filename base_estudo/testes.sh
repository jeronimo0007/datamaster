# Testes unitários
pytest tests/ -v

# Testes de integração
pytest tests/integration/ -v

# Testes de performance
pytest tests/performance/ -v --benchmark-only

# Testes com cobertura
pytest --cov=src --cov-report=html

# Testes específicos
make test-data-quality
make test-ml-models
make test-api-endpoints