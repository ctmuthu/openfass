import pandas as pd

def toTable(data):
    df = pd.DataFrame(data)
    df.to_csv('./analyser/faasData.csv', index=False)