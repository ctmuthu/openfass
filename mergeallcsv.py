import os
import pandas as pd

path = '/Users/MCM/Desktop'
os.chdir(path)
dir_list= []

for p,n,f in os.walk(os.getcwd()):
    for a in f:
        a = str(a)
        if a.endswith('.csv'):
            dir_list.append(os.path.join(p,a))

print(dir_list)
combined_csv = pd.concat([pd.read_csv(f) for f in dir_list ])
#export to csv
combined_csv.to_csv( "combined_csv.csv", index=False, encoding='utf-8-sig')