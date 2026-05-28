# GeoMonitor 🌍

**Monitoramento Geopolítico e Análise de Notícias Internacionais**

> Disciplina: Novas Tecnologias — Prof. Adam Smith Gontijo  
> Turma B — Ciências Políticas (Relações Internacionais e Exteriores)

---

## Instalação

```bash
pip install -r requirements.txt
```

## Execução

```bash
python app.py
# Acesse: http://localhost:5001
```

## Testes

```bash
pytest tests/ -v
# Resultado esperado: 25 passed
```

## Estrutura

```
geomonitor/
├── app.py                 # Servidor Flask
├── requirements.txt
├── data/noticias.csv      # Dataset
├── geomonitor/
│   ├── coletor.py         # Coleta de dados
│   ├── processador.py     # Limpeza NLP
│   ├── classificador.py   # ML (Scikit-Learn)
│   └── visualizador.py    # Gráficos (Matplotlib)
├── tests/
│   └── test_geomonitor.py # 25 testes
└── docs/
    ├── documentacao_tecnica.md
    └── roteiro_video.md
```

## Bibliotecas principais

| Biblioteca | Função |
|------------|--------|
| **Scikit-Learn** | Classificação TF-IDF + Regressão Logística |
| **Flask** | Dashboard web e API REST |
| **Pandas** | Manipulação de dados |
| **Matplotlib** | Visualizações |
