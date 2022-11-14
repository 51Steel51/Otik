from __future__ import annotations

import os.path
import sys
import json
from typing import Tuple, List, BinaryIO

import click
from math import log2, floor
from datetime import datetime, tzinfo, timedelta
from Modules.compressionAlg import Algorithm, NoCompressionAlg, HuffmanAlg
from Modules.Decoder import Decoder
from Modules.Encoder import Encoder
from Modules.FileHeader import FileHeader, DefaultHeader
from Modules.header_handle import DefaultHeaderHandler, HeaderHandler

CUSTOM_EXTENSION = '.vl'
DEFAULT_OUTPUT_NAME = 'Archive'


def list_all_files(path: str) -> List[Tuple[str, str]]:
    files = []
    path_start = ''
    if os.path.isdir(path):
        for r, d, f in os.walk(path):
            for file in f:
                files.append(os.path.join(r, file))
            for directory in d:
                if len(os.listdir(os.path.join(r, directory))) == 0:
                    files.append(os.path.join(r, directory))
        if path.count('/'):
            path_start = path.rsplit('/', 1)[0]
            path_start += '/'
    else:
        files.append(path)

    files = [(file, file.replace(path_start, '')) for file in files]
    return files


def create_supply_folders(path: str, is_folder: bool):
    path = path.split('/')
    res_path = ''
    if not is_folder:
        path = path[0:-1]
    for folder in path:
        res_path = os.path.join(res_path, folder)
        if not os.path.exists(res_path):
            os.mkdir(res_path)


def countSize(bits: str):
    size = len(bits)

    # find power of 2
    size = log2(size)
    if size % 1 > 0:
        size = floor(size + 1)
    return size


def str_to_bytes(data: str | tuple, bytes_count: int = None) -> (bytes, int):
    bits = ''.join(format(ord(x), 'b').zfill(8) for x in data)

    if bytes_count:
        return int(bits, 2).to_bytes(bytes_count, 'big'), bytes_count
    else:
        b_c = countSize(bits)
        return int(bits, 2).to_bytes(bytes_count, 'big'), b_c


class FileInfo:
    # source file info
    Name: str
    FullName: str
    Extension: str
    Path: str
    Len: int
    Size: int

    def __init__(self):
        pass

    def countNameSize(self):
        size = 0
        for ch in self.Name:
            size += sys.getsizeof(ch + '!') - sys.getsizeof('!')

        # find power of 2
        size = log2(size)
        if size % 1 > 0:
            size = floor(size + 1)
        return pow(2, size)


class FileHandler:
    # files info containers
    sourceFile: FileInfo
    processedFile: FileInfo

    # algorithm to be used
    alg: Algorithm

    # decoder and encoder
    decoder: Decoder
    encoder: Encoder

    # header handler

    headerHandler: HeaderHandler

    # file header config
    config: dict

    def __init__(self):
        pass

    def writeFile(self, file_content: bytes = None, output_file: BinaryIO = None, header: FileHeader = None,
                  encoding: str = '', ):
        if header:
            self.headerHandler.headerWrite(output_file=output_file, header=header, encoding=encoding)

        if file_content:
            # source file
            output_file.write(file_content)

        if header:
            # end flag
            output_file.write(bytearray.fromhex(self.config['flag']['value']))

    def decodeFile(self, file_path: str, encoding: str = ''):
        self.sourceFile.Path = file_path
        self.sourceFile.Name = file_path.split('/')[-1]
        self.sourceFile.Extension = self.sourceFile.Name.split('.')[-1]

        folderName = self.sourceFile.Name.split('.')[0]

        with open(file_path, 'rb') as file_to_encode:
            while True:
                # define header and read data
                header, source_data, codes = self.headerHandler.headerRead(file_to_encode, encoding)

                # decode data and write it to file / create folder
                if not header.fileType:

                    # select compression algorithm
                    if header.compressionMethod[0] == 0:
                        self.alg = NoCompressionAlg()
                    elif header.compressionMethod[0] == 1:
                        self.alg = HuffmanAlg()
                    else:
                        raise ValueError(f"Unknown compression algorithm: {header.compressionMethod[0]}")

                    # decode data
                    self.decoder = Decoder(self.alg)
                    decoded_file = self.decoder.decompress(source_data, codes)

                    path = os.path.join(folderName, header.fileName[0])
                    create_supply_folders(path, False)

                    self.sourceFile.Path = path

                    # write decoded data
                    decoded_file_path = self.sourceFile.Path
                    with open(decoded_file_path, 'wb') as file_to_write:
                        print(f"File {header.fileName[0]} was encoded with {header.compressionMethod[0]} algorithm")
                        self.writeFile(file_content=decoded_file, output_file=file_to_write)

                else:
                    path = os.path.join(folderName, header.fileName[0])
                    create_supply_folders(path, True)

                # check EOF
                if not file_to_encode.read(1):
                    break
                else:
                    file_to_encode.seek(-1, 1)

    def encodeFile(self, file_paths: list, compression_alg: tuple | int = None, noise_prot: int = None, outputName: str = None):
        if not outputName:
            outputName = DEFAULT_OUTPUT_NAME
        self.processedFile.Path = outputName + CUSTOM_EXTENSION
        if not os.path.exists(self.processedFile.Path):
            open(self.processedFile.Path, 'w').close()
        with open(self.processedFile.Path, 'ab') as compressed_file:
            if len(compression_alg) == 1:
                compression_alg = tuple([compression_alg[0] for _ in range(len(file_paths))])
            print(compression_alg)
            print(file_paths)
            alg_order = 0
            for path in file_paths:
                inner_paths = list_all_files(path)
                for (orig_path, file_path) in inner_paths:

                    # select compression algorithm
                    if compression_alg[alg_order] == 0:
                        self.alg = NoCompressionAlg()
                    elif compression_alg[alg_order] == 1:
                        self.alg = HuffmanAlg()
                    else:
                        raise ValueError(f"Unknown compression algorithm: {compression_alg[alg_order]}")

                    self.sourceFile.Path = file_path
                    self.sourceFile.Name = file_path
                    self.sourceFile.Len = len(self.sourceFile.Name)
                    self.sourceFile.Extension = file_path.split('/')[-1].split('.')[-1]
                    self.sourceFile.Size = os.path.getsize(orig_path)

                    is_dir = os.path.isdir(orig_path)
                    encoded_data = None
                    codes = None
                    compression_method = compression_alg[alg_order]
                    if not is_dir:
                        self.encoder = Encoder(self.alg)
                        data = None
                        with open(orig_path, 'rb') as f:
                            data = f.read()
                        codes, encoded_data = self.encoder.compress(data)

                        encoded_data_len = sys.getsizeof(encoded_data)
                        data_len = sys.getsizeof(data)

                        print("Source size:", data_len, "compressed size:", encoded_data_len, "file:", self.sourceFile.Name)
                        if encoded_data_len > data_len:
                            compression_method = 0
                            encoded_data = data
                            print(f"Uncompressed data ({data_len}) is smaller in size then compressed data ({encoded_data_len}) for file {self.sourceFile.Name}")

                    # set up header
                    header = self.headerHandler.headerSetUp(is_dir, self.sourceFile, encoded_data, codes, compression_method=compression_method)
                    if not is_dir:
                        print(self.sourceFile.Name, "compression algorithm", header.compressionMethod[0])

                    # write info about file or directory to archive
                    if not is_dir:
                        self.writeFile(file_content=encoded_data, output_file=compressed_file, header=header,
                                       encoding='utf-8')
                    else:
                        self.writeFile(header=header, output_file=compressed_file, encoding='utf-8')
                alg_order += 1

    def loadConfig(self, file_path: str, header_name: str):
        with open(file_path) as f:
            config = json.load(f)
            self.config = config[header_name]
        self.sourceFile = FileInfo()
        self.processedFile = FileInfo()
        self.headerHandler = DefaultHeaderHandler(self.config)
