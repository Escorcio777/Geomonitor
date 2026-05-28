"""
geomonitor/coletor.py
Módulo de coleta de dados de notícias geopolíticas.
Suporta carregamento de CSV local e integração com NewsAPI (opcional).
"""

import os
import pandas as pd
from datetime import datetime


class ColetorNoticias:
    """
    Coleta notícias de fontes configuradas.
    Por padrão usa dataset CSV local; pode ser estendido para APIs externas.
    """

    COLUNAS_ESPERADAS = ["titulo", "texto", "data", "fonte", "categoria"]

    def __init__(self, caminho_csv: str = None, api_key: str = None):
        """
        Parâmetros
        ----------
        caminho_csv : str
            Caminho para o arquivo CSV local com notícias.
        api_key : str
            Chave da NewsAPI (opcional – para uso futuro em tempo real).
        """
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.caminho_csv = caminho_csv or os.path.join(base, "data", "noticias.csv")
        self.api_key = api_key

    # ------------------------------------------------------------------
    # Fonte 1: CSV local
    # ------------------------------------------------------------------

    def carregar_csv(self) -> pd.DataFrame:
        """Lê o arquivo CSV e devolve um DataFrame validado."""
        if not os.path.exists(self.caminho_csv):
            raise FileNotFoundError(f"Arquivo não encontrado: {self.caminho_csv}")

        df = pd.read_csv(self.caminho_csv, sep=";", parse_dates=["data"])
        self._validar_colunas(df)
        df = self._normalizar(df)
        return df

    # ------------------------------------------------------------------
    # Fonte 2: NewsAPI (stub para extensão futura)
    # ------------------------------------------------------------------

    def buscar_newsapi(self, query: str = "geopolitics", idioma: str = "pt",
                       pagina_max: int = 1) -> pd.DataFrame:
        """
        Busca notícias na NewsAPI.
        Requer pacote 'requests' instalado e api_key válida.
        Devolve DataFrame no mesmo formato do CSV local.
        """
        try:
            import requests
        except ImportError:
            raise ImportError("Instale 'requests' para usar a NewsAPI.")

        if not self.api_key:
            raise ValueError("api_key não configurada.")

        registros = []
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "language": idioma,
            "pageSize": 20,
            "page": 1,
            "apiKey": self.api_key,
        }

        for pagina in range(1, pagina_max + 1):
            params["page"] = pagina
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            artigos = resp.json().get("articles", [])
            if not artigos:
                break
            for art in artigos:
                registros.append({
                    "titulo": art.get("title", ""),
                    "texto": art.get("description", "") or art.get("content", ""),
                    "data": art.get("publishedAt", ""),
                    "fonte": art.get("source", {}).get("name", "Desconhecida"),
                    "categoria": "",          # será preenchida pelo classificador
                })

        df = pd.DataFrame(registros)
        df["data"] = pd.to_datetime(df["data"], errors="coerce")
        df = self._normalizar(df)
        return df

    # ------------------------------------------------------------------
    # Helpers privados
    # ------------------------------------------------------------------

    def _validar_colunas(self, df: pd.DataFrame) -> None:
        faltando = [c for c in self.COLUNAS_ESPERADAS if c not in df.columns]
        if faltando:
            raise ValueError(f"Colunas ausentes no CSV: {faltando}")

    @staticmethod
    def _normalizar(df: pd.DataFrame) -> pd.DataFrame:
        """Garante tipos e remove linhas completamente vazias."""
        df = df.dropna(subset=["titulo", "texto"])
        df["titulo"] = df["titulo"].astype(str).str.strip()
        df["texto"] = df["texto"].astype(str).str.strip()
        df["fonte"] = df["fonte"].astype(str).str.strip()
        if "categoria" in df.columns:
            df["categoria"] = df["categoria"].astype(str).str.strip().str.lower()
        return df.reset_index(drop=True)
