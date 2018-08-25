
class IPRangeGenerator(object):
    """
    'ipaddr' should be in the following format:
        A.B.C.D
    Where the letters (A, B, C, D) could be either a number in range 0-255 or
    an asterix (*). If it is a number, the field will be static, otherwise it
    will be dynamic and generated.
    """
    def __init__(self, ipaddr):
        self.finished = False
        self.beginning = []
        self.end = []

        tmp = ipaddr.split('.')
        for i in tmp:
            if i == '*':
                self.beginning.append(0)
                self.end.append(255)
            else:
                self.beginning.append(int(i))
                self.end.append(int(i))

        self.b = self.beginning[:]
        self.e = self.end[:]

    def __iter__(self):
        return self

    # python 3 compatibility
    def __next__(self):
        return self.next()

    def next(self):
        if self.finished: raise StopIteration()
        to_return = str(self.b[0]) + '.' + str(self.b[1]) + '.' + str(self.b[2]) + '.' + str(self.b[3])

        self.b[3] += 1
        for i in range(3, 0, -1):
            if self.b[i] > self.e[i]:
                self.b[i] = self.beginning[i]
                self.b[i - 1] += 1
        if self.b[0] > self.e[0]:
            self.finished = True

        return to_return
