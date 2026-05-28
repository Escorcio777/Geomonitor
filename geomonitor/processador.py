"""
geomonitor/processador.py
Módulo de limpeza e pré-processamento de texto.
"""

import re
import unicodedata
import pandas as pd


# Stopwords simples em português (sem dependências externas)
_STOPWORDS_PT = {
    "a", "o", "e", "de", "do", "da", "em", "um", "uma", "com", "por",
    "para", "que", "se", "no", "na", "os", "as", "ao", "à", "mais",
    "mas", "foi", "são", "após", "entre", "sobre", "após", "seus",
    "suas", "isso", "este", "esta", "estes", "estas", "esse", "essa",
    "dos", "das", "nos", "nas", "pelo", "pela", "pelos", "pelas",
    "ele", "ela", "eles", "elas", "eu", "nós", "vocês", "você",
    "também", "já", "como", "quando", "onde", "porque", "então",
    "até", "desde", "durante", "sem", "sob", "ante", "após", "contra",
    "entre", "perante", "segundo", "versus", "via", "há", "ter",
    "ser", "estar", "ter", "fazer", "poder", "dever",
}


class Processador:
    """
    Aplica limpeza e normalização nos textos das notícias.
    """

    def __init__(self, remover_stopwords: bool = True, min_tokens: int = 3):
        self.remover_stopwords = remover_stopwords
        self.min_tokens = min_tokens

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def processar(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Recebe um DataFrame bruto e devolve um DataFrame limpo com a
        coluna extra 'texto_limpo'.
        """
        df = df.copy()
        df = self._remover_duplicatas(df)
        df["texto_limpo"] = (df["titulo"] + " " + df["texto"]).apply(self._limpar_texto)
        df = df[df["texto_limpo"].str.split().str.len() >= self.min_tokens]
        return df.reset_index(drop=True)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _limpar_texto(self, texto: str) -> str:
        texto = self._remover_acentos(texto)
        texto = texto.lower()
        texto = re.sub(r"http\S+|www\S+", " ", texto)          # URLs
        texto = re.sub(r"[^a-z\s]", " ", texto)                # pontuação / números
        texto = re.sub(r"\s+", " ", texto).strip()             # espaços extras
        tokens = texto.split()
        if self.remover_stopwords:
            tokens = [t for t in tokens if t not in _STOPWORDS_PT and len(t) > 2]
        return " ".join(tokens)

    @staticmethod
    def _remover_acentos(texto: str) -> str:
        nfkd = unicodedata.normalize("NFKD", texto)
        return "".join(c for c in nfkd if not unicodedata.combining(c))

    @staticmethod
    def _remover_duplicatas(df: pd.DataFrame) -> pd.DataFrame:
        return df.drop_duplicates(subset=["titulo"]).reset_index(drop=True)
