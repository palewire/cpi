import pandas as pd

import cpi

pd.DataFrame([o.__dict__() for o in cpi.areas]).to_csv("./data/areas.csv", index=False)
pd.DataFrame([o.__dict__() for o in cpi.items]).to_csv("./data/items.csv", index=False)
pd.DataFrame([o.__dict__() for o in cpi.periods]).to_csv(
    "./data/periods.csv", index=False
)
pd.DataFrame([o.__dict__() for o in cpi.periodicities]).to_csv(
    "./data/periodicities.csv", index=False
)
