from typing import Dict, AnyStr
from Modules.compressionAlg import Algorithm


class Decoder:
    alg: Algorithm

    def __init__(self, alg: Algorithm):
        self.alg = alg

    def decompress(self, file_data: bytes, codes: Dict[str, AnyStr]) -> bytes:
        decompressed = self.alg.decode(file_data, codes)
        return decompressed
