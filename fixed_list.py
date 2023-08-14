from collections import UserList
from custom_exc import ReSizeError


class FixedLengthList(UserList):
    def __init__(self, length: int = 0, *a, **kw):
        self.length = int(length)
        super().__init__(*a, **kw)

    def __len__(self):
        return self.length

    def __mul__(self, other):
        raise ReSizeError

    def __rmul__(self, other):
        raise ReSizeError

    def __imul__(self, other):
        raise ReSizeError

    def __add__(self, other):
        raise ReSizeError

    def __radd__(self, other):
        raise ReSizeError

    def __iadd__(self, other):
        raise ReSizeError

    def append(self, other):
        raise ReSizeError

    def extend(self, other):
        raise ReSizeError

    def insert(self, index: int, other):
        raise ReSizeError

    def pop(self, pos: int = -1):
        raise ReSizeError

    def reverse(self):
        raise ReSizeError

    def remove(self, item):
        raise ReSizeError

    def sort(self, key):
        raise ReSizeError

    def __getitem__(self, i):
        return self.data[i]

