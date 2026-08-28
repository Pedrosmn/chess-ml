# %%

import pandas as pd

# %%

df = pd.read_parquet('data/processed/rapid/1stSecond_2026-05-26_16-30-35.parquet')


# %%

df
# %%

print(df['white'].iloc[6])

"""criar colunas a partir do "pgn":
    Event
    Date
    Round
    White
    Black
    Result
    CurrentPosition
    ECO
    ECOUrl
    WhiteElo
    BlackElo
    Termination
    StartTime

A partir do "accuracies:
    WhiteAcc
    BlackAcc
    Remover accuracies

A partir do "white":
    WhiteResult
    WhiteUsername
    WhiteUuid

A partir do "black":
    BlackResult
    BlackUsername
    BlackUuid
    """


# %%
