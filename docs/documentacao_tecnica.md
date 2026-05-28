# GeoMonitor — Documentação Técnica Completa

**Disciplina:** Novas Tecnologias  
**Professor:** Adam Smith Gontijo  
**Turma:** B — Ciências Políticas (Relações Internacionais e Exteriores)  
**Grupo:** Arthur Murillo Brito · Arthur Escorcio Alves · Arthur Andre Beraldo Santos · Alberto Holanda · Gabriel Porto  
**Data:** Junho / 2025

---

## 1. Problema Real

O volume de notícias internacionais cresce exponencialmente, tornando inviável para analistas, estudantes e profissionais de relações internacionais acompanhar e categorizar manualmente eventos geopolíticos relevantes. O **GeoMonitor** automatiza a coleta, limpeza, classificação e visualização dessas notícias em um dashboard web interativo.

---

## 2. Requisitos

### 2.1 Funcionais

| Código | Descrição |
|--------|-----------|
| RF01 | Coletar notícias de fontes públicas confiáveis (CSV local / NewsAPI) |
| RF02 | Limpar e normalizar textos (remoção de ruído, duplicatas, stopwords) |
| RF03 | Classificar notícias automaticamente em: Conflito, Economia, Diplomacia |
| RF04 | Exibir dashboard com gráficos (barras, pizza, série temporal, fontes) |
| RF05 | Permitir filtros dinâmicos por categoria, período e busca por título |
| RF06 | Expor endpoints JSON para integração com outras aplicações |

### 2.2 Não-funcionais

| Código | Descrição |
|--------|-----------|
| RNF01 | **Usabilidade:** interface responsiva, tema escuro, navegação intuitiva |
| RNF02 | **Desempenho:** carregamento do dashboard em < 2 s para até 10 000 registros |
| RNF03 | **Rastreabilidade:** fonte exibida para cada notícia |
| RNF04 | **Privacidade:** apenas dados públicos; sem coleta de dados pessoais |
| RNF05 | **Modularidade:** arquitetura em camadas — coletor / processador / classificador / visualizador |
| RNF06 | **Testabilidade:** cobertura de testes unitários e de aceitação |

---

## 3. Escopo

### O que está incluído

- Coleta de notícias via CSV local (com estrutura pronta para NewsAPI)
- Pipeline NLP: limpeza → vetorização TF-IDF → classificação Logística
- Dashboard Flask com 4 visualizações Matplotlib
- Filtros dinâmicos (categoria, data, busca textual)
- API REST JSON (`/api/noticias`, `/api/metricas`)
- 25 testes automatizados (pytest)

### Limitações desta versão

- Dados estáticos em CSV; integração NewsAPI disponível mas não ativada por padrão
- Modelo simples (Regressão Logística); modelos transformer melhorariam a acurácia
- Interface sem autenticação; adequada para uso interno/acadêmico

---

## 4. Arquitetura do Sistema

```
┌──────────────────────────────────────────────────────┐
│                     Usuário (Browser)                │
└────────────────────────────┬─────────────────────────┘
                             │ HTTP GET / query params
┌────────────────────────────▼─────────────────────────┐
│              Flask (app.py)  — Camada Web             │
│   Rotas: /   /api/noticias   /api/metricas            │
└──────┬────────────────────────────────────┬──────────┘
       │                                    │
┌──────▼──────┐  ┌────────────┐  ┌─────────▼────────┐
│  Coletor    │  │ Processador │  │  Visualizador    │
│ (coletor.py)│  │(processador │  │(visualizador.py) │
│             │  │   .py)      │  │  Matplotlib      │
└──────┬──────┘  └─────┬──────┘  └──────────────────┘
       │               │
┌──────▼───────────────▼──────────────────────────────┐
│            Classificador (classificador.py)          │
│       Scikit-Learn: TF-IDF  +  Logistic Regression   │
└──────────────────────────────────────────────────────┘
       │
┌──────▼──────────────────────────────────────────────┐
│             Armazenamento (data/)                    │
│   noticias.csv  (entrada)   modelo.pkl (modelo ML)  │
└─────────────────────────────────────────────────────┘
```

**Fluxo de dados:**
```
CSV → ColetorNoticias.carregar_csv()
    → Processador.processar()       (limpeza + texto_limpo)
    → Classificador.treinar()       (TF-IDF + LogReg)
    → Classificador.prever_df()     (categoria_predita)
    → Visualizador.*()              (base64 PNG → template Flask)
    → render_template_string()      (HTML → Browser)
```

---

## 5. Descrição dos Módulos

### 5.1 `geomonitor/coletor.py` — ColetorNoticias

**Responsabilidade:** Ler e validar notícias de fontes externas.

| Método | Descrição |
|--------|-----------|
| `carregar_csv()` | Lê `data/noticias.csv` (sep=`;`), valida colunas, normaliza tipos |
| `buscar_newsapi()` | Consulta NewsAPI (requer chave; extensão futura) |
| `_validar_colunas()` | Verifica presença de titulo, texto, data, fonte, categoria |
| `_normalizar()` | Remove nulos, padroniza strings |

---

### 5.2 `geomonitor/processador.py` — Processador

**Responsabilidade:** Limpar e normalizar textos para o pipeline ML.

Passos aplicados a cada texto:
1. Remoção de acentos (NFKd Unicode)
2. Conversão para minúsculas
3. Remoção de URLs
4. Remoção de caracteres não-alfabéticos
5. Remoção de stopwords em português (lista built-in)
6. Descarte de tokens com ≤ 2 caracteres

---

### 5.3 `geomonitor/classificador.py` — Classificador

**Responsabilidade:** Treinar e aplicar modelo de classificação de texto.

**Pipeline Scikit-Learn:**
```
TfidfVectorizer(ngram_range=(1,2), max_features=5001, sublinear_tf=True)
    ↓
LogisticRegression(C=1.0, solver='lbfgs', max_iter=500)
```

**Categorias:** `conflito` | `economia` | `diplomacia`

**Métricas avaliadas:**
- Acurácia no conjunto de teste (holdout 20%)
- Cross-validation 3-fold (média ± desvio)
- Classification report (precision, recall, F1 por classe)
- Matriz de confusão

**Fallback:** classificação por palavras-chave quando modelo não está treinado.

---

### 5.4 `geomonitor/visualizador.py` — Visualizador

**Responsabilidade:** Gerar visualizações Matplotlib em base64 para embedding no HTML.

| Função | Gráfico |
|--------|---------|
| `grafico_categorias()` | Barras verticais por categoria |
| `grafico_pizza()` | Pizza com proporções |
| `grafico_serie_temporal()` | Linhas por mês/categoria |
| `grafico_fontes()` | Barras horizontais — top fontes |

Tema escuro (#0D1B2A) consistente com a identidade visual GeoMonitor.

---

### 5.5 `app.py` — Aplicação Flask

| Rota | Método | Descrição |
|------|--------|-----------|
| `/` | GET | Dashboard principal com filtros e gráficos |
| `/api/noticias` | GET | JSON com lista de notícias (filtro `?cat=`) |
| `/api/metricas` | GET | JSON com métricas do modelo ML |

**Parâmetros de query string (rota `/`):**

| Parâmetro | Tipo | Exemplo |
|-----------|------|---------|
| `cat` | string | `?cat=conflito` |
| `di` | date | `?di=2024-02-01` |
| `df` | date | `?df=2024-02-28` |
| `q` | string | `?q=ONU` |

---

## 6. Fontes de Dados

| Fonte | Tipo | Uso |
|-------|------|-----|
| `data/noticias.csv` | CSV local (sep=`;`) | Desenvolvimento e testes |
| NewsAPI (`newsapi.org`) | REST API | Extensão para dados em tempo real |

**Campos do CSV:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| titulo | str | Título da notícia |
| texto | str | Corpo / descrição |
| data | date (YYYY-MM-DD) | Data de publicação |
| fonte | str | Veículo jornalístico |
| categoria | str | Rótulo para treinamento |

---

## 7. Tecnologias e Bibliotecas

| Biblioteca | Versão mínima | Papel |
|------------|--------------|-------|
| **Scikit-Learn** | 1.4 | Biblioteca **principal** — TF-IDF + Classificação |
| **Flask** | 3.0 | Framework web (servidor e rotas) |
| **Pandas** | 2.1 | Manipulação de DataFrames |
| **Matplotlib** | 3.8 | Visualizações embutidas no dashboard |
| **NumPy** | 1.26 | Operações numéricas (dependência do pipeline ML) |
| **pytest** | 8.0 | Framework de testes |

---

## 8. Metodologia de Desenvolvimento

**Abordagem:** Kanban simplificado com 3 sprints:

| Sprint | Período | Entregável |
|--------|---------|-----------|
| 1 | Semana 1–2 | Levantamento, escopo, arquitetura, protótipo |
| 2 | Semana 3–4 | Módulos coletor, processador, classificador |
| 3 | Semana 5–6 | Dashboard Flask, testes, documentação, vídeo |

**Versionamento:** Git com branches `main` / `dev` / `feature/*`.

---

## 9. Testes e Validação

### 9.1 Testes Unitários

| Classe | Testes | Cobertura |
|--------|--------|-----------|
| TestColetor | 5 | Carregamento, colunas, nulos, datas, erro de path |
| TestProcessador | 6 | texto_limpo, duplicatas, minúsculas, caracteres, tokens mín. |
| TestClassificador | 7 | Métricas, acurácia, predição, persistência, fallback |

### 9.2 Testes de Aceitação

| Teste | Critério |
|-------|---------|
| test_pipeline_completo | DataFrame com `categoria_predita` ao fim do pipeline |
| test_filtro_por_categoria | Filtragem devolve apenas categoria solicitada |
| test_api_flask_noticias | Endpoint `/api/noticias` retorna JSON não-vazio |
| test_api_flask_metricas | Endpoint `/api/metricas` retorna dict de métricas |
| test_pagina_principal_carrega | HTTP 200 + conteúdo "GeoMonitor" |
| test_privacidade_sem_dados_sensiveis | Dataset sem CPF, e-mail, senha etc. |

### 9.3 Resultado Final

```
25 passed in 3.02s  (100% ✅)
```

---

## 10. Considerações Éticas, de Privacidade e Segurança

- **Dados públicos apenas:** o sistema não coleta, armazena nem processa dados pessoais identificáveis.
- **Transparência de fonte:** cada notícia exibe o veículo de origem, permitindo rastreabilidade.
- **Sem orientação política:** a classificação é factual (conflito/economia/diplomacia) e não emite julgamentos de valor.
- **Limitações do modelo ML:** o classificador pode errar em textos ambíguos; não deve ser usado como única fonte de análise.
- **Extensão com NewsAPI:** ao ativar APIs externas, deve-se respeitar os Termos de Serviço de cada provedor.

---

## 11. Estrutura de Arquivos

```
geomonitor/
├── app.py                    # Aplicação Flask principal
├── requirements.txt          # Dependências Python
├── data/
│   ├── noticias.csv          # Dataset local (24 notícias rotuladas)
│   └── modelo.pkl            # Modelo treinado (gerado em runtime)
├── geomonitor/
│   ├── __init__.py
│   ├── coletor.py            # Módulo de coleta
│   ├── processador.py        # Módulo de limpeza NLP
│   ├── classificador.py      # Módulo ML (Scikit-Learn)
│   └── visualizador.py       # Módulo de gráficos (Matplotlib)
└── tests/
    └── test_geomonitor.py    # 25 testes (pytest)
```

---

## 12. Como Executar

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Executar o servidor
python app.py
# → http://localhost:5001

# 3. Executar os testes
pytest tests/ -v
```

---

## 13. Próximos Passos

- Integração em tempo real com NewsAPI
- Análise de sentimento por notícia
- Exportação de relatórios em PDF
- Autenticação de usuários
- Deploy em nuvem (Railway / Render)
- Expansão do dataset e melhora do modelo (BERT/DistilBERT)
