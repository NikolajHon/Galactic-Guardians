import pandas as pd
import numpy as np


class Data:
    def __init__(self, name: str):
        self.csv_name = name

    def open_csv(self):
        try:
            df = pd.read_csv(self.csv_name)
            print(df.info())
        except FileNotFoundError:
            print("no such file")