# Loads the landscape materials
import os

import pandas as pd

def parse_materials(filename = 'landscape.csv'):
    path = os.path.join(os.getcwd(), 'data', filename)
    df = pd.read_csv(path)
    df['Embodied-CO2eq'] = pd.to_numeric(df['Embodied-CO2eq'], errors='coerce')
    return df
if __name__ == '__main__':
    df = parse_materials()
    print (df.head(5))
