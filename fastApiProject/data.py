import pandas as pd
from fastapi import File

class Data:
    def __init__(self):
        self.df = None

    def open_csv(self, name: str):
        try:
            df = pd.read_csv(name)
            print(df.info())
        except FileNotFoundError:
            print("no such file")