from collections import deque

class InstructionQueue(object):
    def __init__(self):
        self.instructions = deque()
        self.buffer_size= 16
    
    def peak(self):
        return self.instructions[0]
    
    def add(self, val):
        self.instructions.append(val)
    
    def pop(self):
        return self.instructions.popleft()
    
    def printQueue(self):
        print self.instructions

    def isFull(self):
        if len(self.instructions) == self.buffer_size:
            return True
        else:
            return False

a = InstructionQueue()

a.add("a")
a.add("b")
a.add("c")
a.add("d")

a.printQueue()
print a.pop()
a.printQueue()
