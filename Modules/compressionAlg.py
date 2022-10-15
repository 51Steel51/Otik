class Algorithm:
    def __init__(self):
        pass

    def encode(self, src: bytes) -> bytes:
        pass

    def decode(self, src: bytes) -> bytes:
        pass

class NoCompressionAlg(Algorithm):

    def encode(self, src: bytes) -> bytes:
        return src

    def decode(self, src: bytes) -> bytes:
        return src
