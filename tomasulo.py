import numpy as np
import assembler
import random
from collections import deque

class InstructionQueue(object):
    def __init__(self):
        self.instructions = deque()
        self.buffer_size = 1
    
    def reset(self):
        self.instructions =  deque()

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
class ALU_unit(object):
    def __init__(self):
        self.busy = False
        self.rs_id = 0
        self.result = 0
class Memory_unit(object):
    def __init__(self):
        self.busy = False
        self.rs_id =  0
        self.result = 0
class Branch_unit(object):
    def __init__(self):
        self.busy = False
        self.rs_id = 0
        self.result = 0
class RS(object):
    def __init__(self):
        self.opcode = ''
        self.qk = 0
        self.vk = 0
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
class Registers(object):
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
        self.instruction = {"noop":True}
        self.branch_flag = 0

    def relativeBranch(self, new_pc):
        self.pc = new_pc
        IQ.reset()

    def tick(self):
        print self.pc
        if not IQ.isFull():
            if self.pc < len(program):
                self.instruction = program[self.pc]
                self.instruction["noop"] = False

            else:
                self.instruction = {}
                self.instruction["noop"] = True
                self.instruction["terminate"] = True


            self.pc+=1
            IQ.add(self.instruction)
    
    def tock(self):
        # print self.branch_flag 
        print self.pc
        if self.branch_flag == 1:

            if self.pc < len(program):
                self.instruction = program[self.pc]
                self.instruction["noop"] = False

            else:
                self.instruction = {}
                self.instruction["noop"] = True
                self.instruction["terminate"] = True

            self.branch_flag  = 0
            self.pc+=1
            IQ.add(self.instruction)


class Decode(object):
    def __init__(self):
        self.register_file = Registers()
        self.instruction = None
        self.stall = False
    
    def update_reg(self, rs_id, result):
        if rs_id is not 0:
            for i in range(reg_size):
                if self.register_file.qi[i] == rs_id:
                    print "$$$$$ REG_ID: %d RS_ID: %d RESULT: %d $$$$" % (i, rs_id, result)
                    self.register_file.qi[i] = 0
                    self.register_file.val[i] = result
        
    def tock(self):
        self.instruction = IQ.peak()
        self.output = {}
        self.output["noop"] = self.instruction["noop"]
        
        # if "terminate" in self.instruction:
        #     if self.instruction["terminate"] == True:
        #         self.terminate = True
        
        if not self.instruction["noop"]:
            self.output["opcode"] = self.instruction["opcode"]
            
            if self.instruction["opcode"] == "sys":
                self.output["file"] = self.instruction["arg1"]
                if self.output["file"] == "r":
                    pass
                else:
                    self.output["from"] = self.instruction["arg2"]
                    self.output["to"] = self.instruction["arg3"]

            else:
                if "arg1" in self.instruction:
                    self.output["arg1"] = int(self.instruction["arg1"][1:])
     
                if "arg2" in self.instruction:
                    self.output["arg2"] = int(self.instruction["arg2"][1:])

                if "arg3" in self.instruction:
                    self.output["arg3"] = int(self.instruction["arg3"][1:])

        if not self.output["noop"] and self.stall is False:
            if not self.output["opcode"] == "sys" :
                # MEM_UNIT
                issued = False
                if self.output["opcode"] == "sto" or self.output["opcode"] == "ldr" or self.output["opcode"] == "ldc"  :
                    for i in range(RS_map["MEM"][0],RS_map["MEM"][1]):
                        if RESERVE[i].busy == False:
                            issued = True
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

                                if self.register_file.qi[self.output["arg2"]] == 0 or self.register_file.qi[self.output["arg2"]] == i:
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
                            issued = True

                            if self.output["opcode"] == "add" or self.output["opcode"] == "sub" or self.output["opcode"] == "cmp":
                              self.register_file.qi[self.output["arg1"]] = i  
                              RESERVE[i].d = self.output["arg1"]

                              if self.register_file.qi[self.output["arg2"]] == 0 or self.register_file.qi[self.output["arg2"]] == i:
                                  RESERVE[i].qj = 0
                                  RESERVE[i].vj = self.register_file.val[self.output["arg2"]]

                              else:
                                  RESERVE[i].qj = self.register_file.qi[self.output["arg2"]]

                              if self.register_file.qi[self.output["arg3"]] == 0 or self.register_file.qi[self.output["arg3"]] == i:
                                  RESERVE[i].qk = 0
                                  RESERVE[i].vk = self.register_file.val[self.output["arg3"]]
                              else:
                                  RESERVE[i].qk = self.register_file.qi[self.output["arg3"]]
                        
                            if self.output["opcode"] == "addi" or self.output["opcode"] == "subi":
                                self.register_file.qi[self.output["arg1"]] = i  
                                RESERVE[i].A = self.output["arg3"]

                                if self.register_file.qi[self.output["arg2"]] == 0 or self.register_file.qi[self.output["arg2"]] == i:
                                    RESERVE[i].qj = 0
                                    RESERVE[i].vj = self.register_file.val[self.output["arg2"]]

                                else:
                                    RESERVE[i].qj = self.register_file.qi[self.output["arg2"]]
                # BRANCH_UNIT                
                elif self.output["opcode"] in BranchInstructions or self.output["opcode"] == "j": 
                    self.stall = True
                    if self.output["opcode"] == "j":
                        self.stall = False
                        IF.relativeBranch(self.output["arg1"])
                        IF.branch_flag = 1
                    else:
                        for i in range(RS_map["BRANCH"][0],RS_map["BRANCH"][1]):
                            if RESERVE[i].busy == False:
                                RESERVE[i].busy = True
                                RESERVE[i].opcode = self.output["opcode"]
                                RESERVE[i].instruction = self.output
                                issued = True
                                RESERVE[i].A = self.output["arg2"]

                                if self.register_file.qi[self.output["arg1"]] == 0:
                                    RESERVE[i].qj = 0
                                    RESERVE[i].vj = self.register_file.val[self.output["arg1"]]

                                else:
                                    RESERVE[i].qj = self.register_file.qi[self.output["arg1"]]

                if issued == True:
                    IQ.pop()
    
    def tick(self):
        pass
class Execute(object):
    def __init__(self):
        self.alu_unit = None
        self.mem_unit = None
        self.branch_unit = None

    def issue_mem(self):
        if self.mem_unit.busy == False:
            for i in range(RS_map["MEM"][0],RS_map["MEM"][1]):
                if RESERVE[i].qj == 0 and RESERVE[i].qk == 0 and RESERVE[i].busy == True:
                    self.mem_unit.busy = True
                    self.mem_unit.rs_id = i

                    if RESERVE[i].opcode == "ldc":
                        destination = RESERVE[i].d
                        self.mem_unit.result = RESERVE[i].A

                    elif RESERVE[i].opcode == "sto":
                        operand1 = RESERVE[i].vj 
                        operand2 = RESERVE[i].vk
                        self.mem_unit.result = operand2 

                    elif RESERVE[i].opcode == "ldr":
                        operand1 = RESERVE[i].vj 
                        destination = RESERVE[i].d
                        self.mem_unit.result = operand1
    def issue_branch(self):
        if self.branch_unit.busy == False:
            for i in range(RS_map["BRANCH"][0],RS_map["BRANCH"][1]):
                if RESERVE[i].qj == 0 and RESERVE[i].qk == 0 and RESERVE[i].busy == True:
                   
                    self.branch_unit.rs_id = i
                    self.branch_unit.busy = True

                    opcode = RESERVE[i].opcode
                
                    operand1 = RESERVE[i].vj
                    if opcode == "blth":
                        if operand1 < 0:
                            self.branch_unit.result = RESERVE[i].A
                        else :
                            self.branch_unit.result = "noop"                        
                    
                    elif opcode == "be":
                        if operand1 == 0:
                           self.branch_unit.result = RESERVE[i].A

                        else :
                            self.branch_unit.result = "noop"                        
                    elif opcode == "bgth":
                        if operand1 > 0:
                           self.branch_unit.result = RESERVE[i].A
                        else :
                            self.branch_unit.result = "noop"                        
                    
                    elif opcode == "blthe":
                        if operand1 <= 0:
                           self.branch_unit.result = RESERVE[i].A
                        else :
                            self.branch_unit.result = "noop"

                    elif opcode == "bgthe":
                        if operand1 >= 0:
                           self.branch_unit.result = RESERVE[i].A
                        else :
                            self.branch_unit.result = "noop"

                    elif opcode == "bne":
                        if operand1 != 0:
                           self.branch_unit.result = RESERVE[i].A
                        else :
                            self.branch_unit.result = "noop"
    def issue_alu(self):
        if self.alu_unit.busy == False:
            for i in range(RS_map["ALU"][0],RS_map["ALU"][1]):
                if RESERVE[i].qj == 0 and RESERVE[i].qk == 0 and RESERVE[i].busy == True:
                    opcode = RESERVE[i].opcode
                    operand1 = RESERVE[i].vj
                    operand2 = RESERVE[i].vk
                    destination = RESERVE[i].instruction["arg1"]
                    
                    self.alu_unit.rs_id = i
                    self.alu_unit.busy = True

                    if opcode == "add":
                        self.alu_unit.result =  RESERVE[i].vj + RESERVE[i].vk
                    elif opcode == "cmp":
                        self.alu_unit.result =  RESERVE[i].vj - RESERVE[i].vk
                    elif opcode == "sub":
                        self.alu_unit.result =  RESERVE[i].vj - RESERVE[i].vk
                    elif opcode == "subi":
                        self.alu_unit.result =  RESERVE[i].vj - RESERVE[i].A
                    elif opcode == "addi":
                       self.alu_unit.result =  RESERVE[i].vj +  RESERVE[i].A
                    
                    # print self.alu_unit.result
    def tock(self):
        self.issue_mem()
        self.issue_alu()
        self.issue_branch()
    
    def tick(self):
        if self.mem_unit.busy:
            result = {}
            result["rs_id"] = mem_unit.rs_id
            result["result"] = mem_unit.result
            CB.mem_results.append(result)
            # self.mem_unit.busy = False
        if self.alu_unit.busy:
            result = {}
            result["rs_id"] = alu_unit.rs_id
            result["result"] = alu_unit.result
            CB.alu_results.append(result)
            # self.alu_unit.busy = False
        if self.branch_unit.busy:
            result = {}
            result["rs_id"] = branch_unit.rs_id
            result["result"] = branch_unit.result
            CB.branch_results.append(result)
            
            ID.stall = False
            
            if result["result"] is not "noop":
                print result
                IF.relativeBranch(result["result"])
                IF.branch_flag = 1


    def print_units(self):
        print 'ALU unit: \n\tRS id: %d, result: %f, busy: %r' % ( self.alu_unit.rs_id, self.alu_unit.result, self.alu_unit.busy)
        print "----------------------------------------------------------------"
        print 'MEM unit: \n\tRS id: %d, result: %f, busy: %r' % ( self.mem_unit.rs_id, self.mem_unit.result, self.mem_unit.busy) 
        print "----------------------------------------------------------------"
        print 'BRANCH unit: \n\tRS id: %d, result: %s, busy: %r' % ( self.branch_unit.rs_id, str(self.branch_unit.result), self.branch_unit.busy) 

class CDB(object):
    def __init__(self):
        self.mem_results = []
        self.alu_results = []
        self.branch_results = []

class WriteBack(object):
    def __init__(self):
        pass

    def tock(self):
        if len(CB.mem_results) > 0:
            result = CB.mem_results.pop()
            rs_id =  result["rs_id"]
            result = result["result"]

            for i in range(RS_map['ALU'][0], RS_map['MEM'][1]):
                if RESERVE[i].qj == rs_id:
                    RESERVE[i].qj = 0
                    RESERVE[i].vj = result
            
                if RESERVE[i].qk == rs_id:
                    RESERVE[i].qk = 0
                    RESERVE[i].vk = result


            if RESERVE[rs_id].opcode == "ldc":
                ID.update_reg(rs_id, result)
            
            if RESERVE[rs_id].opcode == "ldr":
                print " $$$$$$$$$$$$$$ " + str(result)
                result = memory[result]
                ID.update_reg(rs_id, result)

            
            elif RESERVE[rs_id].opcode == "sto":
                print " $$$$$$$$$$$$$$ " + str(result)
                memory[RESERVE[i].vj] = result

            RESERVE[rs_id].busy = False
            EX.mem_unit.busy = False
        

        if len(CB.alu_results) > 0:
            result = CB.alu_results.pop()
            rs_id =  result["rs_id"]
            result = result["result"]

            for i in range(RS_map['ALU'][0], RS_map['MEM'][1]):
                if RESERVE[i].qj == rs_id:
                    RESERVE[i].qj = 0
                    RESERVE[i].vj = result
            
                if RESERVE[i].qk == rs_id:
                    RESERVE[i].qk = 0
                    RESERVE[i].vk = result

            ID.update_reg(rs_id, result)
            RESERVE[rs_id].busy = False
            EX.alu_unit.busy = False

        if len(CB.branch_results) > 0:
            result = CB.branch_results.pop()
            rs_id =  result["rs_id"]
            result = result["result"]

            EX.branch_unit.busy = False
            RESERVE[rs_id].busy = False



    def tick(self):
        pass

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
        print '\tRESERVE #%s, Op: %s, Qj: %s, Qk: %s, Vj: %s, Vk: %s, busy: %s, A: %s' % (i, RESERVE[i].opcode, RESERVE[i].qj, RESERVE[i].qk, RESERVE[i].vj, RESERVE[i].vk, RESERVE[i].busy, RESERVE[i].A)
    print "----------------------------------------------------------------"

def print_memory(fromIndex, toIndex):
    print ""
    i = fromIndex
    for x in memory[fromIndex:toIndex]:
        print "m" + "[" + str(i) + "]" + ":[" + str(x) + "]"
        i = i+1
    
RS_map = {"ALU":(1,2), "MEM":(2,3), "BRANCH":(3,4)}
RESERVE = [RS() for i in range(4)]


program = assembler.program

reg_size = 16
mem_size = 4096

clock = 0

ALUinstructions = ["add", "addi", "sub", "subi", "cmp"] 
BranchInstructions = [ "blth", "blthe", "bgth", "bgthe", "bne", "be"] 


memory = np.zeros(mem_size, dtype=int)

for x in range(20, 30):
    memory[x] = 30 - x

IF = Fetch()
ID = Decode()
EX = Execute()
CB = CDB()
WB = WriteBack()
IQ = InstructionQueue()

alu_unit = ALU_unit()
mem_unit = Memory_unit()
branch_unit = Branch_unit()
EX.mem_unit = mem_unit
EX.alu_unit = alu_unit
EX.branch_unit = branch_unit

def clock_tick():
    IF.tick()
    ID.tick()
    EX.tick()
    WB.tick()

    IF.tock()
    WB.tock()
    ID.tock()
    EX.tock()


def run():
    i = 0
    while True:
    # for x in range(1000):
        i+= 1
        clock_tick()
        print_reserve()
        EX.print_units()
        ID.register_file.print_reg()
        print_memory(20,30)
        raw_input("Press Enter to continue...")

        # if IF.terminate == True and EX.terminate == True and ID.terminate == True:
            # break
    print "Total clock cycles: %d" % (i)
run()
ID.register_file.print_reg()
# print_reserve()