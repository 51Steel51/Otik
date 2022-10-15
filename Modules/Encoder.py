from Modules.compressionAlg import Algorithm


class Encoder:
    alg: Algorithm

    def __init__(self, alg: Algorithm):
        self.alg = alg

    def compress(self, file_data) -> bytes:
        compressed = self.alg.encode(file_data)
        return compressed
