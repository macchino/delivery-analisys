# -*- coding: utf-8 -*-

import sys
import pandas as pd
from datetime import datetime

args = sys.argv

MASTER_FILE_PATH = './data/shop_master.csv'
GOOGLEMAP_FILE_PATH = './data/googlemap.csv'

DIR_PATH = "./rawdata/shops/"


def get_file_name(file_name_base):
    return "{}_{}.csv".format(datetime.now().strftime('%y%m%d'),
                              file_name_base)


FILE_NAME_BASE_LIST = [
    "musashinakahara", "musashikosugi", "musashishinjo", "musashimizonokuchi",
    "miyazakidai"
]

FILE_PATH_LIST = [
    DIR_PATH + get_file_name(file_name_base)
    for file_name_base in FILE_NAME_BASE_LIST
]

master = pd.read_csv(MASTER_FILE_PATH, index_col='id')

for file_path in FILE_PATH_LIST:
    df = pd.read_csv(file_path, index_col="id")
    master = pd.concat([master, df], sort=False).drop_duplicates(subset="url",
                                                                 keep="last")

# master
master.to_csv(MASTER_FILE_PATH, index=True, mode="w")

# googlemap
googlemap = pd.DataFrame()
googlemap["店名"] = master["name"]
googlemap["住所"] = master["address"]
googlemap["緯度"] = master["latitude"]
googlemap["経度"] = master["longitude"]
# googlemap["開始"] = data["open_hour"]
# googlemap["終了"] = data["close_hour"]
googlemap["点数"] = master["point"]
googlemap["レビュー数"] = master["reviews"]
googlemap["URL"] = master["url"]

googlemap.to_csv(GOOGLEMAP_FILE_PATH, index=False, mode="w")
