import pandas as pd

def toTable(data, data2):
    df = pd.DataFrame(data)
    df.set_index("Time", inplace = True)
    df = df.resample('1s').median().interpolate()
    df2 = pd.DataFrame(data2)
    df2.set_index("Time", inplace = True)
    df2 = df2.resample('1s').median().interpolate()
    df["req"] = df2.reqCount.values
    df.to_csv('./analyser/faasData.csv', index=True)