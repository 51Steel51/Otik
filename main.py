from math import log2
from typing import BinaryIO, MutableMapping

import hexdump as hd
import os
from os import path
import time
import Modules
import click
from Modules.FileHandle import FileHandler, create_supply_folders, list_all_files
from encode_terminal import cli
import glob
import json

EXTENSTION = 'vl'
SIGNATURE = 'pivl'
ENCODING = 'utf-8'

def convert_to_system(number: int, foundation: int, start_found: int = None):
    if start_found:
        str_num = str(number)[::-1]
        number = sum([int(str_num[i]) * pow(start_found, i) for i in range(len(str_num))])
    num = []
    d, m = divmod(number, foundation)
    num.append(m)
    if d >= foundation:
        num.extend(convert_to_system(d, foundation))
    else:
        num.append(d)
    return num

def count_elements(num_el: int, mes: str) -> dict:
    return {i: mes.count(str(i)) for i in range(num_el)}

def count_probability(freq: dict, mes: str) -> dict:
    mes_len = len(mes)
    return {i: v/mes_len for i, v in freq.items()}

def information_amount(prob: dict) -> dict:
    return {i: -log2(p) for i, p in prob.items()}

def su_inf_amount(amount: dict) -> int:
    return sum([i for i in amount.values()])

def sort_by_alphabet(d: dict, rev=False) -> dict:
    return {k: v for k, v in sorted(d.items(), key=lambda value: value[1], reverse=rev)}

if __name__ == '__main__':
    # ----------TASK 1---------

    # cli()

    #print(list_all_files('123.txt'))
    #create_supply_folders('f1/f2/f3/f4', False)

    #print(list_all_files('labs-files/files1'))

    # fHandler = FileHandler()
    # fHandler.loadConfig('header_config.json', 'DefaultHeader')
    # #fHandler.encodeFile(['TestFolder', 'chess16.png'], outputName='archive')
    # fHandler.decodeFile('archive.vl', 'utf-8')

    # _path = 'TestFolder/f1'
    # files = [file for file in os.listdir(_path) if os.path.isfile(_path + '/' + file)]
    # print(os.listdir(_path))
    # for file in files:
    #     with open(f'{_path}/{file}', 'rb') as file_bin, open(f'dumps/{file}1.txt', 'w+') as w:
    #         w.write(f'____HEX DUMP OF {file.upper()}____\n\n')
    #         st = hd.hexdump(file_bin, result='return')
    #         w.write(st)

    print(list(reversed(convert_to_system(1344, 2, 8))))
