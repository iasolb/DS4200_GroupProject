import pandas as pd


class Year:
    def __init__(self, fp: str):
        self.data = pd.read_csv(fp)

    def filter_parking() -> None:
        pass

    def filter_open() -> None:
        pass
