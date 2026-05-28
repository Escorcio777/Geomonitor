# GeoMonitor — Roteiro de Vídeo de Apresentação
## (Máx. 7 minutos)

---

### [00:00 – 00:30] ABERTURA / IDENTIDADE DO PROJETO

**[Tela: Logo GeoMonitor + slide de título]**

> "Bem-vindos à apresentação do **GeoMonitor** — um sistema de Monitoramento Geopolítico e Análise de Notícias Internacionais.
>
> Nosso grupo é formado por Arthur Murillo, Arthur Escorcio, Arthur Beraldo, Alberto Holanda e Gabriel Porto, da Turma B — Ciências Políticas.
>
> O projeto foi desenvolvido para a disciplina Novas Tecnologias, com o Professor Adam Smith Gontijo."

---

### [00:30 – 01:15] O PROBLEMA REAL

**[Tela: slide "O Problema Real"]**

> "O problema que motivou o GeoMonitor é simples: **o volume de notícias internacionais cresce exponencialmente** — e analisar manualmente eventos geopolíticos relevantes tornou-se inviável.
>
> Jornalistas, analistas de relações internacionais e estudantes precisam categorizar, comparar e visualizar rapidamente notícias sobre conflitos, economia global e diplomacia.
>
> Nossa solução: um sistema que **coleta, limpa, classifica automaticamente e visualiza** essas notícias em um dashboard interativo."

---

### [01:15 – 02:00] LEVANTAMENTO DE REQUISITOS E ESCOPO

**[Tela: slide de Requisitos]**

> "Levantamos cinco requisitos funcionais principais:
> - Coleta de notícias de fontes públicas confiáveis
> - Limpeza e normalização dos textos
> - Classificação automática em: Conflito, Economia e Diplomacia
> - Visualização com gráficos dinâmicos
> - Filtros por categoria, período e busca textual
>
> Nos não-funcionais, priorizamos **rastreabilidade** — toda notícia exibe sua fonte — e **privacidade** — apenas dados públicos são processados.
>
> O escopo desta versão usa um dataset CSV local com 24 notícias rotuladas, mas a arquitetura já está preparada para integração com a **NewsAPI** em tempo real."

---

### [02:00 – 02:45] ARQUITETURA DO SISTEMA

**[Tela: diagrama de arquitetura em camadas]**

> "A arquitetura segue um pipeline em camadas:
>
> Primeiro, o **Coletor** lê e valida o CSV.
> Em seguida, o **Processador** aplica limpeza NLP: remoção de acentos, stopwords e caracteres especiais.
> Depois, o **Classificador** usa Scikit-Learn para vetorizar os textos com TF-IDF e classificar com Regressão Logística.
> O resultado alimenta o **Visualizador**, que gera gráficos Matplotlib.
> Por fim, o **Flask** serve tudo em um dashboard web responsivo.
>
> Cada módulo é independente — o que facilita testes e futuras melhorias."

---

### [02:45 – 04:30] DEMONSTRAÇÃO DA APLICAÇÃO

**[Tela: gravação do browser com o dashboard rodando em localhost:5001]**

> "Vamos ver o sistema em funcionamento.
>
> **[mostrar dashboard]**
> Aqui está o dashboard principal. No topo, temos os KPIs: total de notícias e contagem por categoria.
>
> **[apontar para gráfico de barras]**
> O gráfico de barras mostra a distribuição: neste dataset temos 10 notícias de conflito, 8 de economia e 6 de diplomacia.
>
> **[rolar para gráfico de pizza]**
> O gráfico de pizza mostra a proporção percentual de cada categoria.
>
> **[rolar para série temporal]**
> A série temporal mostra como os eventos se distribuíram ao longo de fevereiro e março de 2024.
>
> **[usar os filtros]**
> Agora vou aplicar um filtro: seleciono apenas 'Conflito'... e o dashboard se atualiza mostrando apenas as 10 notícias de conflito, com todos os gráficos recalculados.
>
> **[mostrar tabela]**
> Na tabela, cada notícia tem o título, a categoria predita pelo modelo, a data e a fonte — garantindo rastreabilidade total.
>
> **[abrir /api/noticias no browser]**
> Também temos uma API REST: o endpoint `/api/noticias` devolve os dados em JSON, permitindo integração com outros sistemas.
>
> **[abrir /api/metricas]**
> E o endpoint `/api/metricas` expõe as métricas do modelo — acurácia de teste e cross-validation."

---

### [04:30 – 05:30] PRINCIPAIS PONTOS DO CÓDIGO

**[Tela: editor de código com os arquivos abertos]**

> "Vamos destacar os pontos principais do código.
>
> **[abrir classificador.py]**
> O coração do sistema é o Classificador. Usamos o **pipeline do Scikit-Learn** combinando TF-IDF com bigramas e Regressão Logística. Isso garante alta eficiência para classificação de texto sem precisar de GPU.
>
> **[mostrar trecho do TfidfVectorizer]**
> O TF-IDF com `sublinear_tf=True` e `ngram_range=(1,2)` captura tanto palavras isoladas quanto expressões como 'guerra civil' ou 'acordo bilateral'.
>
> **[abrir processador.py]**
> O Processador aplica limpeza sem depender de NLTK ou spaCy — usamos apenas Python puro com unicodedata e regex, o que reduz as dependências do projeto.
>
> **[abrir app.py, mostrar rota index]**
> A rota principal do Flask aplica os filtros dinamicamente sobre o DataFrame em memória, gerando os gráficos e a tabela filtrada a cada requisição.
>
> **[abrir visualizador.py]**
> E o Visualizador usa Matplotlib com backend Agg — sem janela gráfica — para gerar os gráficos como PNG em base64, que são embutidos diretamente no HTML."

---

### [05:30 – 06:15] TESTES E VALIDAÇÃO

**[Tela: terminal rodando pytest]**

> "Para garantir a qualidade do sistema implementamos **25 testes automatizados** com pytest.
>
> Temos testes unitários para cada módulo — verificando carregamento de dados, limpeza de texto, acurácia do modelo, e persistência do pickle.
>
> E testes de aceitação que simulam o pipeline completo — da coleta até as rotas Flask.
>
> **[mostrar resultado: 25 passed in 3.02s]**
> Resultado: 25/25 testes passando, em 3 segundos.
>
> A acurácia do modelo no conjunto de teste foi de **100%** neste dataset pequeno e bem rotulado — em produção com mais dados, esperamos valores entre 80–90%."

---

### [06:15 – 07:00] CONSIDERAÇÕES FINAIS E PRÓXIMOS PASSOS

**[Tela: slide de considerações]**

> "Como considerações éticas: o sistema usa apenas dados públicos, exibe sempre a fonte de cada notícia, e a classificação é factual — sem emitir julgamentos políticos.
>
> Como próximos passos:
> - Integração em tempo real com NewsAPI
> - Análise de sentimento por notícia
> - Exportação de relatórios em PDF
> - E deploy em nuvem para acesso público
>
> O GeoMonitor demonstra como Python e suas bibliotecas — especialmente **Scikit-Learn e Flask** — podem resolver problemas reais de análise de informação geopolítica de forma acessível e transparente.
>
> Agradecemos ao Professor Adam Smith Gontijo pela orientação. Obrigado!"

---

## Dicas de Gravação

- Resolução mínima: **1080p**
- Narração: **fone de ouvido** para evitar eco
- Abrir o browser em **modo anônimo** para tela limpa
- Usar **OBS Studio** (gratuito) para gravar tela + voz simultaneamente
- Duração total: **6m30s – 7m00s**
- Upload: YouTube não-listado → copiar link para o AVA
