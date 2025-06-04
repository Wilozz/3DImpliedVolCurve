import pandas as pd
from vol_surface import VolSurface

def main():
    df = pd.read_csv('options_data_filled.csv')
    print(df)
    vs = VolSurface(df)
    vs.compute_surface()
    vs.plot_surface()

if __name__ == "__main__":
    main()