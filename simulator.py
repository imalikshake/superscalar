import numpy as np
import assembler
import random
from collections import deque

program = assembler.program

reg_size = 32
mem_size = 4096
clock = 0
ALUinstructions = ["add", "addi", "sub", "subi", "cmp"] 
BranchInstructions = [ "blth", "blthe", "bgth", "bgthe", "bne", "be"] 

memory = np.zeros(mem_size, dtype=int)

         

for x in range(20, 30):
    memory[x] = 30 - x

class Fetch(object):
    def __init__(self):
        self.pc = 0
        self.branchFlag = 0
        self.EX = None
        self.output = {"noop":True}
        self.input = {"noop":True}


    def setup(self,EX):
        self.EX = EX
    
    def relativeBranch(self,branch):
        self.pc = branch["value"]

    def tick1(self):
        if self.pc < len(program):
            self.input = program[self.pc]
            self.input["noop"] = False
        else:
            self.input = {}
            self.input["noop"] = True

        self.output = self.input

        self.pc+=1
    
    def tick2(self):
        if self.branchFlag == 1:
            if self.pc < len(program):
                self.input = program[self.pc]
                self.input["noop"] = False
            else:
                self.input = {}
                self.input["noop"] = True

            self.output = self.input
            self.instruction_buffer.append(self.output)

            self.pc+=1
            self.branchFlag = 0
            # print "IF OUTPUT:"
            # print self.output

class Decode(object):
    def __init__(self):
        self.register_file = np.zeros(16, dtype=int)
        self.IF = None
        self.EX = None
        self.input = {"noop":True}
        self.output = {"noop":True}
        
    def setup(self,IF,EX):
        self.IF = IF
        self.EX = EX
    
    def printRegisterFile(self) :
        print ""
        i = 0
        for x in self.register_file:
            print "r" + str(i) + ":[" + str(x) + "]"
            i = i+1
        # raw_input("Press Enter to continue...")

    def writeToReg(self, intermediate):
        self.register_file[intermediate["id"]] = intermediate["value"]
        # print intermediate

    def tick1(self):
        self.input = self.IF.output
        self.output = {}
        self.output["noop"] = self.input["noop"]
       
        if not self.input["noop"]:
            
            self.output["opcode"] = self.input["opcode"]
            
            if self.input["opcode"] == "sys":
                self.output["arg1"] = self.input["arg1"]
                if self.output["arg1"] == "r":
                    pass
                else:
                    self.output["arg2"] = self.input["arg2"]
                    self.output["arg3"] = self.input["arg3"]

            else:
                if "arg1" in self.input:
                    self.output["arg1"] = int(self.input["arg1"][1:])
     
                if "arg2" in self.input:
                    self.output["arg2"] = int(self.input["arg2"][1:])

                if "arg3" in self.input:
                    self.output["arg3"] = int(self.input["arg3"][1:])

                if self.output["opcode"] in ALUinstructions:
                    self.output["B"] = self.register_file[self.output["arg2"]]
                    self.output["C"] = self.register_file[self.output["arg3"]]
                
                elif self.output["opcode"] in BranchInstructions:
                    self.output["B"] = self.register_file[self.output["arg1"]]

                elif self.output["opcode"] == "sto":
                    self.output["B"] = self.register_file[self.output["arg1"]]
                    self.output["C"] = self.register_file[self.output["arg2"]]

                elif self.output["opcode"] == "ldr":
                    self.output["B"] = self.register_file[self.output["arg2"]]
        # print "ID OUTPUT:"
        # print self.output
    def tick2(self):
        pass
            # self.input = self.IF.output
            # print "ID INPUT:"
            # print self.input

class Execute(object):
    def __init__(self):
        self.forwarding_reg = {"id" : None,
                                "value" : None}
        self.IF = None
        self.ID = None
        self.WB = None
        self.input = {"noop":True}
        self.output = {"noop":True}

    def setup(self,IF,ID,WB):
        self.IF = IF
        self.ID = ID
        self.WB = WB

        self.mem_unit = Memory_unit()
        self.alu_unit = ALU_unit()
        self.branch_unit = Branch_unit()

    def tick1(self):
        self.input = self.ID.output
        # print "EX INPUT:"
        # print self.input
        self.output = {}
        self.output["noop"] = self.input["noop"]
        value = None;
        type = None;
        id = None;
        if not self.input["noop"]:
            if self.input["opcode"] in ALUinstructions:
                if self.forwarding_reg["id"]  == self.input["arg2"]:
                    self.input["B"] = self.forwarding_reg["value"] 

                elif self.forwarding_reg["id"]  == self.input["arg3"]:
                    self.input["C"] = self.forwarding_reg["value"] 
            
            elif self.input["opcode"] in BranchInstructions:
                if self.forwarding_reg["id"]  == self.input["arg1"]:
                    self.input["B"] = self.forwarding_reg["value"] 

            elif self.input["opcode"] == "sto":
                if self.forwarding_reg["id"]  == self.input["arg1"]:
                    self.input["B"] = self.forwarding_reg["value"] 
                elif self.forwarding_reg["id"]  == self.input["arg2"]:
                    self.input["C"] = self.forwarding_reg["value"] 

            elif self.input["opcode"] == "ldr":
                if self.forwarding_reg["id"]  == self.input["arg2"]:
                    self.input["B"] = self.forwarding_reg["value"] 

        if not self.input["noop"]:
            if self.input["opcode"] == "add" :
                self.output["value"] = self.input["B"] + self.input["C"]
                self.output["type"] = "register"
                self.output["action"] = "write"
                self.output["id"] = self.input["arg1"]
                
            elif self.input["opcode"] == "addi": 
                # print self.input
                self.output["value"] = self.input["B"] + self.input["arg3"]
                self.output["type"] = "register"
                self.output["id"] = self.input["arg1"]
                self.output["action"] = "write"

            elif self.input["opcode"] == "sub" :
                self.output["value"] = self.input["B"] - self.input["C"]
                self.output["type"] = "register"
                self.output["id"] = self.input["arg1"]
                self.output["action"] = "write"

            elif self.input["opcode"] == "subi" :
                self.output["value"] = self.input["B"] - self.input["arg3"]
                self.output["type"] = "register"
                self.output["id"] = self.input["arg1"]
                self.output["action"] = "write"   

            elif self.input["opcode"] == "blth":
                if self.input["B"] < 0:
                    self.output["type"] = "pc"
                    self.output["value"] = self.input["arg2"]
                else :
                    self.output["noop"] = True
            
            elif self.input["opcode"] == "be":
                if self.input["B"] == 0:
                    self.output["type"] = "pc"
                    self.output["value"] = self.input["arg2"]
                else :
                    self.output["noop"] = True
            
            elif self.input["opcode"] == "bgth":
                if self.input["B"] > 0:
                    self.output["type"] = "pc"
                    self.output["value"] = self.input["arg2"]
                else :
                    self.output["noop"] = True
            
            elif self.input["opcode"] == "blthe":
                if self.input["B"] <= 0:
                    self.output["type"] = "pc"
                    self.output["value"] = self.input["arg2"]
                else :
                    self.output["noop"] = True
            
            elif self.input["opcode"] == "bgthe":
                if self.input["B"] >= 0:
                    self.output["type"] = "pc"
                    self.output["value"] = self.input["arg2"]
                else :
                    self.output["noop"] = True

            elif self.input["opcode"] == "j":
                self.output["type"] = "pc"
                self.output["value"] = self.input["arg1"]

            elif self.input["opcode"] == "bne":
                if self.input["B"] != 0:
                    self.output["type"] = "pc"
                    self.output["value"] = self.input["arg2"]
                else :
                    self.output["noop"] = True

            elif self.input["opcode"] == "cmp" :
                
                value = self.input["B"] - self.input["C"]

                compare = None;
                if value > 0 : compare = 1
                elif value == 0 : compare = 0
                elif value < 0 : compare = -1
                self.output["type"] = "register"
                self.output["action"] = "write"
                self.output["id"] = self.input["arg1"]
                self.output["value"] = compare
                
            elif self.input["opcode"] == "ldc" :
                self.output["type"] = "register"
                self.output["id"] = self.input["arg1"]
                self.output["value"] = self.input["arg2"]
                self.output["action"] = "write"

            elif self.input["opcode"] == "ldr" :
                 
                self.output["type"] = "memory"
                self.output["action"] = "read"
                self.output["id"] = self.input["arg1"]
                self.output["value"] = self.input["B"]

                self.output["value"] = memory[self.output["value"]]
                self.output["type"] = "register"
                self.output["action"] = "write"
                
            elif self.input["opcode"] == "sto" :
                self.output["type"] = "memory"
                self.output["action"] = "write"
                self.output["id"] = self.input["B"]
                self.output["value"] = self.input["C"]
                
            elif self.input["opcode"] == "sys":
                if self.input["arg1"] == 'r':
                    self.output["type"] = "register"
                    self.output["action"] = "print" 

                elif self.input["arg1"] == 'm':
                    self.output["type"] = "memory"
                    self.output["action"] = "print" 
                    self.output["arg1"] = self.input["arg2"]
                    self.output["arg2"] = self.input["arg3"]

            else:
                print "Cannot find execute for" + str(self.input)

        if not self.input["noop"]:
            if self.input["opcode"] in ALUinstructions:
                self.forwarding_reg["id"] = self.input["arg1"]
                self.forwarding_reg["value"] = self.output["value"]
            
            elif self.input["opcode"] in ["ldr","ldc","cmp"]:
                self.forwarding_reg["id"] = self.input["arg1"]
                self.forwarding_reg["value"] = self.output["value"]

        if not self.output["noop"] == True:
            if self.output["type"] == "pc":
                self.IF.relativeBranch(self.output)
                self.ID.output = {"noop":True}
                self.ID.input = {"noop":True}
                self.IF.input = {"noop":True}
                self.IF.output = {"noop":True}

    def tick2(self):
        pass
        # if not self.output["noop"] == True:
        #     if self.output["type"] == "pc":
        #         self.IF.relativeBranch(self.output)
        # print "EX OUTPUT:"
        # print self.output

class WriteBack(object):
    def __init__(self):
        self.ID = None
        self.EX = None
        self.input = {"noop":True}

    def setup(self,ID,EX):
        self.ID = ID
        self.EX = EX

    def printMemory(self, fromIndex, toIndex):
        print ""
        i = fromIndex
        for x in memory[fromIndex:toIndex]:
            print "m" + "[" + str(i) + "]" + ":[" + str(x) + "]"
            i = i+1
        # raw_input("Press Enter to continue...")
    
    def tick1(self):
        self.input = self.EX.output
        # print "WB INPUT:"
        # print self.input
        if not self.input["noop"]:
            if self.input["type"] == "register":
                
                if self.input["action"] == "write":
                    self.ID.writeToReg(self.input)
                    
                elif self.input["action"] == "print":
                    self.ID.printRegisterFile()
            
            elif self.input["type"] == "memory":
                if self.input["action"] == "write":
                    memory[self.input["id"]] = self.input["value"]

                elif self.input["action"] == "print":
                    self.printMemory(int(self.input["arg1"]),int(self.input["arg2"]))
                

    def tick2(self):
        pass

# ---------------- #

class ALU_unit(object):
    def __init__(self):
        self.RS = [RS() for x in range(3)]
        self.end_time = 0

class Memory_unit(object):
    def __init__(self):
        self.RS = [RS() for x in range(2)]
        self.end_time = 0

class Branch_unit(object):
    def __init__(self):
        pass

class RS(object):
    def __init__(self):
        self.op = ''
        self.qj = self.qk = 0
        self.vj = self.vk = 0
        self.A = 0
        self.busy = False
        self.ins = None 

# ---------------- #

class Processor(object):
    def __init__(self):
        self.IF = Fetch()
        self.ID = Decode()
        self.EX = Execute()
        self.WB = WriteBack()

    def setup(self):
        self.IF.setup(self.ID)
        self.ID.setup(self.IF,self.EX)
        self.EX.setup(self.IF,self.ID, self.WB)
        self.WB.setup(self.ID,self.EX)

    def tick1(self):
        self.IF.tick1()
        self.WB.tick1()
        self.ID.tick1()
        self.EX.tick1()
    
    def tick2(self):

        self.IF.tick2()
        self.ID.tick2()
        self.EX.tick2()
        self.WB.tick2()

    def isComplete(self):
        if self.IF.output["noop"] == True and self.ID.output["noop"] == True and self.EX.output["noop"] == True and self.WB.input["noop"] == True :
            return True

def run():
    global clock
    proc = Processor()
    proc.setup()

    while True:
        proc.tick1()
        proc.tick2()
        clock += 1
        if proc.isComplete():
            print "Clock Cycles:" + str(clock)
            break;

run()


