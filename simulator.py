import numpy as np
import assembler
import random

program = assembler.program

register_file = np.zeros(16, dtype=int)
memory = np.zeros(100, dtype=int)

for x in range(20, 30):
    memory[x] = 30 - x

pc = 0 

def printRegisterFile() :
    print ""
    i = 0
    for x in register_file:
        print "r" + str(i) + ":[" + str(x) + "]"
        i = i+1
    # raw_input("Press Enter to continue...")

def printMemory(fromIndex, toIndex):
    print ""
    i = 0
    for x in memory[fromIndex:toIndex]:
        print "m" + "[" + str(i) + "]" + ":[" + str(x) + "]"
        i = i+1
    # raw_input("Press Enter to continue...")

# - - - - - - - - - - - - - - - - - - - - - #

def fetch(branch=None):
    global pc
    if branch is None:
        if pc < len(program):
            instruction = program[pc]
            instruction["noop"] = False
            pc+=1
            return instruction
        else:
            instruction = {}
            instruction["noop"] = True
            return instruction
    elif "type" in branch and branch["type"] == "pc":
        pc = branch["value"]
        return branch
    else:
        return branch

def decode(instruction):
    decoded = {}
    decoded["noop"] = instruction["noop"]
   
    if not instruction["noop"]:
        decoded["opcode"] = instruction["opcode"]
        if instruction["opcode"] == "sys":
            return instruction
       
        if "arg1" in instruction:
            # print str(instruction["arg1"])
            decoded["arg1"] = int(instruction["arg1"][1:])

        if "arg2" in instruction:
            # print str(instruction["arg2"])
            decoded["arg2"] = int(instruction["arg2"][1:])
        
        if "arg3" in instruction:
            # print str(instruction["arg3"])
            decoded["arg3"] = int(instruction["arg3"][1:])

    return decoded
    
def execute(instruction):
    intermediate = {}
    intermediate["noop"] = instruction["noop"]
    value = None;
    type = None;
    id = None;
    if not instruction["noop"]:
        if instruction["opcode"] == "add" :
            intermediate["value"] = register_file[instruction["arg2"]] + register_file[instruction["arg3"]]
            intermediate["type"] = "register"
            intermediate["action"] = "write"
            intermediate["id"] = instruction["arg1"]
            return intermediate
        
        elif instruction["opcode"] == "addi": 
            intermediate["value"] = register_file[instruction["arg2"]] + instruction["arg3"]
            intermediate["type"] = "register"
            intermediate["id"] = instruction["arg1"]
            intermediate["action"] = "write"
            return intermediate

        elif instruction["opcode"] == "sub" :
            intermediate["value"] = register_file[instruction["arg2"]] - register_file[instruction["arg3"]]
            intermediate["type"] = "register"
            intermediate["id"] = instruction["arg1"]
            intermediate["action"] = "write"
            return intermediate
            
        elif instruction["opcode"] == "subi" :
            intermediate["value"] = register_file[instruction["arg2"]] - instruction["arg3"]
            intermediate["type"] = "register"
            intermediate["id"] = instruction["arg1"]
            intermediate["action"] = "write"
            return intermediate   
            


        elif instruction["opcode"] == "blth":
            if register_file[instruction["arg1"]] < 0:
                intermediate["type"] = "pc"
                intermediate["value"] = instruction["arg2"]
            else :
                intermediate["noop"] = True
            return intermediate
        
        elif instruction["opcode"] == "be":
            if register_file[instruction["arg1"]] == 0:
                intermediate["type"] = "pc"
                intermediate["value"] = instruction["arg2"]
            else :
                intermediate["noop"] = True
            return intermediate
        
        elif instruction["opcode"] == "bgth":
            if register_file[instruction["arg1"]] > 0:
                intermediate["type"] = "pc"
                intermediate["value"] = instruction["arg2"]
            else :
                intermediate["noop"] = True
            return intermediate
        
        elif instruction["opcode"] == "blthe":
            if register_file[instruction["arg1"]] <= 0:
                intermediate["type"] = "pc"
                intermediate["value"] = instruction["arg2"]
            else :
                intermediate["noop"] = True
            return intermediate
        
        elif instruction["opcode"] == "bgthe":
            if register_file[instruction["arg1"]] >= 0:
                intermediate["type"] = "pc"
                intermediate["value"] = instruction["arg2"]
            else :
                intermediate["noop"] = True
            return intermediate

        elif instruction["opcode"] == "j":
            intermediate["type"] = "pc"
            intermediate["value"] = instruction["arg1"]
            return intermediate

        elif instruction["opcode"] == "bne":
            if register_file[instruction["arg1"]] != 0:
                intermediate["type"] = "pc"
                intermediate["value"] = instruction["arg2"]
            else :
                intermediate["noop"] = True
            return intermediate

        elif instruction["opcode"] == "cmp" :
            value = register_file[instruction["arg2"]] - register_file[instruction["arg3"]]
            compare = None;
            if value > 0 : compare = 1
            elif value == 0 : compare = 0
            elif value < 0 : compare = -1
            intermediate["type"] = "register"
            intermediate["action"] = "write"
            intermediate["id"] = instruction["arg1"]
            intermediate["value"] = compare
            return intermediate



        elif instruction["opcode"] == "ldc" :
            intermediate["type"] = "register"
            intermediate["id"] = instruction["arg1"]
            intermediate["value"] = instruction["arg2"]
            intermediate["action"] = "write"
            return intermediate

        elif instruction["opcode"] == "ldr" :
            intermediate["type"] = "memory"
            intermediate["action"] = "read"
            intermediate["id"] = instruction["arg1"]
            intermediate["value"] = register_file[instruction["arg2"]]
            return intermediate

        elif instruction["opcode"] == "sto" :
            intermediate["type"] = "memory"
            intermediate["action"] = "write"
            intermediate["id"] = register_file[instruction["arg1"]]
            intermediate["value"] = register_file[instruction["arg2"]]
            return intermediate



        elif instruction["opcode"] == "sys":
            if instruction["arg1"] == 'r':
                intermediate["type"] = "register"
                intermediate["action"] = "print" 
                # printRegisterFile()
            elif instruction["arg1"] == 'm':
                intermediate["type"] = "memory"
                intermediate["action"] = "print" 
                intermediate["arg1"] = instruction["arg2"]
                intermediate["arg2"] = instruction["arg3"]
                # printMemory(int(instruction["arg2"]),int(instruction["arg3"]))
            # intermediate["noop"] = True
            return intermediate
        
        else:
            print "Cannot find execute for" + str(instruction)
    else:
        return intermediate

def memory_access(intermediate):
    if not intermediate["noop"]:
        if intermediate["type"] == "memory":
            
            if intermediate["action"] == "write": 
                memory[intermediate["id"]] = intermediate["value"]
            
            elif intermediate["action"] == "print":
                printMemory(int(intermediate["arg1"]),int(intermediate["arg2"]))
            
            elif intermediate["action"] == "read":
                intermediate["value"] = memory[intermediate["value"]]
                intermediate["type"] = "register"
                intermediate["action"] = "write"

    return intermediate

def write_back(intermediate):
    if not intermediate["noop"]:
        if intermediate["type"] == "register":
            if intermediate["action"] == "write":
                register_file[intermediate["id"]] = intermediate["value"]
            elif intermediate["action"] == "print":
                printRegisterFile()

def shift(l):
    instruction = {}
    instruction["noop"] = True
    return [instruction] + l[:-1] 

def run():
    instruction = {}
    instruction["noop"] = True
   
    output = [instruction] * 5
    input = [instruction]  * 5
    print "-------------------"   
    while(True):

        # print "in"    
        # for x in input: 
        #     print x  

        output[0] = fetch()
        write_back(input[4])
        output[1] = decode(input[1])
        output[2]  = execute(input[2])
        output[3] = memory_access(input[3])
        

        if output[2]["noop"] == False:
            if output[2]["type"] == "pc":
                fetch(output[2])
                output[1] = {}
                output[1]["noop"] = True

        
        print "out"    
        for x in output: 
            print x        
       
        print "-------------------"   


        input = shift(output[:])

        if output == [instruction] * 5:
            break

run()


