import numpy as np
import assembler
import random

from collections import deque

scalar_size = 2
mem_unit_size = 2
alu_unit_size = 2
instructions_issued = 0
clock_cycles = 0
stalls = 0
fetch = 0
class InstructionQueue(object):
	def __init__(self):
		self.instructions = deque()
		self.buffer_size = 32

	def reset(self):
		# print "RESETTING at IQ LENGTH %d" % (len(IQ.instructions))
		self.instructions =  deque()

	def peak(self):
		# print "PEEPING at IQ LENGTH %d" % (len(IQ.instructions))
		return self.instructions[0]

	def add(self, val):
		self.instructions.append(val)

	def pop(self):
		# print "POPPING at IQ LENGTH %d" % (len(IQ.instructions))
		return self.instructions.popleft()

	def printQueue(self):
		print self.instructions


	def isEmpty(self):
		if len(self.instructions) == 0:
			return True
		else:
			return False
	def isFull(self):
		if len(self.instructions) == self.buffer_size:
			return True
		else:
			return False
class Neural_unit(object):
	def __init__(self):
		self.busy = False
		self.rs_id = 0
		self.result = 0
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
		global fetch
		for x in range(scalar_size):
			if not IQ.isFull():
				fetch += 1
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
		global fetch
		# print self.branch_flag
		if self.branch_flag == 1:
			for x in range(scalar_size):
				if not IQ.isFull():
					fetch += 1
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
					# print "$$$$$ REG_ID: %d RS_ID: %d RESULT: %d $$$$" % (i, rs_id, result)
					self.register_file.qi[i] = 0
					self.register_file.val[i] = result

	def tock(self):
		global stalls, instructions_issued
		if self.stall:
			stalls += 1

		for x in range(scalar_size):
			if not IQ.isEmpty():
				self.instruction = IQ.peak()
				self.output = {}
				self.output["noop"] = self.instruction["noop"]

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
									RESERVE[i].issued = False

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

									break
						# ALU_UNIT
						elif self.output["opcode"] in ALUinstructions:
							for i in range(RS_map["ALU"][0],RS_map["ALU"][1]):
								if RESERVE[i].busy == False:
									RESERVE[i].busy = True
									RESERVE[i].issued = False

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

									break
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
										RESERVE[i].issued = False

										RESERVE[i].opcode = self.output["opcode"]
										RESERVE[i].instruction = self.output
										issued = True
										RESERVE[i].A = self.output["arg2"]

										if self.register_file.qi[self.output["arg1"]] == 0:
											RESERVE[i].qj = 0
											RESERVE[i].vj = self.register_file.val[self.output["arg1"]]

										else:
											RESERVE[i].qj = self.register_file.qi[self.output["arg1"]]

										break

						if issued == True:
							instructions_issued += 1
							IQ.pop()

	def tick(self):
		pass
class Execute(object):
	def __init__(self):
		self.alu_unit = None
		self.mem_unit = None
		self.branch_unit = None

	def issue_mem(self):
		for i in range(RS_map["MEM"][0],RS_map["MEM"][1]):
			for x in range(mem_unit_size):
				if RESERVE[i].qj == 0 and RESERVE[i].qk == 0 and RESERVE[i].busy == True and self.mem_units[x].busy == False and RESERVE[i].issued == False:
					self.mem_units[x].busy = True
					self.mem_units[x].rs_id = i
					RESERVE[i].issued = True

					if RESERVE[i].opcode == "ldc":
						destination = RESERVE[i].d
						self.mem_units[x].result = RESERVE[i].A

					elif RESERVE[i].opcode == "sto":
						operand1 = RESERVE[i].vj
						operand2 = RESERVE[i].vk
						self.mem_units[x].result = operand2

					elif RESERVE[i].opcode == "ldr":
						operand1 = RESERVE[i].vj
						destination = RESERVE[i].d
						self.mem_units[x].result = operand1


	def issue_branch(self):
		if self.branch_unit.busy == False:
			for i in range(RS_map["BRANCH"][0],RS_map["BRANCH"][1]):
				if RESERVE[i].qj == 0 and RESERVE[i].qk == 0 and RESERVE[i].busy == True :

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
		for i in range(RS_map["ALU"][0],RS_map["ALU"][1]):
			for x in range(alu_unit_size):
				if RESERVE[i].qj == 0 and RESERVE[i].qk == 0 and RESERVE[i].busy == True and RESERVE[i].issued == False and self.alu_units[x].busy == False:
					opcode = RESERVE[i].opcode
					operand1 = RESERVE[i].vj
					operand2 = RESERVE[i].vk
					destination = RESERVE[i].instruction["arg1"]

					self.alu_units[x].rs_id = i
					self.alu_units[x].busy = True
					RESERVE[i].issued = True

					if opcode == "add":
						self.alu_units[x].result =  RESERVE[i].vj + RESERVE[i].vk
					elif opcode == "cmp":
						self.alu_units[x].result =  RESERVE[i].vj - RESERVE[i].vk
					elif opcode == "sub":
						self.alu_units[x].result =  RESERVE[i].vj - RESERVE[i].vk
					elif opcode == "subi":
						self.alu_units[x].result =  RESERVE[i].vj - RESERVE[i].A
					elif opcode == "addi":
						self.alu_units[x].result =  RESERVE[i].vj +  RESERVE[i].A
					break
					# print self.alu_unit.result

	def tock(self):
		self.issue_mem()
		self.issue_alu()
		self.issue_branch()

	def tick(self):
		for i in range(mem_unit_size):
			if self.mem_units[i].busy:
				result = {}
				result["rs_id"] = self.mem_units[i].rs_id
				result["result"] = self.mem_units[i].result
				result["unit_id"] = i
				CB.mem_results.append(result)
				# self.mem_units[x].busy = False
		for i in range(alu_unit_size):
			if self.alu_units[i].busy:
				result = {}
				result["rs_id"] = alu_units[i].rs_id
				result["result"] = alu_units[i].result
				result["unit_id"] = i
				CB.alu_results.append(result)
				# self.alu_units[x].busy = False
		if self.branch_unit.busy:
			result = {}
			result["rs_id"] = branch_unit.rs_id
			result["result"] = branch_unit.result
			CB.branch_results.append(result)

			ID.stall = False

			if result["result"] is not "noop":
				# print "BRANCHING TO" + str(result["result"])
				IF.relativeBranch(result["result"])
				IF.branch_flag = 1


	def print_units(self):
		print "EXECUTION UNITS"
		print "----------------------------------------------------------------"

		for i in range(alu_unit_size):
			print '\tALU unit %d:  \n\t\tRS id: %d, result: %f, busy: %r, opcode: %s, vj: %d, vk: %d:' % (i, self.alu_units[i].rs_id, self.alu_units[i].result, self.alu_units[i].busy, RESERVE[self.alu_units[i].rs_id].opcode, RESERVE[self.alu_units[i].rs_id].vj, RESERVE[self.alu_units[i].rs_id].vk)
			print "----------------------------------------------------------------"
		for i in range(mem_unit_size):
			print '\tMEM unit %d: \n\t\tRS id: %d, result: %f, busy: %r, opcode: %s' % (i ,self.mem_units[i].rs_id, self.mem_units[i].result, self.mem_units[i].busy, RESERVE[self.mem_units[i].rs_id].opcode)
			print "----------------------------------------------------------------"
		print '\tBRANCH unit: \n\t\tRS id: %d, result: %s, busy: %r, opcode: %s' % ( self.branch_unit.rs_id, str(self.branch_unit.result), self.branch_unit.busy, RESERVE[self.branch_unit.rs_id].opcode)

class CDB(object):
	def __init__(self):
		self.mem_results = []
		self.alu_results = []
		self.branch_results = []

class WriteBack(object):
	def __init__(self):
		pass

	def tock(self):
		while len(CB.mem_results) > 0:
			result = CB.mem_results.pop()
			rs_id =  result["rs_id"]
			unit_id = result["unit_id"]
			result = result["result"]

			# print " $$$$$$ RESULT OF MEMORY  " + str(result)

			if RESERVE[rs_id].opcode == "ldr":
				# print " $$$$$$$$$$ RETRIEVING M at " + str(result)
				result = memory[result]
				# print " $$$$$$ RETRIEVED VAL  " + str(result)
				# print " $$$$$$ UPDATING  rs_id  " + str(rs_id)

				ID.update_reg(rs_id, result)

			elif RESERVE[rs_id].opcode == "ldc":
				ID.update_reg(rs_id, result)

			elif RESERVE[rs_id].opcode == "sto":
				# print " $$$$$$$$$$$$$$ " + str(result) +" PRINTING INTO MEMORY $$$$$$$$$$$"
				# print "AT" + str(RESERVE[rs_id].vj)
				memory[RESERVE[rs_id].vj] = result

			for i in range(RS_map['ALU'][0], RS_map['BRANCH'][1]):
				if RESERVE[i].qj == rs_id:
					RESERVE[i].qj = 0
					RESERVE[i].vj = result

				if RESERVE[i].qk == rs_id:
					RESERVE[i].qk = 0
					RESERVE[i].vk = result



			RESERVE[rs_id].busy = False
			EX.mem_units[unit_id].busy = False


		while len(CB.alu_results) > 0:
			result = CB.alu_results.pop()
			rs_id =  result["rs_id"]
			unit_id = result["unit_id"]
			result = result["result"]

			for i in range(RS_map['ALU'][0], RS_map['BRANCH'][1]):
				if RESERVE[i].qj == rs_id:
					RESERVE[i].qj = 0
					RESERVE[i].vj = result

				if RESERVE[i].qk == rs_id:
					RESERVE[i].qk = 0
					RESERVE[i].vk = result

			ID.update_reg(rs_id, result)
			RESERVE[rs_id].busy = False
			EX.alu_units[unit_id].busy = False

		if len(CB.branch_results) > 0:
			result = CB.branch_results.pop()
			rs_id =  result["rs_id"]
			result = result["result"]

			EX.branch_unit.busy = False
			RESERVE[rs_id].busy = False



	def tick(self):
		pass

def print_reserve():
	print "RS"
	for i in range(len(RESERVE)):
		if i == 0:
			continue
		elif i  <= RS_map["ALU"][0] and i < RS_map["ALU"][1]:
			print "----------------------------------------------------------------"
			print "\tALU"
		elif i  == RS_map["MEM"][0]:
			print "\tMEM"
		elif i  == RS_map["BRANCH"][0]:
			print "\tBRANCH"
		print '\t\tRESERVE #%s, Op: %s, Qj: %s, Qk: %s, Vj: %s, Vk: %s, busy: %s, A: %s' % (i, RESERVE[i].opcode, RESERVE[i].qj, RESERVE[i].qk, RESERVE[i].vj, RESERVE[i].vk, RESERVE[i].busy, RESERVE[i].A)
	print "----------------------------------------------------------------"

def print_memory(fromIndex, toIndex):
	print "----------------------------------------------------------------"
	print "MEMORY"
	print "----------------------------------------------------------------"
	i = fromIndex
	for x in memory[fromIndex:toIndex]:
		print "\tm" + "[" + str(i) + "]" + ":[" + str(x) + "]"
		i = i+1
	print "----------------------------------------------------------------"

# RS_map = {"ALU":(1,2), "MEM":(2,3), "BRANCH":(3,4)}
# RESERVE = [RS() for i in range(4)]

rs_alu = 3*alu_unit_size+1
rs_mem = 2*mem_unit_size+1
RS_map = {"ALU":(1,rs_alu), "MEM":(rs_alu,rs_alu+rs_mem), "BRANCH":(rs_alu+rs_mem,rs_alu+rs_mem+1)}
RESERVE = [RS() for i in range(rs_alu+rs_mem+1)]


program = assembler.program

reg_size = 16
mem_size = 4096

clock = 0

ALUinstructions = ["add", "addi", "sub", "subi", "cmp"]
BranchInstructions = [ "blth", "blthe", "bgth", "bgthe", "bne", "be"]


memory = np.zeros(mem_size, dtype=int)

for x in range(0, 10):
	memory[x] = 10 - x

IF = Fetch()
ID = Decode()
EX = Execute()
CB = CDB()
WB = WriteBack()
IQ = InstructionQueue()

alu_units = [ALU_unit() for x in range(alu_unit_size)]
mem_units = [Memory_unit() for x in range(mem_unit_size)]
branch_unit = Branch_unit()


EX.mem_units = mem_units
EX.alu_units = alu_units
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
	print "----------------------------------------------------------------"
	print "$$$$$$$$$$ START $$$$$$$$$$$$"
	print "----------------------------------------------------------------"
	if assembler.filename == "fibonacci.asm":
		print "N is stored in R3 and the Nth fibonacci number is stored in R1."
	elif assembler.filename == "gcd.asm":
		print "N1 is stored in R0 and N2 in R4, and the GCD is stored in R1."
	ID.register_file.print_reg()
	print_memory(0,10)
	while True:
	# for x in range(500):
		i+= 1
		if IF.pc >= len(program):
			busy_mem = [not x.busy for x in EX.mem_units]
			busy_alu = [not x.busy for x in EX.alu_units]
			if all(busy_mem) and all(busy_alu) and not EX.branch_unit.busy:
				break

		clock_tick()


		# FOR DEBUG
		# print_reserve()
		# EX.print_units()
		# ID.register_file.print_reg()
		# print_memory(0,10)
		# raw_input("Press Enter to continue...")

	print "\n\n\n\n\n\n\n----------------------------------------------------------------"
	print "$$$$$$$$$$ END $$$$$$$$$$"
	ID.register_file.print_reg()
	print_memory(0,10)
	print "\n\n\n\n\n\n\n----------------------------------------------------------------"
	print "$$$$$$$$$$ RESULTS $$$$$$$$$$"
	ipc = float(instructions_issued)/float(i)
	fpc = float(fetch)/float(i)
	print "----------------------------------------------------------------"
	print "Total clock cycles: %d" % (i)
	print "Total stall cycles: %d" % (stalls)
	print "Total stall ratio: %.2f" % (float(stalls)/i)
	print "Total instructions issued: %d" % (instructions_issued)
	print "Total instructions fetched: %d" % (fetch)
	print "Fetched per cycle: %.2f" % (fpc)
	print "Issue to Fetch ration: %.2f" % (float(instructions_issued)/fetch)
	print "Instructions per cycle: %.2f" % (ipc)
	print "----------------------------------------------------------------"

run()
# ID.register_file.print_reg()
# print_memory(20,30)

# print_reserve()
