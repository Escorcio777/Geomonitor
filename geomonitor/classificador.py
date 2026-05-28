"""
geomonitor/classificador.py
Módulo de classificação automática de notícias usando Scikit-Learn.
Biblioteca principal conforme escopo do projeto.
"""

import os
import pickle
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import numpy as np


CATEGORIAS = ["conflito", "economia", "diplomacia"]

# Palavras-chave de fallback para classificação por regras
_KEYWORDS = {
    "conflito": [
        "ataque", "guerra", "militar", "bomba", "ofensiva", "tropas", "armado",
        "violencia", "rebeldes", "terrorista", "missil", "combate", "batalha",
        "refugiados", "evacuacao", "guerrilha", "bombardeio", "explosao",
        "mortos", "feridos", "submarines", "submarino", "nuclear", "armas",
    ],
    "economia": [
        "economia", "mercado", "bolsa", "inflacao", "pib", "banco", "juros",
        "comercio", "exportacao", "importacao", "investimento", "moeda",
        "cambio", "dolar", "euro", "petroleo", "opep", "fmi", "crescimento",
        "recessao", "emprego", "desemprego", "crypto", "bitcoin", "commodities",
    ],
    "diplomacia": [
        "acordo", "tratado", "negociacao", "embaixada", "diplomatico", "onu",
        "g7", "g20", "cimeira", "reuniao", "bilateral", "multilateral",
        "sancoes", "cooperacao", "pacto", "mediacao", "paz", "cessar",
        "embaixador", "ministerio", "relacoes", "exteriores", "nato", "otan",
    ],
}


class Classificador:
    """
    Treina e aplica um pipeline TF-IDF + Regressão Logística para
    classificar notícias em: conflito | economia | diplomacia.
    """

    def __init__(self, caminho_modelo: str = None):
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.caminho_modelo = caminho_modelo or os.path.join(base, "data", "modelo.pkl")
        self.pipeline: Pipeline | None = None
        self.treinado: bool = False
        self.metricas: dict = {}

    # ------------------------------------------------------------------
    # Treino
    # ------------------------------------------------------------------

    def treinar(self, df: pd.DataFrame, coluna_texto: str = "texto_limpo",
                coluna_label: str = "categoria") -> dict:
        """
        Treina o pipeline e persiste o modelo em disco.
        Devolve métricas de avaliação.
        """
        df_rot = df[df[coluna_label].isin(CATEGORIAS)].copy()
        if df_rot.empty:
            raise ValueError("Sem exemplos rotulados para treinamento.")

        X = df_rot[coluna_texto].values
        y = df_rot[coluna_label].values

        self.pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(
                ngram_range=(1, 2),
                max_features=5001,
                sublinear_tf=True,
            )),
            ("clf", LogisticRegression(
                max_iter=500,
                C=1.0,
                solver="lbfgs",
                
                random_state=42,
            )),
        ])

        if len(df_rot) >= 10:
            X_tr, X_te, y_tr, y_te = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            self.pipeline.fit(X_tr, y_tr)
            y_pred = self.pipeline.predict(X_te)
            acc = accuracy_score(y_te, y_pred)
            report = classification_report(y_te, y_pred, output_dict=True)
            cm = confusion_matrix(y_te, y_pred, labels=CATEGORIAS)

            # Cross-validation com todos os dados
            cv_scores = cross_val_score(self.pipeline, X, y, cv=3, scoring="accuracy")
            self.metricas = {
                "acuracia_teste": round(float(acc), 4),
                "cv_media": round(float(cv_scores.mean()), 4),
                "cv_std": round(float(cv_scores.std()), 4),
                "report": report,
                "matriz_confusao": cm.tolist(),
                "labels": CATEGORIAS,
                "n_treino": len(X_tr),
                "n_teste": len(X_te),
            }
            # Retreina com todos os dados
            self.pipeline.fit(X, y)
        else:
            self.pipeline.fit(X, y)
            self.metricas = {"aviso": "Poucos dados; métricas não calculadas."}

        self.treinado = True
        self._salvar()
        return self.metricas

    # ------------------------------------------------------------------
    # Predição
    # ------------------------------------------------------------------

    def prever(self, textos) -> list[str]:
        """
        Classifica uma lista de textos (ou único texto).
        Usa modelo treinado se disponível; senão usa regras por palavras-chave.
        """
        if isinstance(textos, str):
            textos = [textos]

        if self.treinado and self.pipeline:
            return list(self.pipeline.predict(textos))

        # Fallback por palavras-chave
        return [self._classificar_por_keywords(t) for t in textos]

    def prever_df(self, df: pd.DataFrame,
                  coluna: str = "texto_limpo") -> pd.DataFrame:
        """Adiciona coluna 'categoria_predita' ao DataFrame."""
        df = df.copy()
        df["categoria_predita"] = self.prever(df[coluna].tolist())
        return df

    # ------------------------------------------------------------------
    # Persistência
    # ------------------------------------------------------------------

    def _salvar(self) -> None:
        with open(self.caminho_modelo, "wb") as f:
            pickle.dump(self.pipeline, f)

    def carregar(self) -> bool:
        """Carrega modelo salvo. Retorna True se bem-sucedido."""
        if os.path.exists(self.caminho_modelo):
            with open(self.caminho_modelo, "rb") as f:
                self.pipeline = pickle.load(f)
            self.treinado = True
            return True
        return False

    # ------------------------------------------------------------------
    # Fallback por regras
    # ------------------------------------------------------------------

    @staticmethod
    def _classificar_por_keywords(texto: str) -> str:
        texto_lower = texto.lower()
        scores = {cat: 0 for cat in CATEGORIAS}
        for cat, kws in _KEYWORDS.items():
            for kw in kws:
                if kw in texto_lower:
                    scores[cat] += 1
        return max(scores, key=scores.get)
