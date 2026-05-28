"""
app.py  –  GeoMonitor: aplicação web Flask
Biblioteca web principal: Flask
Biblioteca ML principal: Scikit-Learn
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify
import pandas as pd

from geomonitor.coletor import ColetorNoticias
from geomonitor.processador import Processador
from geomonitor.classificador import Classificador
from geomonitor.visualizador import (
    grafico_categorias, grafico_pizza,
    grafico_serie_temporal, grafico_fontes,
)

# ──────────────────────────────────────────────────────────────────────
# Bootstrap: carrega dados e treina modelo na inicialização
# ──────────────────────────────────────────────────────────────────────

coletor      = ColetorNoticias()
processador  = Processador()
classificador = Classificador()

df_bruto    = coletor.carregar_csv()
df_limpo    = processador.processar(df_bruto)

if not classificador.carregar():
    classificador.treinar(df_limpo)

df_final = classificador.prever_df(df_limpo)

# ──────────────────────────────────────────────────────────────────────
# Flask app
# ──────────────────────────────────────────────────────────────────────

app = Flask(__name__)

# ─── Template HTML inline ─────────────────────────────────────────────
HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GeoMonitor – Monitoramento Geopolítico</title>
<style>
  :root {
    --bg:    #0D1B2A;
    --card:  #131F30;
    --border:#2A3F5F;
    --text:  #E8EAF0;
    --muted: #8899AA;
    --red:   #E53935;
    --green: #43A047;
    --blue:  #1E88E5;
    --accent:#00B4D8;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--bg); color: var(--text);
         font-family: 'Segoe UI', system-ui, sans-serif; min-height: 100vh; }

  /* ── Header ── */
  header { background: var(--card); border-bottom: 1px solid var(--border);
           padding: 1rem 2rem; display: flex; align-items: center; gap: 1rem; }
  header .logo { font-size: 1.6rem; font-weight: 800; letter-spacing: .06em;
                 color: var(--accent); text-transform: uppercase; }
  header .sub  { font-size: .8rem; color: var(--muted); }

  /* ── Layout ── */
  main { max-width: 1300px; margin: 0 auto; padding: 2rem; }

  /* ── KPI cards ── */
  .kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px,1fr));
          gap: 1rem; margin-bottom: 2rem; }
  .kpi  { background: var(--card); border: 1px solid var(--border);
          border-radius: 10px; padding: 1.2rem 1rem; text-align: center; }
  .kpi .val { font-size: 2rem; font-weight: 800; }
  .kpi .lbl { font-size: .75rem; color: var(--muted); margin-top: .3rem;
              text-transform: uppercase; letter-spacing: .05em; }
  .kpi.red   .val { color: var(--red); }
  .kpi.green .val { color: var(--green); }
  .kpi.blue  .val { color: var(--blue); }
  .kpi.white .val { color: var(--text); }

  /* ── Filtros ── */
  .filtros { background: var(--card); border: 1px solid var(--border);
             border-radius: 10px; padding: 1.2rem 1.5rem; margin-bottom: 2rem;
             display: flex; flex-wrap: wrap; gap: 1rem; align-items: flex-end; }
  .filtros label { font-size: .75rem; color: var(--muted); display: block;
                   margin-bottom: .3rem; text-transform: uppercase; }
  .filtros select, .filtros input {
    background: var(--bg); color: var(--text);
    border: 1px solid var(--border); border-radius: 6px;
    padding: .45rem .7rem; font-size: .9rem; outline: none; }
  .filtros select:focus, .filtros input:focus { border-color: var(--accent); }
  .btn { background: var(--accent); color: #000; border: none;
         border-radius: 6px; padding: .5rem 1.2rem; font-weight: 700;
         cursor: pointer; font-size: .9rem; transition: opacity .15s; }
  .btn:hover { opacity: .85; }
  .btn-reset { background: var(--border); color: var(--text); }

  /* ── Gráficos ── */
  .charts { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;
            margin-bottom: 2rem; }
  @media(max-width: 800px){ .charts { grid-template-columns: 1fr; } }
  .chart-card { background: var(--card); border: 1px solid var(--border);
                border-radius: 10px; padding: 1.2rem; }
  .chart-card h3 { font-size: .9rem; color: var(--muted); margin-bottom: .8rem;
                   text-transform: uppercase; letter-spacing: .06em; }
  .chart-card img { width: 100%; border-radius: 6px; display: block; }
  .chart-wide { grid-column: 1 / -1; }

  /* ── Tabela ── */
  .table-card { background: var(--card); border: 1px solid var(--border);
                border-radius: 10px; padding: 1.2rem; overflow-x: auto; }
  .table-card h3 { font-size: .9rem; color: var(--muted); margin-bottom: .8rem;
                   text-transform: uppercase; letter-spacing: .06em; }
  table { width: 100%; border-collapse: collapse; font-size: .88rem; }
  th { color: var(--muted); font-weight: 600; padding: .6rem .8rem;
       text-align: left; border-bottom: 1px solid var(--border);
       font-size: .75rem; text-transform: uppercase; }
  td { padding: .55rem .8rem; border-bottom: 1px solid #1a2a3a;
       vertical-align: top; }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: #192534; }
  .badge { display: inline-block; padding: .2rem .55rem; border-radius: 20px;
           font-size: .72rem; font-weight: 700; text-transform: uppercase; }
  .badge-conflito  { background: #3b1010; color: var(--red); }
  .badge-economia  { background: #0e2a10; color: var(--green); }
  .badge-diplomacia{ background: #0e1e3b; color: var(--blue); }
  .fonte { color: var(--muted); font-size: .8rem; }

  /* ── Footer ── */
  footer { text-align: center; padding: 2rem; color: var(--muted);
           font-size: .78rem; border-top: 1px solid var(--border); margin-top: 2rem; }
</style>
</head>
<body>

<header>
  <div>
    <div class="logo">⬡ GeoMonitor</div>
    <div class="sub">Monitoramento Geopolítico &amp; Análise de Notícias Internacionais</div>
  </div>
</header>

<main>

  <!-- KPIs -->
  <div class="kpis">
    <div class="kpi white"><div class="val">{{ total }}</div><div class="lbl">Total</div></div>
    <div class="kpi red">  <div class="val">{{ conflito }}</div><div class="lbl">Conflito</div></div>
    <div class="kpi green"><div class="val">{{ economia }}</div><div class="lbl">Economia</div></div>
    <div class="kpi blue"> <div class="val">{{ diplomacia }}</div><div class="lbl">Diplomacia</div></div>
  </div>

  <!-- Filtros -->
  <form class="filtros" method="GET" action="/">
    <div>
      <label>Categoria</label>
      <select name="cat">
        <option value="">Todas</option>
        <option value="conflito"   {% if cat=='conflito'   %}selected{% endif %}>Conflito</option>
        <option value="economia"   {% if cat=='economia'   %}selected{% endif %}>Economia</option>
        <option value="diplomacia" {% if cat=='diplomacia' %}selected{% endif %}>Diplomacia</option>
      </select>
    </div>
    <div>
      <label>Data inicial</label>
      <input type="date" name="di" value="{{ di }}">
    </div>
    <div>
      <label>Data final</label>
      <input type="date" name="df" value="{{ df_val }}">
    </div>
    <div>
      <label>Buscar título</label>
      <input type="text" name="q" value="{{ q }}" placeholder="Ex: ONU, China…">
    </div>
    <button class="btn" type="submit">Aplicar Filtros</button>
    <a href="/"><button class="btn btn-reset" type="button">Limpar</button></a>
  </form>

  <!-- Gráficos -->
  <div class="charts">
    <div class="chart-card">
      <h3>Distribuição por Categoria</h3>
      <img src="data:image/png;base64,{{ img_barras }}" alt="Barras">
    </div>
    <div class="chart-card">
      <h3>Proporção</h3>
      <img src="data:image/png;base64,{{ img_pizza }}" alt="Pizza">
    </div>
    <div class="chart-card chart-wide">
      <h3>Evolução Temporal</h3>
      <img src="data:image/png;base64,{{ img_temporal }}" alt="Temporal">
    </div>
    <div class="chart-card chart-wide">
      <h3>Principais Fontes</h3>
      <img src="data:image/png;base64,{{ img_fontes }}" alt="Fontes">
    </div>
  </div>

  <!-- Tabela de notícias -->
  <div class="table-card">
    <h3>Notícias Filtradas ({{ noticias|length }})</h3>
    <table>
      <thead>
        <tr>
          <th>Título</th>
          <th>Categoria</th>
          <th>Data</th>
          <th>Fonte</th>
        </tr>
      </thead>
      <tbody>
        {% for n in noticias %}
        <tr>
          <td>{{ n.titulo }}</td>
          <td><span class="badge badge-{{ n.categoria_predita }}">{{ n.categoria_predita }}</span></td>
          <td>{{ n.data }}</td>
          <td class="fonte">{{ n.fonte }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>

</main>

<footer>
  GeoMonitor © 2024 — Turma B · Novas Tecnologias · Prof. Adam Smith Gontijo<br>
  Dados atualizados em: {{ agora }} | Biblioteca principal: Scikit-Learn + Flask
</footer>
</body>
</html>
"""

# ──────────────────────────────────────────────────────────────────────
# Rotas
# ──────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    df = df_final.copy()

    # ── Filtros ──
    cat  = request.args.get("cat", "").strip().lower()
    di   = request.args.get("di", "")
    df_v = request.args.get("df", "")
    q    = request.args.get("q", "").strip()

    if cat:
        df = df[df["categoria_predita"] == cat]
    if di:
        df = df[df["data"] >= pd.to_datetime(di, errors="coerce")]
    if df_v:
        df = df[df["data"] <= pd.to_datetime(df_v, errors="coerce")]
    if q:
        df = df[df["titulo"].str.contains(q, case=False, na=False)]

    # ── KPIs (sobre dados filtrados) ──
    def cnt(c): return int((df["categoria_predita"] == c).sum())

    # ── Gráficos (sobre dados filtrados) ──
    img_barras   = grafico_categorias(df)
    img_pizza    = grafico_pizza(df)
    img_temporal = grafico_serie_temporal(df)
    img_fontes   = grafico_fontes(df)

    noticias = df[["titulo", "categoria_predita", "data", "fonte"]].copy()
    noticias["data"] = noticias["data"].dt.strftime("%d/%m/%Y").fillna("—")
    noticias = noticias.to_dict("records")

    return render_template_string(
        HTML,
        total=len(df),
        conflito=cnt("conflito"),
        economia=cnt("economia"),
        diplomacia=cnt("diplomacia"),
        noticias=noticias,
        img_barras=img_barras,
        img_pizza=img_pizza,
        img_temporal=img_temporal,
        img_fontes=img_fontes,
        cat=cat, di=di, df_val=df_v, q=q,
        agora=datetime.now().strftime("%d/%m/%Y %H:%M"),
    )


@app.route("/api/noticias")
def api_noticias():
    """Endpoint JSON – lista de notícias com filtros."""
    df = df_final.copy()
    cat = request.args.get("cat", "")
    if cat:
        df = df[df["categoria_predita"] == cat]
    df["data"] = df["data"].astype(str)
    return jsonify(df[["titulo", "texto", "data", "fonte", "categoria_predita"]]
                   .to_dict("records"))


@app.route("/api/metricas")
def api_metricas():
    """Endpoint JSON – métricas do modelo."""
    return jsonify(classificador.metricas)


# ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5001)
