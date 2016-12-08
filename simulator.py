import numpy as np
import assembler
import random

program = assembler.program



register_file = np.zeros(16, dtype=int)
memory = np.zeros(100, dtype=int)

# for x in range(20, 30):
#     memory[x] = 30 - x

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


def fetch():
    global pc
    instruction = program[pc]
    pc+=1

    return instruction

def decode(instruction):
    
    decoded = {}
    decoded["opcode"] = instruction["opcode"]
    # print str(instruction["opcode"])
    
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
    value = None;
    type = None;
    id = None;
    
    if instruction["opcode"] == "add" :
        intermediate["value"] = register_file[instruction["arg2"]] + register_file[instruction["arg3"]]
        intermediate["type"] = "register"
        intermediate["id"] = instruction["arg1"]
        return intermediate
    
    elif instruction["opcode"] == "addi": 
        intermediate["value"] = register_file[instruction["arg2"]] + instruction["arg3"]
        intermediate["type"] = "register"
        intermediate["id"] = instruction["arg1"]
        return intermediate
        
    elif instruction["opcode"] == "blth":
        if register_file[instruction["arg1"]] < 0:
            intermediate["type"] = "pc"
            intermediate["value"] = instruction["arg2"]
        else :
            intermediate["type"] = "noop"
        return intermediate
    
    elif instruction["opcode"] == "be":
        if register_file[instruction["arg1"]] == 0:
            intermediate["type"] = "pc"
            intermediate["value"] = instruction["arg2"]
        else :
            intermediate["type"] = "noop"
        return intermediate
    
    elif instruction["opcode"] == "bgth":
        if register_file[instruction["arg1"]] > 0:
            intermediate["type"] = "pc"
            intermediate["value"] = instruction["arg2"]
        else :
            intermediate["type"] = "noop"
        return intermediate
    
    elif instruction["opcode"] == "blthe":
        if register_file[instruction["arg1"]] <= 0:
            intermediate["type"] = "pc"
            intermediate["value"] = instruction["arg2"]
        else :
            intermediate["type"] = "noop"
        return intermediate
    
    elif instruction["opcode"] == "bgthe":
        if register_file[instruction["arg1"]] >= 0:
            intermediate["type"] = "pc"
            intermediate["value"] = instruction["arg2"]
        else :
            intermediate["type"] = "noop"
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
            intermediate["type"] = "noop"
        return intermediate

    elif instruction["opcode"] == "sub" :
        intermediate["value"] = register_file[instruction["arg2"]] - register_file[instruction["arg3"]]
        intermediate["type"] = "register"
        intermediate["id"] = instruction["arg1"]
        return intermediate
        
    # elif instruction["opcode"] == "idiv" :
    #     intermediate["value"] = int(register_file[instruction["arg2"]] / register_file[instruction["arg3"]])
    #     intermediate["type"] = "register"
    #     intermediate["id"] = instruction["arg1"]
    #     return intermediate

    # elif instruction["opcode"] == "imul" :
    #     intermediate["value"] = int(register_file[instruction["arg2"]] * register_file[instruction["arg3"]])
    #     intermediate["type"] = "register"
    #     intermediate["id"] = instruction["arg1"]
    #     return intermediate
        
    elif instruction["opcode"] == "subi" :
        intermediate["value"] = register_file[instruction["arg2"]] - instruction["arg3"]
        intermediate["type"] = "register"
        intermediate["id"] = instruction["arg1"]
        return intermediate   
    
    elif instruction["opcode"] == "ldc" :
        intermediate["type"] = "register"
        intermediate["id"] = instruction["arg1"]
        intermediate["value"] = instruction["arg2"]
        return intermediate

    elif instruction["opcode"] == "ldr" :
        intermediate["type"] = "register"
        intermediate["id"] = instruction["arg1"]
        intermediate["value"] = memory[register_file[instruction["arg2"]]]
        return intermediate

    elif instruction["opcode"] == "sto" :
        intermediate["type"] = "memory"
        intermediate["id"] = register_file[instruction["arg1"]]
        intermediate["value"] = register_file[instruction["arg2"]]
        return intermediate

    elif instruction["opcode"] == "sys" :
        if instruction["arg1"] == 'r':
            printRegisterFile()
        elif instruction["arg1"] == 'm':
            printMemory(int(instruction["arg2"]),int(instruction["arg3"]))
        intermediate["type"] = "noop"
        return intermediate
    
    elif instruction["opcode"] == "cmp" :
        value = register_file[instruction["arg2"]] - register_file[instruction["arg3"]]
        compare = None;
        if value > 0 : compare = 1
        elif value == 0 : compare = 0
        elif value < 0 : compare = -1
        intermediate["type"] = "register"
        intermediate["id"] = instruction["arg1"]
        intermediate["value"] = compare
        return intermediate
    
    else:
        print "Cannot find execute for" + str(instruction)
       

def write_back(intermediate):
    global pc
    # print intermediate
    if intermediate["type"] == "memory":
        memory[intermediate["id"]] = intermediate["value"]
    
    elif intermediate["type"] == "register":
        register_file[intermediate["id"]] = intermediate["value"]
    
    elif intermediate["type"] == "pc":
        pc = intermediate["value"]

    elif intermediate["type"] == "noop":
        pass

def run():
    while(True):
        instruction = fetch()
        instruction = decode(instruction)
        # print instruction
        intermediate  = execute(instruction)
        # print intermediate
        write_back(intermediate)
        if pc >= len(program):
            break

run()


