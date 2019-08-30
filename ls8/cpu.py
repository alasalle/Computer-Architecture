"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
ADD = 0b10100000
POP = 0b01000110
PUSH = 0b01000101
CALL = 0b01010000
RET  = 0b00010001
JMP  = 0b01010100

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[7] = 0xF4
        self.sp = self.reg[7]
        self.program_length = 0
        self.dispatch_table = {}
        self.dispatch_table[LDI] = self.handle_LDI
        self.dispatch_table[PRN] = self.handle_PRN
        self.dispatch_table[MUL] = self.handle_MUL
        self.dispatch_table[ADD] = self.handle_ADD
        self.dispatch_table[HLT] = self.handle_HLT
        self.dispatch_table[POP] = self.handle_POP
        self.dispatch_table[PUSH] = self.handle_PUSH
        self.dispatch_table[CALL] = self.handle_CALL
        self.dispatch_table[RET] = self.handle_RET
        self.dispatch_table[JMP] = self.handle_JMP
        self.alu_dispatch_table = {}
        self.alu_dispatch_table['ADD'] = self.alu_ADD
        self.alu_dispatch_table['MUL'] = self.alu_MUL
        self.running = True
        self.pc = 0

    def handle_LDI(self, OP_A, OP_B, OP):
        self.reg[OP_A] = OP_B
        self.pc += ((0b11000000 & OP) >> 6) + 1

    def handle_PRN(self, OP_A, OP_B, OP):
        print(self.reg[OP_A])
        self.pc += ((0b11000000 & OP) >> 6) + 1


    def handle_ADD(self, OP_A, OP_B, OP):
        self.alu('ADD', OP_A, OP_B)
        self.pc += ((0b11000000 & OP) >> 6) + 1

    def handle_MUL(self, OP_A, OP_B, OP):
        self.alu('MUL', OP_A, OP_B)
        self.pc += ((0b11000000 & OP) >> 6) + 1


    def handle_HLT(self, OP_A, OP_B, OP):
        self.running = False

    def handle_POP(self, OP_A, OP_B, OP):

        self.reg[OP_A] = self.ram[self.reg[7]]

        if (self.reg[7] + 1) % 0xF5 > self.program_length -1:

            self.reg[7] = (self.reg[7] + 1) % 0xF5

        else:

            self.reg[7] = self.program_length
        
        self.pc += ((0b11000000 & OP) >> 6) + 1



    def handle_PUSH(self, OP_A, OP_B, OP):

        if (self.reg[7] - 1) % 0xF5 > self.program_length - 1:

            self.reg[7] = (self.reg[7] - 1) % 0xF5 

        else:

            self.reg[7] = self.program_length

        self.ram[self.reg[7]] = self.reg[OP_A]
        self.pc += ((0b11000000 & OP) >> 6) + 1


    def handle_CALL(self, OP_A, OP_B, OP):

        self.ram[self.reg[7]] = self.pc + 2
        self.reg[7] -= 1
        self.pc = self.reg[OP_A]

    def handle_RET(self, OP_A, OP_B, OP):
        
        self.reg[7] += 1
        self.pc = self.ram[self.reg[7]]

    def handle_JMP(self, OP_A, OP_B, OP):
        print({'a': OP_A, 'reg': self.reg, 'ram': self.ram})
        self.pc = self.reg[OP_A]

    def alu_ADD(self, reg_a, reg_b):
        self.reg[reg_a] = (self.reg[reg_a] + self.reg[reg_b]) & 0xFF

    def alu_MUL(self, reg_a, reg_b):
        self.reg[reg_a] = (self.reg[reg_a] * self.reg[reg_b]) & 0xFF


    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def load(self):
        """Load a program into memory."""

        address = 0

        program = []

        try:

            with open(sys.argv[1]) as b:
                for line in b:
                    if line.startswith('0') | line.startswith('1'):
                        l = line.split('#')[0].strip()
                        number = int(l, 2)
                        program.append(number)

            for instruction in program:
                self.ram[address] = instruction
                address += 1
        
            self.program_length = address

        except:
            print("Oops!",sys.exc_info()[0],"occured in load function.")
            sys.exit(1)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        try:

            self.alu_dispatch_table[op](reg_a, reg_b)

        except:

            print("Oops!",sys.exc_info()[0],"occured in alu function.")
            sys.exit(1)


    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        while self.running:

            # try:

                IR = self.ram[self.pc]

                OP_A = self.ram_read(self.pc + 1)
                OP_B = self.ram_read(self.pc + 2)


                self.dispatch_table[IR](OP_A, OP_B, IR)
            
            # except:

            #     print("Oops!",sys.exc_info()[0],"occured in run function.")
            #     sys.exit(1)
