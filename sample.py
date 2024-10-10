import pandas as pd

import cpi

pd.DataFrame([o.__dict__() for o in cpi.areas.all()]).to_csv("./data/areas.csv", index=False)
pd.DataFrame([o.__dict__() for o in cpi.items.all()]).to_csv("./data/items.csv", index=False)
pd.DataFrame([o.__dict__() for o in cpi.periods.all()]).to_csv(
    "./data/periods.csv", index=False
)
pd.DataFrame([o.__dict__() for o in cpi.periodicities.all()]).to_csv(
    "./data/periodicities.csv", index=False
)
