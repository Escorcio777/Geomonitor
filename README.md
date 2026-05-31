# GeoMonitor 🌍

**Monitoramento Geopolítico e Análise de Notícias Internacionais**

> Disciplina: Novas Tecnologias — Prof. Adam Smith Gontijo  
> Turma B — Ciências Políticas (Relações Internacionais e Exteriores)

---

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Execução

```bash
python manage.py runserver
# Acesse: http://localhost:8000
```

## Testes

```bash
pytest tests/ -v
# Resultado esperado: 25 passed
```

## Estrutura

```
geomonitor/
├── manage.py              # Entrada Django
├── requirements.txt
├── pytest.ini
├── config/                # Configurações Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── monitor/               # App Django (web)
│   ├── views.py           # Rotas e lógica de exibição
│   ├── urls.py
│   ├── apps.py            # Inicialização do pipeline ML
│   ├── pipeline.py        # Estado global do modelo
│   └── templates/monitor/
│       └── index.html     # Dashboard HTML
├── geomonitor/            # Pacote ML
│   ├── coletor.py         # Coleta de dados
│   ├── processador.py     # Limpeza NLP
│   ├── classificador.py   # ML (Scikit-Learn)
│   └── visualizador.py    # Gráficos (Matplotlib)
├── data/
│   └── noticias.csv       # Dataset
├── tests/
│   └── test_geomonitor.py # 25 testes
└── docs/
    ├── documentacao_tecnica.md
    └── explicacao_do_projeto.md
```

## Bibliotecas principais

| Biblioteca | Função |
|------------|--------|
| **Scikit-Learn** | Classificação TF-IDF + Regressão Logística |
| **Django** | Dashboard web e API REST |
| **Pandas** | Manipulação de dados |
| **Matplotlib** | Visualizações |
