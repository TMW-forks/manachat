import os


class PlayerList:
    def __init__(self, fn):
        self._filename = fn
        self._last_modified = os.path.getmtime(fn)
        self._list = self._load_file(fn)

    def _load_file(self, fn):
        self._list = []
        with open(fn, 'r') as f:
            for l in f:
                self._list.append(l.strip())
        return self._list

    def check_player(self, pn):
        if pn in self._list:
            return True
        else:
            lm = os.path.getmtime(self._filename)
            if lm != self._last_modified:
                self._last_modified = lm
                self._load_file(self._filename)
                if pn in self._list:
                    return True

        return False
