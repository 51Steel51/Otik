from __future__ import annotations

import os
from math import log2
import hexdump as hd
from typing import List, Any


EXTENSTION = 'vl'
SIGNATURE = 'pivl'
ENCODING = 'utf-8'


if __name__ == '__main__':
    # ----------TASK 1---------

    _path = 'labs-files/files'
    files = [file for file in os.listdir(_path) if os.path.isfile(_path + '/' + file)]
    # print(os.listdir(_path))
    for file in files:
        with open(f'{_path}/{file}', 'rb') as file_bin, open(f'dumps/{file}.txt', 'w+') as w:
            w.write(f'____HEX DUMP OF {file.upper()}____\n\n')
            st = hd.hexdump(file_bin, result='return')
            w.write(st)

    pass


