class A:
    def __init__(self):
        print(str(self))

import b
class C(b.B):
    def __str__(self):
        return 'C'
