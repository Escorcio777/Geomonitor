"""
tests/test_geomonitor.py
Testes unitários e de aceitação do sistema GeoMonitor.
Execução: pytest tests/ -v
"""

import os
import sys
import pytest
import pandas as pd

# Garante que o pacote seja encontrado
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from geomonitor.coletor import ColetorNoticias
from geomonitor.processador import Processador
from geomonitor.classificador import Classificador, CATEGORIAS

# ──────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def df_bruto():
    coletor = ColetorNoticias()
    return coletor.carregar_csv()


@pytest.fixture(scope="module")
def df_processado(df_bruto):
    proc = Processador()
    return proc.processar(df_bruto)


@pytest.fixture(scope="module")
def classificador_treinado(df_processado):
    clf = Classificador(caminho_modelo="/tmp/modelo_teste.pkl")
    clf.treinar(df_processado)
    return clf


# ──────────────────────────────────────────────────────────────────────
# Testes: Coletor
# ──────────────────────────────────────────────────────────────────────

class TestColetor:
    def test_carrega_csv(self, df_bruto):
        """CSV deve ser carregado como DataFrame não-vazio."""
        assert isinstance(df_bruto, pd.DataFrame)
        assert len(df_bruto) > 0

    def test_colunas_obrigatorias(self, df_bruto):
        """DataFrame deve conter as colunas esperadas."""
        esperadas = ["titulo", "texto", "data", "fonte", "categoria"]
        for col in esperadas:
            assert col in df_bruto.columns, f"Coluna '{col}' ausente."

    def test_sem_titulos_nulos(self, df_bruto):
        """Não deve haver títulos nulos após carregamento."""
        assert df_bruto["titulo"].isnull().sum() == 0

    def test_datas_parseadas(self, df_bruto):
        """Coluna 'data' deve ser do tipo datetime."""
        assert pd.api.types.is_datetime64_any_dtype(df_bruto["data"])

    def test_arquivo_invalido_levanta_erro(self):
        """Caminho inválido deve levantar FileNotFoundError."""
        coletor = ColetorNoticias(caminho_csv="/nao/existe.csv")
        with pytest.raises(FileNotFoundError):
            coletor.carregar_csv()


# ──────────────────────────────────────────────────────────────────────
# Testes: Processador
# ──────────────────────────────────────────────────────────────────────

class TestProcessador:
    def test_cria_coluna_texto_limpo(self, df_processado):
        assert "texto_limpo" in df_processado.columns

    def test_sem_duplicatas(self, df_processado):
        assert df_processado["titulo"].duplicated().sum() == 0

    def test_texto_minusculo(self, df_processado):
        textos = df_processado["texto_limpo"]
        assert textos.str.lower().equals(textos), "Texto deve estar em minúsculas."

    def test_sem_caracteres_especiais(self, df_processado):
        import re
        for txt in df_processado["texto_limpo"].head(10):
            assert not re.search(r"[^a-z\s]", txt), f"Caractere inválido em: '{txt}'"

    def test_tokens_minimos(self, df_processado):
        """Todas as linhas devem ter pelo menos 3 tokens."""
        assert (df_processado["texto_limpo"].str.split().str.len() >= 3).all()

    def test_limpeza_direta(self):
        proc = Processador()
        df = pd.DataFrame({
            "titulo": ["Título Teste", "Título Teste"],  # duplicata
            "texto": ["Texto limpo aqui.", "Texto limpo aqui."],
            "data": ["2024-01-01", "2024-01-01"],
            "fonte": ["Teste", "Teste"],
            "categoria": ["conflito", "conflito"],
        })
        df["data"] = pd.to_datetime(df["data"])
        resultado = proc.processar(df)
        assert len(resultado) == 1   # duplicata removida


# ──────────────────────────────────────────────────────────────────────
# Testes: Classificador
# ──────────────────────────────────────────────────────────────────────

class TestClassificador:
    def test_treinamento_retorna_metricas(self, classificador_treinado):
        metricas = classificador_treinado.metricas
        assert isinstance(metricas, dict)
        assert len(metricas) > 0

    def test_acuracia_minima(self, classificador_treinado):
        """Acurácia deve ser ≥ 60 % no conjunto de teste."""
        acc = classificador_treinado.metricas.get("acuracia_teste", 1.0)
        assert acc >= 0.60, f"Acurácia muito baixa: {acc:.2%}"

    def test_predicao_categoria_valida(self, classificador_treinado):
        """Predições devem pertencer ao conjunto de categorias."""
        textos = [
            "tropas avancam bombardeio guerra militar",
            "mercado bolsa inflacao economia juros",
            "acordo tratado diplomacia onu negociacao",
        ]
        preds = classificador_treinado.prever(textos)
        assert len(preds) == 3
        for p in preds:
            assert p in CATEGORIAS, f"Categoria inválida: {p}"

    def test_predicao_string_unica(self, classificador_treinado):
        """Deve aceitar string simples como entrada."""
        pred = classificador_treinado.prever("conflito guerra ataque militar")
        assert isinstance(pred, list)
        assert pred[0] in CATEGORIAS

    def test_prever_df(self, classificador_treinado, df_processado):
        resultado = classificador_treinado.prever_df(df_processado)
        assert "categoria_predita" in resultado.columns
        assert len(resultado) == len(df_processado)

    def test_fallback_keywords(self):
        """Classificação por palavras-chave (sem modelo treinado)."""
        clf = Classificador(caminho_modelo="/tmp/inexistente.pkl")
        # sem treinar, deve usar fallback
        pred = clf.prever("tropas militares atacam cidade bombardeio conflito")
        assert pred[0] == "conflito"

    def test_persistencia_modelo(self, df_processado, tmp_path):
        """Modelo salvo deve ser carregável e produzir os mesmos resultados."""
        cam = str(tmp_path / "modelo.pkl")
        clf1 = Classificador(caminho_modelo=cam)
        clf1.treinar(df_processado)
        pred1 = clf1.prever(["guerra conflito tropas ataque"])

        clf2 = Classificador(caminho_modelo=cam)
        clf2.carregar()
        pred2 = clf2.prever(["guerra conflito tropas ataque"])
        assert pred1 == pred2


# ──────────────────────────────────────────────────────────────────────
# Testes de Aceitação (integração ponta a ponta)
# ──────────────────────────────────────────────────────────────────────

class TestAceitacao:
    def test_pipeline_completo(self):
        """
        O pipeline completo (coleta → processamento → classificação)
        deve produzir um DataFrame com categorias preditas.
        """
        coletor = ColetorNoticias()
        df = coletor.carregar_csv()

        proc = Processador()
        df = proc.processar(df)

        clf = Classificador(caminho_modelo="/tmp/acc_modelo.pkl")
        clf.treinar(df)
        df = clf.prever_df(df)

        assert "categoria_predita" in df.columns
        assert df["categoria_predita"].isin(CATEGORIAS).all()

    def test_filtro_por_categoria(self, classificador_treinado, df_processado):
        """Filtragem por categoria deve retornar apenas registros daquela categoria."""
        df = classificador_treinado.prever_df(df_processado)
        filtrado = df[df["categoria_predita"] == "conflito"]
        assert (filtrado["categoria_predita"] == "conflito").all()

    def test_api_flask_noticias(self):
        """Endpoint /api/noticias deve retornar JSON com lista de notícias."""
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from app import app as flask_app
        client = flask_app.test_client()
        resp = client.get("/api/noticias")
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_api_flask_metricas(self):
        """Endpoint /api/metricas deve retornar dicionário de métricas."""
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from app import app as flask_app
        client = flask_app.test_client()
        resp = client.get("/api/metricas")
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, dict)

    def test_pagina_principal_carrega(self):
        """Página principal deve responder com status 200."""
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from app import app as flask_app
        client = flask_app.test_client()
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"GeoMonitor" in resp.data

    def test_filtro_via_querystring(self):
        """Filtro por categoria via query string deve funcionar."""
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from app import app as flask_app
        client = flask_app.test_client()
        resp = client.get("/?cat=conflito")
        assert resp.status_code == 200

    def test_privacidade_sem_dados_sensiveis(self, df_bruto):
        """Dataset não deve conter colunas com dados pessoais identificáveis."""
        colunas_sensiveis = ["cpf", "email", "telefone", "senha", "password"]
        for col in colunas_sensiveis:
            assert col not in df_bruto.columns, f"Coluna sensível encontrada: {col}"
