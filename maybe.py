class Maybe:

    def __init__(self, value):
        self.value = value

    def __add__(self, other):
        if self.value == None or other.value == None:
            return Maybe(None)
        return Maybe(self.value + other.value)

    def __mul__(self, other):
        if self.value == None or other.value == None:
            return Maybe(None)
        return Maybe(self.value * other.value)

    def __sub__(self, other):
        if self.value == None or other.value == None:
            return Maybe(None)
        return Maybe(self.value - other.value)

    def __floordiv__(self, other):
        if self.value == None or other.value == None:
            return Maybe(None)
        return Maybe(self.value // other.value)

    def __mod__(self, other):
        if self.value == None or other.value == None:
            return Maybe(None)
        return Maybe(self.value % other.value)

    def __neg__(self):
        if self.value == None:
            return Maybe(None)
        return Maybe(-self.value)

    def __and__(self, other):
        if self.value == None or other.value == None:
            return Maybe(None)
        return Maybe(self.value and other.value)

    def __or__(self, other):
        if self.value == None or other.value == None:
            return Maybe(None)
        return Maybe(self.value or other.value)

    def __not__(self):
        if self.value == None or other.value == None:
            return Maybe(None)
        return Maybe(not self.value)

    def __bool__(self):
        if self.value:
            return True
        else:
            return False

    __nonzero__ = __bool__

    def __lt__(self, other):
        return Maybe((self.value < other.value))

    def __le__(self, other):
        return Maybe((self.value <= other.value))

    def __gt__(self, other):
        return Maybe((self.value > other.value))

    def __ge__(self, other):
        return Maybe((self.value >= other.value))

    def __eq__(self, other):
        return Maybe((self.value == other.value))

    def __ne__(self, other):
        return Maybe((self.value != other.value))

    def __str__(self):
        return 'Maybe(' + str(self.value) + ')'

    def __repr__(self):
        return self.__str__()


