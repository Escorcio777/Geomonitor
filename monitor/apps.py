from django.apps import AppConfig


class MonitorConfig(AppConfig):
    name = "monitor"
    _initialized = False

    def ready(self):
        if MonitorConfig._initialized:
            return
        MonitorConfig._initialized = True

        from geomonitor.coletor import ColetorNoticias
        from geomonitor.processador import Processador
        from geomonitor.classificador import Classificador
        from monitor import pipeline

        coletor = ColetorNoticias()
        processador = Processador()
        classificador = Classificador()

        df_bruto = coletor.carregar_csv()
        df_limpo = processador.processar(df_bruto)

        if not classificador.carregar():
            classificador.treinar(df_limpo)

        pipeline.df_final = classificador.prever_df(df_limpo)
        pipeline.classificador = classificador
