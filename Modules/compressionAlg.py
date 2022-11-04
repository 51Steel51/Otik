from filecmp import cmp
from typing import AnyStr, Dict, Tuple, Any
from bitarray import bitarray


class Algorithm:
    def __init__(self):
        pass

    def encode(self, src: bytes) -> Tuple[Dict[str, AnyStr], bytes]:
        pass

    def decode(self, src: bytes, codes: Dict[str, AnyStr]) -> bytes:
        pass


class NoCompressionAlg(Algorithm):

    def encode(self, src: bytes) -> Tuple[Dict[str, AnyStr], bytes]:
        return {}, src

    def decode(self, src: bytes, codes: Dict[str, AnyStr]) -> bytes:
        return src


class HuffmanAlg(Algorithm):
    class Root:

        def __init__(self):
            self.childs = []
            self._size = 0

        def size(self):
            return self._size

        def add_child(self, child):
            self.childs.append(child)
            if isinstance(child[1], int):
                self._size += child[1]
            else:
                self._size += child[1].size()

        def __repr__(self):
            return f"root[{self._size}] ({self.childs})"

        def __cmp__(self, other):
            return cmp(str(self._size), str(other))

        def __gt__(self, other):
            if self._size > other:
                return True
            else:
                return False

        def __ge__(self, other):
            if self._size >= other:
                return True
            else:
                return False

        def __lt__(self, other):
            if self._size < other:
                return True
            else:
                return False

        def __le__(self, other):
            if self._size <= other:
                return True
            else:
                return False

        def __eq__(self, other):
            if self._size == other:
                return True
            else:
                return False

        def codes_table(self, start: str):
            d = {}
            i = 0
            for child in self.childs:
                if isinstance(child[1], int):
                    d[child[0]] = start + str(i) if start else '0'
                else:

                    d = {**d, **(child[1].codes_table(start + str(i)))}
                i += 1
            return d

    sort_value = lambda self, items: items[1]

    def sort_dict_by(self, d: dict, criteria: Any, rev=False) -> dict:
        return {k: v for k, v in sorted(d.items(), key=criteria, reverse=rev)}

    def create_root_sort(self, d: dict, root: Root, num: int):

        root.add_child(d.popitem())
        root.add_child(d.popitem())

        d[f'S{num}'] = root

        d = self.sort_dict_by(d, self.sort_value, True)

        if len(d) == 1:
            return root

        new_root = self.Root()

        return self.create_root_sort(d, new_root, num + 1)

    def encode(self, src: bytes) -> Tuple[Dict[str, AnyStr], bytes]:
        src = src.decode()
        symbols = set(src)
        frequences = {s: src.count(s) for s in symbols}
        frequences = self.sort_dict_by(frequences, self.sort_value, True)

        root = self.Root()

        new_root = self.create_root_sort(frequences, root, 1)

        codes = new_root.codes_table('')

        result = ''
        for element in src:
            result += codes[element]

        bt = bitarray()
        bt.extend([int(i) for i in result])
        result = bitarray.tobytes(bt)

        return codes, result

    def decode(self, src: bytes, codes: Dict[str, AnyStr]) -> bytes:
        bt = bitarray()
        src = bytes(src)
        bt.frombytes(src)
        src = bt.tolist()
        src = [str(i) for i in src]
        src = ''.join(src)
        new_codes = {v: k for k, v in codes.items()}
        result = ''
        i = 1
        new_codes_keys = new_codes.keys()
        while src:
            if src[0:i] in new_codes_keys:
                result += new_codes[src[0:i]]
                src = src[i::]
                i = 1
            elif i > len(src):
                break
            else:
                i += 1

        result = result.encode()

        return result
