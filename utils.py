import csv
import json
import uuid
import pandas as pd
from scipy.stats import spearmanr

def get_runs():
    """Gets the number of times the iterations have been run
    based on the number of results stored

    Returns:
        int: number of runs in this session
    """
    try:
        file = open('session/info.txt', 'r')
    except FileNotFoundError:
        return 0
    else:
        run = file.readlines()
        return len(run)

def save_info():
    path = 'session/info.txt'
    runs = get_runs()
    if runs == 0:
        with open(path, 'w') as file:
            file.write('1' + '\n')
    else: 
        with open(path, 'a') as file:
            file.write(str(runs + 1) + '\n')

def get_bom():
    with open('session/bom.json') as file:
        bom = json.load(file)
    return bom

def add_uuid(bom):
    for elem in bom:
        elem['id'] = str(uuid.uuid4())
    return bom

def match_id_name(list_uuid):
    bom = get_bom()
    names = []
    for uid in list_uuid:
        for elem in bom:
            if elem['id'] == uid:
                names.append(elem['Attribute'] + '-' + uid[:4])
                break
    return names

def get_project_area():
    bom = get_bom()
    total = 0
    for element in bom:
        total += float(element['unit'])
    return total

def spearman_corr(dataframe)->pd.DataFrame:
    """
    Calculates the spearman correlation between each one of the elements and the total impact

    Args:
        dataframe (pd.Dataframe): Dataframe

    Returns:
        pd.DataFrame: Returns a dataframe with the correlation index and p-value as columns
    """
    total = dataframe.sum(axis=1)
    corr = []
    for i in range(len(dataframe.columns)):
        s = spearmanr(dataframe.iloc[:,i],total)
        # print(s.correlation)
        corr.append(s)
    df2 = pd.DataFrame(corr)
    df2['Elements'] = dataframe.columns
    df2.index = df2['Elements']
    df2.pop('Elements')
    return df2
