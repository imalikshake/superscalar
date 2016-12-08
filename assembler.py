import sys

# program_file = open("./fib.txt", 'r')
filename = sys.argv[1]
program_file = open(filename, 'r')

labels = {}

program = []

pc = 0

for line in program_file.readlines():

    args = line.split()

    if len(args) == 0:
        pass

    elif args[0] == '#':
        pass

    elif args[1] == ":":
        labels[args[0]] = pc

    elif args[0] == "sys":
        program.append({})
        program[pc]["opcode"] = args[0]
        program[pc]["arg1"] = args[1]
        if args[1] == 'm':
            program[pc]["arg2"] = args[2]
            program[pc]["arg3"] = args[3]
        pc = pc+1
    
    elif args[0] == "cmp":
        program.append({})
        program[pc]["opcode"] = args[0]
        program[pc]["arg1"] = args[1]
        program[pc]["arg2"] = args[2]
        program[pc]["arg3"] = args[3]
        pc = pc+1

    elif args[0] == "blth":
        program.append({})
        program[pc]["opcode"] = args[0]
        program[pc]["arg1"] = args[1]
        program[pc]["arg2"] = args[2]
        pc = pc+1

    elif args[0] == "bgth":
        program.append({})
        program[pc]["opcode"] = args[0]
        program[pc]["arg1"] = args[1]
        program[pc]["arg2"] = args[2]
        pc = pc+1

    elif args[0] == "idiv":
        program.append({})
        program[pc]["opcode"] = args[0]
        program[pc]["arg1"] = args[1]
        program[pc]["arg2"] = args[2]
        program[pc]["arg3"] = args[3]
        pc = pc+1

    elif args[0] == "imul":
        program.append({})
        program[pc]["opcode"] = args[0]
        program[pc]["arg1"] = args[1]
        program[pc]["arg2"] = args[2]
        program[pc]["arg3"] = args[3]
        pc = pc+1

    elif args[0] == "be":
        program.append({})
        program[pc]["opcode"] = args[0]
        program[pc]["arg1"] = args[1]
        program[pc]["arg2"] = args[2]
        pc = pc+1

    elif args[0] == "bgthe":
        program.append({})
        program[pc]["opcode"] = args[0]
        program[pc]["arg1"] = args[1]
        program[pc]["arg2"] = args[2]
        pc = pc+1

    elif args[0] == "blthe":
        program.append({})
        program[pc]["opcode"] = args[0]
        program[pc]["arg1"] = args[1]
        program[pc]["arg2"] = args[2]
        pc = pc+1
        
    elif args[0] == "bne":
        program.append({})
        program[pc]["opcode"] = args[0]
        program[pc]["arg1"] = args[1]
        program[pc]["arg2"] = args[2]
        pc = pc+1

    elif args[0] == "add":
        program.append({})
        program[pc]["opcode"] = args[0]
        program[pc]["arg1"] = args[1]
        program[pc]["arg2"] = args[2]
        program[pc]["arg3"] = args[3]
        pc = pc+1
 
    elif args[0] == "addi":
        program.append({})
        program[pc]["opcode"] = args[0]
        program[pc]["arg1"] = args[1]
        program[pc]["arg2"] = args[2]
        program[pc]["arg3"] = args[3]
        pc = pc+1
        
    elif args[0] == "sub":
        program.append({})
        program[pc]["opcode"] = args[0]
        program[pc]["arg1"] = args[1]
        program[pc]["arg2"] = args[2]
        program[pc]["arg3"] = args[3]
        pc = pc+1

    elif args[0] == "subi":
        program.append({})
        program[pc]["opcode"] = args[0]
        program[pc]["arg1"] = args[1]
        program[pc]["arg2"] = args[2]
        program[pc]["arg3"] = args[3]
        pc = pc+1

    elif args[0] == "ldr":
        program.append({})
        program[pc]["opcode"] = args[0]
        program[pc]["arg1"] = args[1]
        program[pc]["arg2"] = args[2]
        pc = pc+1

    elif args[0] == "ldc":
        program.append({})
        program[pc]["opcode"] = args[0]
        program[pc]["arg1"] = args[1]
        program[pc]["arg2"] = args[2]
        pc = pc+1

    elif args[0] == "sto":
        program.append({})
        program[pc]["opcode"] = args[0]
        program[pc]["arg1"] = args[1]
        program[pc]["arg2"] = args[2]
        pc = pc+1  
    
    elif args[0] == "j":
        program.append({})
        program[pc]["opcode"] = args[0]
        program[pc]["arg1"] = args[1]
        pc = pc+1  

for block in program:
    if block["opcode"] == "blth":
        block["arg2"] = 'p' + str(labels[block["arg2"]])

    elif block["opcode"] == "bgth": 
        block["arg2"] = 'p' + str(labels[block["arg2"]])

    elif block["opcode"] == "bne":
        block["arg2"] = 'p' + str(labels[block["arg2"]])

    elif block["opcode"] == "be":
        block["arg2"] = 'p' + str(labels[block["arg2"]])

    elif block["opcode"] == "bgthe":
        block["arg2"] = 'p' + str(labels[block["arg2"]])

    elif block["opcode"] == "blthe":
        block["arg2"] = 'p' + str(labels[block["arg2"]])
    
    elif block["opcode"] == "j":
        block["arg1"] = 'p' + str(labels[block["arg1"]])


# for x in program: 
#     print x
 
# print labels




         