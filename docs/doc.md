# Coleta de dados

## 1. Definição da amostra inicial

Para o EDA, vou trabalhar com partidas dos melhores jogadores nas três modalidades principais de tempo rápido online: bullet, blitz e rapid.

A escolha pelos top 50 ajuda a controlar parcialmente o nível dos jogadores, já que a análise central do projeto envolve previsibilidade do resultado e diferença de rating. Mesmo assim, essa decisão também cria um recorte específico: os resultados representam jogadores de elite, não a população geral do Chess.com.

## 2. Escolha do endpoint de coleta

A API pública do Chess.com oferece algumas formas de acessar partidas:

- `player/{username}/games/archives`: lista os meses disponíveis no histórico do jogador.
- `player/{username}/games/{YYYY}/{MM}`: retorna todas as partidas de um jogador em um mês específico.
- `player/{username}/games/live/{time_control}`: permite buscar partidas por controle de tempo específico.

Para este projeto, a abordagem escolhida foi consultar os arquivos mensais e filtrar as partidas pelo campo `time_class`. Isso permite coletar bullet, blitz e rapid de forma consistente, sem depender de um único controle de tempo como `60`, `180` ou `600`.

---

O campo `time_class` permite separar as partidas em categorias como `daily`, `rapid`, `blitz` e `bullet`.

Essa classificação é mais útil para a hipótese do projeto do que o controle de tempo exato, porque a comparação principal é entre modalidades. O controle de tempo específico ainda será analisado depois no EDA.

## 3. Coleta de partidas por jogador e modalidade

A meta desta etapa é coletar até 200 partidas para cada jogador presente no top 50 de bullet, blitz e rapid.

Esse número cria uma amostra inicial com alvo teórico de 10.000 partidas por modalidade.