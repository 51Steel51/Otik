from __future__ import annotations

import os
from math import log2
import hexdump as hd
from typing import List, Any

from os import path
import time
import Modules
import click
from Modules.FileHandle import FileHandler, create_supply_folders, list_all_files
from encode_terminal import cli
import glob
import json
from charset_normalizer import detect
from pyclbr import Function


EXTENSTION = 'vl'
SIGNATURE = 'pivl'
ENCODING = 'utf-8'

def file_len_in_alph(alphabet: List[int], mes: bytes | str) -> int:
    if type(mes) == bytes:
        return len([value for value in mes if int(value) in alphabet])
    return len([value for value in mes if ord(value) in alphabet])


def count_elements(alphabet: List[int], mes: bytes | str) -> dict:
    if type(mes) == bytes:
        return {i: mes.count(i.to_bytes(1, byteorder='big')) for i in alphabet}
    return {i: mes.count(chr(i)) for i in alphabet}


def count_probability(freq: dict, mes: bytes | str) -> dict:
    mes_len = len(mes)
    return {i: v / mes_len for i, v in freq.items()}


def information_amount(prob: dict) -> dict:
    return {i: (-log2(p) if p != 0 else 0) for i, p in prob.items()}


def sum_inf_amount(amount: dict) -> int:
    return sum([i for i in amount.values()])


def sort_dict_by(d: dict, criteria: Any, rev=False, hide_zeros=False) -> dict:
    if hide_zeros:
        return {k: v for k, v in sorted(d.items(), key=criteria, reverse=rev) if v != 0}
    return {k: v for k, v in sorted(d.items(), key=criteria, reverse=rev)}


if __name__ == '__main__':
    # ----------TASK 1---------

    # _path = 'labs-files/files'
    # files = [file for file in os.listdir(_path) if os.path.isfile(_path + '/' + file)]
    # # print(os.listdir(_path))
    # for file in files:
    #     with open(f'{_path}/{file}', 'rb') as file_bin, open(f'dumps/{file}.txt', 'w+') as w:
    #         w.write(f'____HEX DUMP OF {file.upper()}____\n\n')
    #         st = hd.hexdump(file_bin, result='return')
    #         w.write(st)
    #
    # pass


    alphabet = [i for i in range(256)]
    with open('123.txt', 'rb') as f:
        mes = f.read()
        print(mes)
        print(file_len_in_alph(alphabet=alphabet, mes=mes))
        freq = count_elements(alphabet=alphabet, mes=mes)
        prob = count_probability(freq=freq, mes=mes)
        inf_amout = information_amount(prob=prob)
        print(sum_inf_amount(amount=inf_amout))
        sort_item = lambda items: items[0]
        sort_value = lambda items: items[1]

        # ai frequency of occurrences
        print(sort_dict_by(d=freq, criteria=sort_item, rev=False, hide_zeros=True))
        print(sort_dict_by(d=freq, criteria=sort_value, rev=True, hide_zeros=True))

        # ai probability frequency of occurrences
        print(sort_dict_by(d=prob, criteria=sort_item, rev=False, hide_zeros=True))
        print(sort_dict_by(d=prob, criteria=sort_value, rev=True, hide_zeros=True))

        # information amount by ai
        print(sort_dict_by(d=inf_amout, criteria=sort_item, rev=False, hide_zeros=True))
        print(sort_dict_by(d=inf_amout, criteria=sort_value, rev=True, hide_zeros=True))

    exceptions = [i for i in range(33)]
    alphabet = [i for i in range(34, 1_114_111)]

    with open('123.txt', 'r') as f:
        mes = f.read()
        print(file_len_in_alph(alphabet=alphabet, mes=mes))
        freq = count_elements(alphabet=alphabet, mes=mes)
        prob = count_probability(freq=freq, mes=mes)
        inf_amout = information_amount(prob=prob)
        print(sum_inf_amount(amount=inf_amout))
        sort_item = lambda items: items[0]
        sort_value = lambda items: items[1]

        # ai frequency of occurrences
        print(sort_dict_by(d=freq, criteria=sort_item, rev=False, hide_zeros=True))
        print(sort_dict_by(d=freq, criteria=sort_value, rev=True, hide_zeros=True))

        # ai probability frequency of occurrences
        print(sort_dict_by(d=prob, criteria=sort_item, rev=False, hide_zeros=True))
        print(sort_dict_by(d=prob, criteria=sort_value, rev=True, hide_zeros=True))

        # information amount by ai
        print(sort_dict_by(d=inf_amout, criteria=sort_item, rev=False, hide_zeros=True))
        print(sort_dict_by(d=inf_amout, criteria=sort_value, rev=True, hide_zeros=True))

    alphabet = [i for i in range(256)]
    _path = 'labs-files/files/plaintext'
    files = [os.path.join(_path, file) for file in os.listdir(_path) if os.path.isfile(os.path.join(_path, file))]
    print(files)
    all_freq = {i: 0 for i in alphabet}
    sort_item = lambda items: items[0]
    sort_value = lambda items: items[1]
    for file in files:
        with open(file, 'rb') as f:
            print(file)
            mes = f.read()
            freq = count_elements(alphabet=alphabet, mes=mes)

            # ai frequency of occurrences
            freq_sorted = sort_dict_by(d=freq, criteria=sort_value, rev=True, hide_zeros=True)
            print("Frequencies:")
            print(freq_sorted)

            for key in freq_sorted.keys():
                all_freq[key] += freq_sorted[key]
        print()

    LIMIT = 4

    all_freq_sorted = sort_dict_by(d=all_freq, criteria=sort_value, rev=True, hide_zeros=True)

    print(dict(list(all_freq_sorted.items())[:LIMIT]))

    alphabet = [i for i in range(256)]
    var = 2
    file = 'labs-files/variants/L2/' + str(var % 9) + '.txt'
    all_freq = {i: 0 for i in alphabet}
    sort_item = lambda items: items[0]
    sort_value = lambda items: items[1]
    with open(file, 'rb') as f:
        print(file)

        mes = f.read()
        freq = count_elements(alphabet=alphabet, mes=mes)

        # ai frequency of occurrences
        freq_sorted = sort_dict_by(d=freq, criteria=sort_value, rev=True, hide_zeros=True)

        LIMIT = 4

        print(dict(list(freq_sorted.items())[:LIMIT]))

        result = detect(mes)

        if result['encoding'] is not None:
            print('got', result['encoding'], 'as detected encoding')
        else:
            print('Bad encoding')



