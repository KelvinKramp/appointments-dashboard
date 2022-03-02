import json
from dateutil import parser
from definitions import ROOT_DIR
import os
import numpy as np


def perf_var_calc():
    loggingsfile = os.path.join(ROOT_DIR, 'config', 'loggings.json')
    with open(loggingsfile) as f:
        data = json.load(f)
    diff_list = []
    for i, j in enumerate(data):
        if i > 0:
            diff = parser.parse(data[i]['start time']) - parser.parse(data[i-1]['start time'])
            diff_seconds = diff.total_seconds()
            diff_list.append(diff_seconds)
    if not len(diff_list):
        avg_seconds = np.nan
    else:
        avg_seconds = (sum(diff_list)/len(diff_list))

    avg = round((avg_seconds / 60), 2)

    return avg
