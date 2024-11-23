import pandas as pd
import numpy as np

try:
    df = pd.read_csv('datasets/Cleaned_Students_Performance.csv')

    print(df.info())
    #print(df.describe())
except FileNotFoundError:
    print("no such file")

#print( df )

