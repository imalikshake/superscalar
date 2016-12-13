import numpy as np
import assembler
import random
from collections import deque

program = assembler.program

reg_size = 16
mem_size = 4096

clock = 0

ALUinstructions = ["add", "addi", "sub", "subi", "cmp"] 
BranchInstructions = [ "blth", "blthe", "bgth", "bgthe", "bne", "be"] 


memory = np.zeros(mem_size, dtype=int)

for x in range(20, 30):
    memory[x] = 30 - x

class ALU_unit(object):
    def __init__(self):
        self.busy = False
        self.rs_id = 0
        self.result = {}

class Memory_unit(object):
    def __init__(self):
        self.rs = [RS() for i in range(1)]
        self.busy = False
        self.rs_id = 0
        self.result = {}

class Branch_unit(object):
    def __init__(self):
        self.rs = [RS() for i in range(1)]
        self.busy = False
        self.rs_id = 0
        self.result = {}

class RS(object):
    def __init__(self):
        self.opcode = ''
        self.qj = self.qk = 0
        self.vj = self.vk = 0
        self.A = 0
        self.busy = False
        self.instruction = None 
        self.d = None

    def reset(self):
        self.opcode = ''
        self.qj = self.qk = 0
        self.vj = self.vk = 0
        self.A = 0
        self.busy = False
        self.instruction = None 
        self.d = None

class Registers:
    def __init__(self, size=16):
        self.qi = [0 for i in range(size)]
        self.val = [0.0 for i in range(size)]
        self.size = size
    
    def reset(self):
        self.qi = [0 for i in range(self.size)]
        self.val = [0.0 for i in range(self.size)]
    
    def print_reg(self):
        print "----------------------------------------------------------------"
        print "REGISTER FILE"
        print "----------------------------------------------------------------"
        for i in range(self.size):
            print '\tRegister: Q[%d]: %d, Value[%d]: %f' % (i, self.qi[i], i, self.val[i])
        print "----------------------------------------------------------------"

class Fetch(object):
    def __init__(self):
        self.pc = 0
        self.branchFlag = 0
        self.output = {"noop":True}
        self.input = {"noop":True}
        self.stall = False
    
    def relativeBranch(self,branch):
        self.pc = branch["value"]

    def tick(self):
        if self.pc < len(program):
            self.input = program[self.pc]
            self.input["noop"] = False
        else:
            self.input = {}
            self.input["noop"] = True

        self.output = self.input
        self.pc+=1
    
    def tock(self):
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
            self.branchFlag = 0

class Decode(object):
    def __init__(self):
        self.register_file = Registers()
        self.input = {"noop":True}
        self.output = {"noop":True}

    def tick(self):
        self.input = IF.output
        self.output = {}
        self.output["noop"] = self.input["noop"]
       
        if not self.input["noop"]:
            
            self.output["opcode"] = self.input["opcode"]
            
            if self.input["opcode"] == "sys":
                self.output["file"] = self.input["arg1"]
                if self.output["file"] == "r":
                    pass
                else:
                    self.output["from"] = self.input["arg2"]
                    self.output["to"] = self.input["arg3"]

            else:
                if "arg1" in self.input:
                    self.output["arg1"] = int(self.input["arg1"][1:])
     
                if "arg2" in self.input:
                    self.output["arg2"] = int(self.input["arg2"][1:])

                if "arg3" in self.input:
                    self.output["arg3"] = int(self.input["arg3"][1:])

    def tock(self):
        if not self.output["noop"]:
            if not self.output["opcode"] == "sys" :
                # MEM_UNIT
                if self.output["opcode"] == "sto" or self.output["opcode"] == "ldr" or self.output["opcode"] == "ldc"  :
                    for i in range(RS_map["MEM"][0],RS_map["MEM"][1]):
                        if RESERVE[i].busy == False:
                            
                            RESERVE[i].busy = True
                            RESERVE[i].opcode = self.output["opcode"]
                            RESERVE[i].instruction = self.output

                            if self.output["opcode"] == "ldc":

                                self.register_file.qi[self.output["arg1"]] = i
                                RESERVE[i].A = self.output["arg2"]
                                RESERVE[i].d = self.output["arg1"]

                            elif self.output["opcode"] == "sto":
                                if self.register_file.qi[self.output["arg1"]] == 0:
                                    RESERVE[i].qj = 0
                                    RESERVE[i].vj = self.register_file.val[self.output["arg1"]]

                                else:
                                    RESERVE[i].qj = self.register_file.qi[self.output["arg1"]]

                                if self.register_file.qi[self.output["arg2"]] == 0:
                                    RESERVE[i].qk = 0
                                    RESERVE[i].vk = self.register_file.val[self.output["arg2"]]
                                else:
                                    RESERVE[i].qk = self.register_file.qi[self.output["arg2"]]

                            elif self.output["opcode"] == "ldr":
                                
                                self.register_file.qi[self.output["arg1"]] = i
                                RESERVE[i].d = self.output["arg1"]

                                if self.register_file.qi[self.output["arg2"]] == 0:
                                    RESERVE[i].qj = 0
                                    RESERVE[i].vj = self.register_file.val[self.output["arg2"]]
                            
                                else:
                                    RESERVE[i].qj = self.register_file.qi[self.output["arg2"]]
                
                # ALU_UNIT
                elif self.output["opcode"] in ALUinstructions:
                    for i in range(RS_map["ALU"][0],RS_map["ALU"][1]):
                        if RESERVE[i].busy == False:
                            
                            RESERVE[i].busy = True
                            RESERVE[i].opcode = self.output["opcode"]
                            RESERVE[i].instruction = self.output
                            
                            if self.output["opcode"] == "add" or self.output["opcode"] == "sub" or self.output["opcode"] == "cmp":
                              
                              self.register_file.qi[self.output["arg1"]] = i  
                              RESERVE[i].d = self.output["arg1"]

                              if self.register_file.qi[self.output["arg2"]] == 0:
                                  RESERVE[i].qj = 0
                                  RESERVE[i].vj = self.register_file.val[self.output["arg2"]]

                              else:
                                  RESERVE[i].qj = self.register_file.qi[self.output["arg2"]]

                              if self.register_file.qi[self.output["arg3"]] == 0:
                                  RESERVE[i].qk = 0
                                  RESERVE[i].vk = self.register_file.val[self.output["arg3"]]
                              else:
                                  RESERVE[i].qk = self.register_file.qi[self.output["arg3"]]
                        
                            if self.output["opcode"] == "addi" or self.output["opcode"] == "subi":
                                self.register_file.qi[self.output["arg1"]] = i  
                                RESERVE[i].A = self.output["arg3"]

                                if self.register_file.qi[self.output["arg2"]] == 0:
                                    RESERVE[i].qj = 0
                                    RESERVE[i].vj = self.register_file.val[self.output["arg2"]]

                                else:
                                    RESERVE[i].qj = self.register_file.qi[self.output["arg2"]]

                # BRANCH_UNIT
                
                elif self.output["opcode"] in BranchInstructions or self.output["opcode"] == "j": 
                    for i in range(RS_map["BRANCH"][0],RS_map["BRANCH"][1]):
                        if RESERVE[i].busy == False:
                            
                            RESERVE[i].busy = True
                            RESERVE[i].opcode = self.output["opcode"]
                            RESERVE[i].instruction = self.output
                            
                            if self.output["opcode"] == "j":
                                RESERVE[i].A = self.output["arg1"]
                            else:
                                RESERVE[i].A = self.output["arg2"]

                            if self.output["opcode"] in BranchInstructions:
                                if self.register_file.qi[self.output["arg1"]] == 0:
                                    RESERVE[i].qj = 0
                                    RESERVE[i].vj = self.register_file.val[self.output["arg1"]]

                                else:
                                    RESERVE[i].qj = self.register_file.qi[self.output["arg1"]]

class Execute(object):
    def __init__(self):
        self.alu_unit = ALU_unit()
        self.mem_unit = Memory_unit()
        self.branch_unit = Branch_unit()

    def issue_mem(self):
        if self.mem_unit.busy == False:
            for i in range(RS_map["MEM"][0],RS_map["MEM"][1]):
                if RESERVE[i].qj == 0 and RESERVE[i].qk == 0 and RESERVE[i].busy == True:
                    if RESERVE[i].opcode == "ldc":
                        destination = RESERVE[i].d
                        self.mem_unit.result["type"] = "register"
                        self.mem_unit.result["action"] = "write"
                        self.mem_unit.result["id"] = destination
                        self.mem_unit.result["value"] = RESERVE[i].A
                        self.mem_unit.result["destination"] = "register"

                    elif RESERVE[i].opcode == "sto":
                        operand1 = RESERVE[i].vj 
                        operand2 = RESERVE[i].vk 
                        self.mem_unit.result["type"] = "memory"
                        self.mem_unit.result["action"] = "write"
                        self.mem_unit.result["id"] = operand1
                        self.mem_unit.result["value"] = operand2
                        self.mem_unit.result["destination"] = "memory"

                    elif RESERVE[i].opcode == "ldr":
                        operand1 = RESERVE[i].vj 
                        destination = RESERVE[i].d
                        
                        self.mem_unit.result["type"] = "memory"
                        self.mem_unit.result["action"] = "read"
                        self.mem_unit.result["id"] = destination
                        self.mem_unit.result["value"] = operand1
                        self.mem_unit.result["destination"] = "register"

    def issue_branch(self):
        if self.branch_unit.busy == False:
            for i in range(RS_map["BRANCH"][0],RS_map["BRANCH"][1]):
                if RESERVE[i].qj == 0 and RESERVE[i].qk == 0 and RESERVE[i].busy == True:
                    
                    opcode = RESERVE[i].opcode
                    
                    if opcode == "j" :
                       self.branch_unit.result["type"] = "pc"
                       self.branch_unit.result["value"] = RESERVE[i].A

                    else:
                        operand1 = RESERVE[i].vj
                        if opcode == "blth":
                            if operand1 < 0:
                               self.branch_unit.result["type"] = "pc"
                               self.branch_unit.result["value"] = RESERVE[i].A
                            else :
                               self.branch_unit.result["noop"] = True
                        
                        elif opcode == "be":
                            if operand1 == 0:
                               self.branch_unit.result["type"] = "pc"
                               self.branch_unit.result["value"] = RESERVE[i].A
                            else :
                               self.branch_unit.result["noop"] = True
                        
                        elif opcode == "bgth":
                            if operand1 > 0:
                               self.branch_unit.result["type"] = "pc"
                               self.branch_unit.result["value"] = RESERVE[i].A
                            else :
                               self.branch_unit.result["noop"] = True
                        
                        elif opcode == "blthe":
                            if operand1 <= 0:
                               self.branch_unit.result["type"] = "pc"
                               self.branch_unit.result["value"] = RESERVE[i].A
                            else :
                               self.branch_unit.result["noop"] = True
                        
                        elif opcode == "bgthe":
                            if operand1 >= 0:
                               self.branch_unit.result["type"] = "pc"
                               self.branch_unit.result["value"] = RESERVE[i].A
                            else :
                               self.branch_unit.result["noop"] = True

                        elif opcode == "bne":
                            if operand1 != 0:
                               self.branch_unit.result["type"] = "pc"
                               self.branch_unit.result["value"] = RESERVE[i].A
                            else :
                               self.branch_unit.result["noop"] = True

    def issue_alu(self):
        if self.alu_unit.busy == False:
            for i in range(RS_map["ALU"][0],RS_map["ALU"][1]):
                if RESERVE[i].qj == 0 and RESERVE[i].qk == 0 and RESERVE[i].busy == True:
                    opcode = RESERVE[i].opcode
                    operand1 = RESERVE[i].vj
                    operand2 = RESERVE[i].vk
                    destination = RESERVE[i].instruction["arg1"]
                    
                    if opcode == "add" or opcode == "addi":
                       self.alu_unit.result["value"] = operand1 + operand2
                       self.alu_unit.result["type"] = "register"
                       self.alu_unit.result["action"] = "write"
                       self.alu_unit.result["id"] = destination
                        
                    elif opcode == "sub" or opcode == "subi":
                       self.alu_unit.result["value"] = operand1 - operand2
                       self.alu_unit.result["type"] = "register"
                       self.alu_unit.result["id"] = destination
                       self.alu_unit.result["action"] = "write"

                    self.alu_unit.busy = False




    def print_units(self):
        print 'ALU unit: \n\tRS id: %d, result: %f, busy: %d' % ( self.alu_unit.rs_id, self.alu_unit.result, self.alu_unit.busy)
        print "----------------------------------------------------------------"
        print 'MEM unit: \n\tRS id: %d, result: %f, busy: %d' % ( self.mem_unit.rs_id, self.mem_unit.result, self.mem_unit.busy) 
        print "----------------------------------------------------------------"
        print 'BRANCH unit: \n\tRS id: %d, result: %f, busy: %d' % ( self.branch_unit.rs_id, self.branch_unit.result, self.branch_unit.busy) 

class CDB(object):
    def __init__(self):
        self.alu_result = None
        self.mem_result = None
        self.branch_result = None

    def fetch_results(self):
        self.alu_result = EX.alu_unit.result
        self.mem_result = EX.mem_unit.result
        self.branch_result = EX.branch_unit.result

    def write_results(self):
        

    def reset(self):
        self.alu_results = None
        self.mem_results = None
        self.branch_results = None

class WriteBack(object):
    def __init__(self):
        self.input = {"noop":True}

    def printMemory(self, fromIndex, toIndex):
        print ""
        i = fromIndex
        for x in memory[fromIndex:toIndex]:
            print "m" + "[" + str(i) + "]" + ":[" + str(x) + "]"
            i = i+1

RS_map = {"ALU":(1,2), "MEM":(2,3), "BRANCH":(3,4)}
RESERVE = [RS() for i in range(4)]

def print_reserve():
    for i in range(len(RESERVE)):
        if i == 0:
            continue
        elif i  <= RS_map["ALU"][0] and i < RS_map["ALU"][1]:
            print "----------------------------------------------------------------"
            print "ALU"

        elif i  >= RS_map["MEM"][0] and i < RS_map["MEM"][1]:
            print "MEM"
        elif i  >= RS_map["BRANCH"][0] and i < RS_map["BRANCH"][1]:
            print "BRANCH"
        print '\tRESERVE #%d, Op: %s, Qj: %d, Qk: %d, Vj: %d, Vk: %d, busy: %d, A: %d' % (i, RESERVE[i].opcode, RESERVE[i].qj, RESERVE[i].qk, RESERVE[i].vj, RESERVE[i].vk, RESERVE[i].busy, RESERVE[i].A)
    print "----------------------------------------------------------------"

def tick():
    IF.tick()
    # WB.tick()
    ID.tick()
    EX.tick()

def tock():
    IF.tock()
    ID.tock()
    EX.tock()



def run():
    for i in range(3):
        tick()
        tock()
        raw_input("")

         
IF = Fetch()
ID = Decode()
EX = Execute()
CDbus = CDB()

IF.tick()
ID.tick()
IF.tock()
ID.tock()
print_reserve()
IF.tick()
ID.tick()
IF.tock()
ID.tock()
print_reserve()
IF.tick()
ID.tick()
IF.tock()
ID.tock()
print_reserve()
# ID.register_file.print_reg()
# EX.print_units()