# Predição de Zebras no Xadrez

## Objetivo

O objetivo deste projeto é **identificar e prever possíveis zebras em partidas de xadrez**, utilizando dados históricos de partidas dos principais jogadores do [Chess.com](https://www.chess.com/).

A ideia é analisar características das partidas e dos jogadores para estimar a probabilidade de um resultado considerado improvável, como a vitória de um jogador com menor rating contra um adversário mais forte.

## Coleta de dados

### API

Os dados das partidas foram coletados por meio da API do Chess.com.

Como o Chess.com possui uma grande base de jogadores e partidas, a plataforma foi escolhida como fonte de dados para o projeto.

Foram selecionados os **50 principais jogadores** das modalidades:

- Bullet
- Blitz
- Rápidas

Para cada jogador, foram coletadas **200 partidas**, totalizando uma base inicial de partidas para análise.

## Processamento dos dados

### Conversão e normalização

As partidas foram inicialmente coletadas no formato **JSON**. Para facilitar o armazenamento, processamento e análise dos dados, os arquivos foram convertidos para o formato **Parquet**.

Durante essa etapa, foi realizada a **normalização e organização dos dados da partida**, transformando informações que estavam agrupadas em diferentes estruturas do JSON em colunas individuais.

Foram extraídas e padronizadas informações relacionadas a quatro principais grupos:

### Informações da partida

- Evento
- Data
- Rodada
- Resultado
- Posição atual
- Código ECO e URL de abertura
- Rating dos jogadores
- Forma de término da partida
- Horário de início

### Precisão dos jogadores

Também foram extraídas as informações de precisão de cada jogador:

- Precisão das jogadas das brancas
- Precisão das jogadas das pretas

### Jogador de brancas

Foram normalizadas informações específicas do jogador que jogou com as peças brancas:

- Resultado
- Username
- UUID

### Jogador de pretas

Da mesma forma, foram normalizadas as informações do jogador que jogou com as peças pretas:

- Resultado
- Username
- UUID

Essa etapa permitiu transformar os dados originalmente estruturados em JSON em uma tabela mais adequada para consultas, análises exploratórias e posteriormente para a criação das features utilizadas no modelo.

## Banco de dados

Após a conversão e normalização dos dados, os arquivos Parquet foram utilizados para realizar a **ingestão em um banco de dados SQLite**.

O banco de dados será utilizado para organizar as partidas e disponibilizar os dados necessários para as próximas etapas do projeto.