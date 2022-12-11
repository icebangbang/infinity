class rolling_window(object):
    def __init__(self, array,window_size):
        self.array = array
        self._hasnext = None
        self.start = 0
        self.end = window_size
    def __next__(self):
        result = self.array[self.start:self.end]
        self.start = self.start+1
        self.end = self.end+1
        return result

    def hasnext(self):
        if self.end > len(self.array):
                self._hasnext = False
                return False
        self._hasnext = True
        return self._hasnext


class hn_wrapper(object):
    def __init__(self, it):
        self.it = iter(it)
        self._hasnext = None

    def __iter__(self):
        return self

    def __next__(self):
        if self._hasnext:
            result = self._thenext
        else:
            result = next(self.it)
        self._hasnext = None
        return result

    def hasnext(self):
        if self._hasnext is None:
            try:
                self._thenext = next(self.it)
            except StopIteration:
                self._hasnext = False
            else:
                self._hasnext = True
        return self._hasnext

if __name__ == "__main__":
    x = rolling_window('ciao',2)
    while x.hasnext():
        print(next(x))
