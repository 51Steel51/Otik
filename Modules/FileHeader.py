import sys


class FileHeader:
    signature: (str, int)
    version: (str, int)
    compressionMethod: (int, int)
    fileLength: (int, int)
    noiseProtection: (int, int)
    extra: (int, int)

    def __init__(self):
        pass


class DefaultHeader(FileHeader):
    fileType: (int, int)    # 0 - file, 1 - dir
    fileName: (str, int)
    modificationTime: (int, int, int, int)
    modificationDate: (int, int, int, int)
    compressedSize: (int, int)
    uncompressedSize: (int, int)

    def __init__(self, sign=None, ver=None, comp=None, n_p=None, extr=None):
        self.signature = sign
        self.version = ver
        self.compressionMethod = comp
        self.noiseProtection = n_p
        self.extra = extr

    def __iter__(self):
        for attr, value in self.__dict__.iteritems():
            yield attr, value

    def countHeaderSize(self):
        size = 0
        for val in self.__dict__.values():
            size += val[-1]
        return size
