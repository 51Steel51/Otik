from typing import Tuple, Dict, AnyStr

from Modules.compressionAlg import Algorithm


class Encoder:
    alg: Algorithm

    def __init__(self, alg: Algorithm):
        self.alg = alg

    def compress(self, file_data) -> Tuple[Dict[str, AnyStr], bytes]:
        codes, compressed = self.alg.encode(file_data)
        return codes, compressed

    @staticmethod
    def find_near_byte(codes: dict, keys_or_values: bool, encoding: str = 'utf-8'):
        if not codes:
            return 0
        if keys_or_values:
            # max_len - bytes
            max_len = max([len(bytearray(i, encoding)) for i in codes.keys()])
            return max_len
        else:
            # max_len - bits
            max_len = max([len(i) for i in codes.values()])

            return (max_len + 7) // 8
