from datetime import datetime

import pandas as pd
from django.http import JsonResponse
from django.shortcuts import render

from geomonitor.visualizador import (
    grafico_categorias,
    grafico_fontes,
    grafico_pizza,
    grafico_serie_temporal,
)
from monitor import pipeline


def index(request):
    df = pipeline.df_final.copy()

    cat = request.GET.get("cat", "").strip().lower()
    di = request.GET.get("di", "")
    df_v = request.GET.get("df", "")
    q = request.GET.get("q", "").strip()

    if cat:
        df = df[df["categoria_predita"] == cat]
    if di:
        df = df[df["data"] >= pd.to_datetime(di, errors="coerce")]
    if df_v:
        df = df[df["data"] <= pd.to_datetime(df_v, errors="coerce")]
    if q:
        df = df[df["titulo"].str.contains(q, case=False, na=False)]

    def cnt(c):
        return int((df["categoria_predita"] == c).sum())

    noticias = df[["titulo", "categoria_predita", "data", "fonte"]].copy()
    noticias["data"] = noticias["data"].dt.strftime("%d/%m/%Y").fillna("—")
    noticias = noticias.to_dict("records")

    context = {
        "total": len(df),
        "conflito": cnt("conflito"),
        "economia": cnt("economia"),
        "diplomacia": cnt("diplomacia"),
        "noticias": noticias,
        "img_barras": grafico_categorias(df),
        "img_pizza": grafico_pizza(df),
        "img_temporal": grafico_serie_temporal(df),
        "img_fontes": grafico_fontes(df),
        "cat": cat,
        "di": di,
        "df_val": df_v,
        "q": q,
        "agora": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }
    return render(request, "monitor/index.html", context)


def api_noticias(request):
    df = pipeline.df_final.copy()
    cat = request.GET.get("cat", "")
    if cat:
        df = df[df["categoria_predita"] == cat]
    df["data"] = df["data"].astype(str)
    data = df[["titulo", "texto", "data", "fonte", "categoria_predita"]].to_dict("records")
    return JsonResponse(data, safe=False)


def api_metricas(request):
    return JsonResponse(pipeline.classificador.metricas)
