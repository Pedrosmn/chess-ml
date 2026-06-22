## Chess ML

Projeto de análise de partidas online de xadrez, com foco em comparar partidas
bullet, blitz e rapid de jogadores de alto rating.

### Objetivo

A hipótese central é que partidas mais rápidas são menos previsíveis do que
partidas rapid, e que a diferença de rating entre os jogadores pode ter menor
poder explicativo conforme o tempo de jogo diminui.

### Estrutura

- `notebooks/01_coleta.ipynb`: coleta jogadores dos leaderboards e baixa as
  partidas pela API pública do Chess.com.
- `notebooks/02_processamento.ipynb`: filtra e transforma os arquivos brutos em
  arquivos Parquet.
- `notebooks/03_eda.ipynb`: análise exploratória das partidas processadas.
- `src/collector.py`: funções auxiliares para coleta e salvamento dos dados.
- `docs/hipoteses.md`: registro da hipótese principal do projeto.

### Dados

Os dados brutos ficam em `data/raw`, separados por modalidade. Os dados
processados ficam em `data/processed`, também separados por modalidade, com um
arquivo consolidado para cada tipo de tempo.