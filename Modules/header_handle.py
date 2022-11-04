from typing import Tuple, BinaryIO, AnyStr, Dict
from typing.io import IO
from math import floor, log2
from datetime import datetime, tzinfo, timedelta
import sys

from Modules.Encoder import Encoder
from Modules.FileHeader import FileHeader, DefaultHeader


def is_flag(file_position, flag: bytearray) -> bool:
    shift = len(flag)
    ch = file_position.read(shift)
    if ch == flag:
        return True
    else:
        file_position.seek(-shift, 1)
        return False


def find_near_2_bytes(bytes_count: int):
    # find power of 2
    if not bytes_count:
        return 0
    size = log2(bytes_count)
    if size % 1 > 0:
        size = floor(size + 1)
    return int(pow(2, size))

def find_zeros_at_start(message: str) -> int:
    count = 0
    for ch in message:
        if ch != '0':
            return count
        count += 1
    return count


class MSK(tzinfo):
    def utcoffset(self, dt):
        ...
        return timedelta(hours=3)

    def dst(self, dt):
        ...
        return timedelta(0)

    def tzname(self, dt):
        ...
        return "+03:00"

    def __repr__(self):
        ...
        return f"{self.__class__.__name__}()"


class HeaderHandler:
    config: dict

    def __init__(self, conf: dict):
        self.config = conf

    def headerRead(self, f: BinaryIO, encoding: str) -> Tuple[DefaultHeader, bytearray, Dict[str, AnyStr]]:
        pass

    def headerWrite(self, output_file: BinaryIO, header: FileHeader, encoding: str, ) -> None:
        pass

    def headerSetUp(self, is_dir: bool, sourceFile, encoded_data: bytes, codes: Dict[str, AnyStr] = None, compression_method: int = 0) -> FileHeader:
        pass


class DefaultHeaderHandler(HeaderHandler):
    def __init__(self, conf):
        super().__init__(conf)

    def headerRead(self, f: BinaryIO, encoding: str) -> Tuple[DefaultHeader, bytearray, Dict[str, AnyStr]]:
        header = DefaultHeader()

        # signature
        header.signature = f.read(self.config['signature']['byte']).decode(encoding=encoding), \
                           self.config['signature']['byte']

        # check signature
        assert header.signature[0] == self.config['signature'][
            'value'], "File signature doesn't match '.vl' Header signature"

        # version
        header.version = '.'.join(
            str(int.from_bytes(f.read(1), 'big')) for _ in range(self.config['version']['byte'])), \
                         self.config['version']['byte']

        # type
        header.fileType = int.from_bytes(f.read(self.config['type']['byte']), 'big')

        # compression method
        header.compressionMethod = int.from_bytes(f.read(self.config['compressionMethod']['byte']), 'big'), \
                                   self.config['compressionMethod']['byte']

        # noise protection
        header.noiseProtection = int.from_bytes(f.read(self.config['noiseProtection']['byte']), 'big'), \
                                 self.config['noiseProtection']['byte']

        # modification time
        bits = format(int.from_bytes(f.read(self.config['modificationTime']['byte']), 'big'), 'b')
        hours = int(bits[0:5], 2)
        minutes = int(bits[5:11], 2)
        seconds = 0 # int(bits[11:16], 2)

        header.modificationTime = (hours, minutes, seconds, self.config['modificationTime']['byte'])

        # modification date
        bits = format(int.from_bytes(f.read(self.config['modificationDate']['byte']), 'big'), 'b')
        month = int(bits[0:4], 2)
        day = int(bits[4:9], 2)
        year = int(bits[9:16], 2)
        header.modificationTime = (month, day, 2000 + year, self.config['modificationDate']['byte'])

        # compressed size
        header.compressedSize = int.from_bytes(f.read(self.config['compressedSize']['byte']), 'big'), \
                                self.config['compressedSize']['byte']

        # uncompressed size
        header.uncompressedSize = int.from_bytes(f.read(self.config['uncompressedSize']['byte']), 'big'), \
                                  self.config['uncompressedSize']['byte']

        # file length
        header.fileLength = int.from_bytes(f.read(self.config['fileLength']['byte']), 'big'), \
                            self.config['fileLength']['byte']

        # file name
        bytes_count = find_near_2_bytes(header.fileLength[0])
        header.fileName = f.read(bytes_count)[0:header.fileLength[0]].decode(encoding=encoding), bytes_count

        # compression character
        header.compressionCharacter = int.from_bytes(f.read(self.config['compressionCharacter']['byte']), 'big'), \
                                      self.config['compressionCharacter']['byte']

        # compression code
        header.compressionCode = int.from_bytes(f.read(self.config['compressionCode']['byte']), 'big'), \
                                 self.config['compressionCode']['byte']

        # code count - count of all characters codes
        header.codesCount = int.from_bytes(f.read(self.config['codesCount']['byte']), 'big'), \
                            self.config['codesCount']['byte']

        # zero added to every code to byte
        header.zeroAdd = (0, self.config['zeroAdd']['byte'])

        # all characters with codes
        # header.codes - (dict[character, code], byte)
        codes = {}
        characterSize = header.compressionCharacter[0]
        codeSize = header.compressionCode[0]
        allCodesSize = int((characterSize + codeSize) * header.codesCount[0])
        for _ in range(header.codesCount[0]):
            character = f.read(characterSize).decode(encoding=encoding).rstrip('\x00')
            zero_added = int.from_bytes(f.read(header.zeroAdd[1]), 'big')
            code = int.from_bytes(f.read(codeSize), 'big')
            code = "{0:b}".format(code)
            code = '0' * zero_added + code
            codes[character] = code
        header.codes = codes, allCodesSize

        # extra space
        header.extra = f.read(self.config['extra']['byte'])

        # source data and flag
        source_data = bytearray()
        if not header.fileType:
            flag = bytearray.fromhex(self.config['flag']['value'])
            while not is_flag(f, flag):
                source_data.extend(f.read(1))
        else:
            flag = f.read(self.config['flag']['byte'])

        return header, source_data, codes

    def headerSetUp(self, is_dir: bool, sourceFile, encoded_data: bytes,
                    codes: Dict[str, AnyStr] = None, compression_method: int = 0, ) -> DefaultHeader:

        # signature, version, compressionMethod
        header = DefaultHeader((self.config['signature']['value'], self.config['signature']['byte']),
                               (self.config['version']['value'], self.config['version']['byte']),
                               (compression_method, self.config['compressionMethod']['byte']),
                               (
                                   self.config['noiseProtection']['value'],
                                   self.config['noiseProtection']['byte']),
                               (self.config['extra']['value'], self.config['extra']['byte'])
                               )

        # is dir
        header.fileType = int(is_dir), self.config['type']['byte']

        # modification time and date
        modification_d_t = datetime.now(tz=MSK())
        header.modificationTime = (modification_d_t.hour, modification_d_t.minute, modification_d_t.second,
                                   self.config['modificationTime']['byte'])
        header.modificationDate = (modification_d_t.month, modification_d_t.day, modification_d_t.year % 1000,
                                   self.config['modificationDate']['byte'])

        # file length
        header.fileLength = (sourceFile.Len, self.config['fileLength']['byte'])

        # file name
        header.fileName = (sourceFile.Name, sourceFile.countNameSize())

        # uncompressed size
        header.uncompressedSize = (sourceFile.Size, self.config['uncompressedSize']['byte'])

        # compressed size
        compSize = self.config['compressedSize']['byte']
        header.compressedSize = (
            int(header.countHeaderSize() + sys.getsizeof(encoded_data) + compSize), compSize)

        # compression character - size of an symbol
        charSize = find_near_2_bytes(Encoder.find_near_byte(codes, True))
        header.compressionCharacter = (charSize, self.config['compressionCharacter']['byte'])

        # compression code - size of one code of a character
        codeSize = find_near_2_bytes(Encoder.find_near_byte(codes, False))
        header.compressionCode = (codeSize, self.config['compressionCode']['byte'])

        # code count - count of all characters codes
        codesCount = len(codes)
        header.codesCount = (codesCount, self.config['codesCount']['byte'])

        # zero add - zeros to be subtracted from every code
        header.zeroAdd = (0, self.config['zeroAdd']['byte'])

        # all characters with codes
        header.codes = (codes, self.config['codes']['byte'])

        return header

    def headerWrite(self, output_file: BinaryIO, header: DefaultHeader, encoding: str, ) -> None:
        # signature
        ba = bytearray(header.signature[0], encoding)
        ba.extend(bytearray(header.signature[1] - len(ba)))
        output_file.write(ba)

        # version
        version = [int(i) for i in header.version[0].split('.')]
        ba = bytearray(version)
        ba.extend(bytearray(header.version[1] - len(ba)))
        output_file.write(ba)

        # type of file - file or dir
        output_file.write((header.fileType[0]).to_bytes(header.fileType[1],
                                                        byteorder='big'))

        # compression method
        output_file.write(header.compressionMethod[0].to_bytes(header.compressionMethod[1]
                                                               , byteorder='big'))

        # noise protection
        output_file.write(header.noiseProtection[0].to_bytes(header.noiseProtection[1]
                                                             , byteorder='big'))

        # modification time
        get_bits = lambda data: ''.join(format(x, 'b').zfill(n) for x, n in data)
        modTime = get_bits(((header.modificationTime[0], 5),
                            (header.modificationTime[1], 6),
                            (header.modificationTime[2] // 2, 5)))
        modTime = int(modTime, 2).to_bytes(header.modificationTime[3], byteorder='big')
        output_file.write(modTime)

        # modification date
        modDate = get_bits(((header.modificationDate[0], 4),
                            (header.modificationDate[1], 5),
                            (header.modificationDate[2], 7)))
        modDate = int(modDate, 2).to_bytes(header.modificationDate[3], byteorder='big')
        output_file.write(modDate)

        # compressed size
        output_file.write(header.compressedSize[0].to_bytes(header.compressedSize[1]
                                                            , byteorder='big'))

        # uncompressed size
        output_file.write(header.uncompressedSize[0].to_bytes(header.uncompressedSize[1]
                                                              , byteorder='big'))

        # file length
        output_file.write(header.fileLength[0].to_bytes(header.fileLength[1]
                                                        , byteorder='big'))

        # file name
        ba = bytearray(header.fileName[0], encoding)
        ba.extend(bytearray(int(header.fileName[1]) - len(ba)))
        output_file.write(ba)

        # compression character
        output_file.write(header.compressionCharacter[0].to_bytes(header.compressionCharacter[1]
                                                                  , byteorder='big'))

        # compression code
        output_file.write(header.compressionCode[0].to_bytes(header.compressionCode[1]
                                                             , byteorder='big'))

        # code count - count of all characters codes
        output_file.write(header.codesCount[0].to_bytes(header.codesCount[1]
                                                        , byteorder='big'))

        # all characters with codes
        # header.codes - (dict[character, code], byte)
        for character, code in header.codes[0].items():
            ch = bytearray(character, encoding)
            ch.extend(bytearray(header.compressionCharacter[0] - len(ch)))
            output_file.write(ch)

            count_of_zeros = find_zeros_at_start(code)
            code = code[count_of_zeros::] if count_of_zeros < len(code) else '0'
            if code == '0':
                count_of_zeros -= 1
            output_file.write(count_of_zeros.to_bytes(header.zeroAdd[1], byteorder='big'))

            code = int(code, 2)
            output_file.write(code.to_bytes(header.compressionCode[0], byteorder='big'))

        # extra space
        output_file.write(bytearray(header.extra[1]))
