"""
geomonitor/visualizador.py
Módulo de visualização de dados geopolíticos usando Matplotlib e Pandas.
"""

import os
import io
import base64
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # backend sem GUI – compatível com servidor
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import Counter

# Paleta de cores GeoMonitor
_CORES = {
    "conflito":   "#E53935",
    "economia":   "#43A047",
    "diplomacia": "#1E88E5",
    "outro":      "#757575",
}
_FUNDO = "#0D1B2A"
_TEXTO = "#E8EAF0"


def _estilo_escuro(fig, ax):
    """Aplica o tema escuro padrão do GeoMonitor."""
    fig.patch.set_facecolor(_FUNDO)
    ax.set_facecolor("#131F30")
    ax.tick_params(colors=_TEXTO)
    ax.xaxis.label.set_color(_TEXTO)
    ax.yaxis.label.set_color(_TEXTO)
    ax.title.set_color(_TEXTO)
    for spine in ax.spines.values():
        spine.set_edgecolor("#2A3F5F")


def _para_base64(fig) -> str:
    """Converte figura Matplotlib para string base64 (PNG)."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=120,
                facecolor=fig.get_facecolor())
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


# ──────────────────────────────────────────────────────────────────────
# Gráficos
# ──────────────────────────────────────────────────────────────────────

def grafico_categorias(df: pd.DataFrame, coluna: str = "categoria_predita") -> str:
    """Gráfico de barras: contagem por categoria."""
    contagem = df[coluna].value_counts()
    categorias = list(contagem.index)
    valores = list(contagem.values)
    cores = [_CORES.get(c, _CORES["outro"]) for c in categorias]

    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(categorias, valores, color=cores, width=0.55, zorder=3)
    _estilo_escuro(fig, ax)
    ax.set_title("Notícias por Categoria", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Categoria", fontsize=11)
    ax.set_ylabel("Quantidade", fontsize=11)
    ax.grid(axis="y", color="#2A3F5F", linestyle="--", alpha=0.6, zorder=0)

    for bar, v in zip(bars, valores):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                str(v), ha="center", va="bottom", color=_TEXTO, fontsize=11,
                fontweight="bold")

    plt.tight_layout()
    b64 = _para_base64(fig)
    plt.close(fig)
    return b64


def grafico_pizza(df: pd.DataFrame, coluna: str = "categoria_predita") -> str:
    """Gráfico de pizza com proporção de cada categoria."""
    contagem = df[coluna].value_counts()
    cores = [_CORES.get(c, _CORES["outro"]) for c in contagem.index]

    fig, ax = plt.subplots(figsize=(6, 5))
    wedges, texts, autotexts = ax.pie(
        contagem.values,
        labels=contagem.index,
        colors=cores,
        autopct="%1.1f%%",
        startangle=140,
        wedgeprops={"edgecolor": _FUNDO, "linewidth": 2},
    )
    for t in texts:
        t.set_color(_TEXTO)
        t.set_fontsize(11)
    for at in autotexts:
        at.set_color(_FUNDO)
        at.set_fontweight("bold")

    ax.set_facecolor(_FUNDO)
    fig.patch.set_facecolor(_FUNDO)
    ax.set_title("Distribuição de Categorias", fontsize=13, color=_TEXTO,
                 fontweight="bold", pad=10)

    plt.tight_layout()
    b64 = _para_base64(fig)
    plt.close(fig)
    return b64


def grafico_serie_temporal(df: pd.DataFrame,
                           coluna_data: str = "data",
                           coluna_cat: str = "categoria_predita") -> str:
    """Linha temporal: número de notícias por mês e categoria."""
    df = df.copy()
    df[coluna_data] = pd.to_datetime(df[coluna_data], errors="coerce")
    df = df.dropna(subset=[coluna_data])
    df["mes"] = df[coluna_data].dt.to_period("M")

    pivot = (df.groupby(["mes", coluna_cat])
               .size()
               .unstack(fill_value=0))

    fig, ax = plt.subplots(figsize=(9, 4))
    _estilo_escuro(fig, ax)

    for cat in pivot.columns:
        cor = _CORES.get(cat, _CORES["outro"])
        ax.plot(
            [str(p) for p in pivot.index],
            pivot[cat].values,
            marker="o", linewidth=2, color=cor, label=cat.capitalize(),
            markersize=6,
        )

    ax.set_title("Notícias por Mês e Categoria", fontsize=13, fontweight="bold")
    ax.set_xlabel("Mês", fontsize=10)
    ax.set_ylabel("Qtd", fontsize=10)
    ax.legend(facecolor="#131F30", labelcolor=_TEXTO, framealpha=0.8)
    ax.grid(color="#2A3F5F", linestyle="--", alpha=0.5)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    b64 = _para_base64(fig)
    plt.close(fig)
    return b64


def grafico_fontes(df: pd.DataFrame, top_n: int = 8) -> str:
    """Barras horizontais: fontes mais frequentes."""
    contagem = df["fonte"].value_counts().head(top_n)

    fig, ax = plt.subplots(figsize=(7, 4))
    _estilo_escuro(fig, ax)

    bars = ax.barh(contagem.index[::-1], contagem.values[::-1],
                   color="#1E88E5", height=0.55, zorder=3)
    ax.set_title(f"Top {top_n} Fontes", fontsize=13, fontweight="bold")
    ax.set_xlabel("Notícias", fontsize=10)
    ax.grid(axis="x", color="#2A3F5F", linestyle="--", alpha=0.5, zorder=0)

    for bar, v in zip(bars, contagem.values[::-1]):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                str(v), va="center", color=_TEXTO, fontsize=10)

    plt.tight_layout()
    b64 = _para_base64(fig)
    plt.close(fig)
    return b64


def salvar_graficos(df: pd.DataFrame, pasta: str = "static") -> dict:
    """Gera todos os gráficos e os salva como PNG na pasta indicada."""
    os.makedirs(pasta, exist_ok=True)

    graficos = {
        "barras": grafico_categorias(df),
        "pizza": grafico_pizza(df),
        "temporal": grafico_serie_temporal(df),
        "fontes": grafico_fontes(df),
    }

    for nome, b64 in graficos.items():
        caminho = os.path.join(pasta, f"{nome}.png")
        with open(caminho, "wb") as f:
            f.write(base64.b64decode(b64))

    return graficos   # retorna base64 strings também (para dashboard web)
