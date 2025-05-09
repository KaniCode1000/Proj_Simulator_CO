import sys

def dec_bin_u(num, length=0):
    '''unsigned dec to bin'''
    bin = format(num, 'b')
    bin = '0'*(length - len(bin)) + bin
    return bin

def dec_bin_s(num, length=1):
    if num>=0:
        return dec_bin_u(num, length)
    flip_2s = num + 2**length
    return dec_bin_u(flip_2s, length)

def dec_hex(num):
    '''Decimal to hexadecimal '''
    if not isinstance(num, int):
        raise TypeError("invalid input")

    hex_digits = '0123456789ABCDEF'
    is_negative = False
    if num < 0:
        is_negative = True
        num = (1 << 32) + num
    result = ''
    if num == 0:
        return '0'
    while num > 0:
        remainder = num % 16
        result = hex_digits[remainder] + result
        num = num // 16

    if is_negative:
        while len(result) < 8:
            result = '0' + result

    return result

def bin_dec(bin_str):
    if not all(digit in ('0', '1') for digit in bin_str):
        raise ValueError("Invalid binary string: " + bin_str)

    length = len(bin_str)
    if length == 0:
        raise ValueError("Binary string is empty")
    decimal = 0
    power = length - 1
    for i in range(length):
        decimal += int(bin_str[i]) * (2 ** power)
        power -= 1
    if bin_str[0] == '1':  # Negative number in two's complement
        decimal -= 2 ** length
    return decimal

def rvrs(val):
    """Reverses the bits of a 32-bit integer."""
    string = format(val & 0xFFFFFFFF, '032b')
    rev = string[::-1]
    return int(rev, 2)
#classes
class Simul:
    def __init__(self, data):
        self.register_values = {dec_bin_u(x, 5): 0 for x in range(0, 32)}
        self.register_values['00010'] = 380
        self.PC = 0
        self.instructions = data
        self.data_memory = {f'000{dec_hex(x)}': 0 for x in range(65536, 65536 + (32*4), 4)}
        #stack memory initialisation
        for x in range(0,381,4):
            self.data_memory[f'00000{('0'*(3-len(dec_hex(x))))+dec_hex(x)}'] = 0
        self.riscv_encoding_map = {
            ("0110011", "000", "0000000"): ("add", "R-Type"),
            ("0110011", "000", "0100000"): ("sub", "R-Type"),
            ("0110011", "111", "0000000"): ("and", "R-Type"),
            ("0110011", "110", "0000000"): ("or", "R-Type"),
            ("0110011", "010", "0000000"): ("slt", "R-Type"),
            ("0110011", "101", "0000000"): ("srl", "R-Type"),
            ("0010011", "000", None): ("addi", "I-Type"),
            ("1100111", "000", None): ("jalr", "I-Type"),
            ("0000011", "010", None): ("lw", "I-Type"),
            ("0100011", "010", None): ("sw", "S-Type"),
            ("1100011", "000", None): ("beq", "B-Type"),
            ("1100011", "001", None): ("bne", "B-Type"),
            ("1101111", None, None): ("jal", "J-Type"),
            # custom
            ("1111100", "000", "0000000"): ("mul", "Bonus-Type"), 
            ("1111101", "000", "0000000"): ("rst", "Bonus-Type"), 
            ("1111110", "000", "0000000"): ("halt", "Bonus-Type"), 
            ("1111111", "000", "0000000"): ("rvrs","Bonus-Type")  
        }

    @staticmethod
    def prep_string(string, binary=True):
        '''Prepares the binary/hexadecimal string by prepending with 0b/0x respectively'''
        if binary:
            return '0b' + string
        return '0x' + string

    @classmethod
    def load_file(cls, filename):
        '''Loads the file and returns a list of instructions'''
        with open(filename, 'r') as f:
            lines = f.readlines()
            instr = [l.strip() for l in lines if l.strip()]
            return cls(instr)

    @staticmethod
    def alu(val1, val2, funct3):
        '''ALU operations'''
        if funct3 == '000':  # add/addi
            return val1 + val2
        elif funct3 == '001':  # sub (R)
            return val1 - val2
        elif funct3 == '111':  # and/andi
            return val1 & val2
        elif funct3 == '110':  # or/ori
            return val1 | val2
        elif funct3 == '101':  # srl/srli
            return val1 >> val2
        elif funct3 == '010':  # slt/slti
            return 1 if val1 < val2 else 0
        else:
            raise ValueError(f"wrong f3: {funct3}")

    def printrow(self, filename):
        '''Writes the final state of registers'''
        pc = Simul.prep_string(dec_bin_u(self.PC, 32))
        col = pc + ' '
        for reg in range(32):
            reg_name = dec_bin_u(reg, 5)
            reg_val = self.register_values[reg_name]
            reg_str = Simul.prep_string(dec_bin_s(reg_val, 32))
            col += reg_str + ' '
        with open(filename, 'a') as f:
            f.write(col + '\n')

    def test_printrow(self, filename):
        pc = self.PC
        col = str(pc) + ' '
        for reg in range(32):
            reg_name = dec_bin_u(reg, 5)
            reg_val = self.register_values[reg_name]
            col += str(reg_val) + ' '
        with open(filename, 'a') as f:
            f.write(col + '\n')

    def write_data_memory(self, filename):
        '''Writes the final state of complete data memory'''
        with open(filename, 'a') as f:
            for x in range(65536, 65536 + (32*4), 4):
                addr = f'000{dec_hex(x)}'
                val = self.data_memory[addr]
                hex_addr = Simul.prep_string(addr, binary=False)
                final_val = Simul.prep_string(dec_bin_s(val, 32))
                f.write(hex_addr + ':' + final_val + '\n')

    def write_test_data_memory(self, filename):
        '''Writes final state of complete data memory in readable format'''
        with open(filename, 'a') as f:
            for x in range(65536, 65536 + (32*4), 4):
                addr = f'000{dec_hex(x)}'
                val = self.data_memory[addr]
                hex_addr = Simul.prep_string(addr, binary=False)
                f.write(hex_addr + ':' + str(val) + '\n')

    def instr_type(self, instr_ip):
        '''Returns a tuple with (instruction_name,instruction_type)'''
        opcode = instr_ip[-7:]
        funct3 = instr_ip[-15:-12] if len(instr_ip) >= 15 else None
        funct7 = instr_ip[0:7] if len(instr_ip) >= 32 else None

        if (opcode, funct3, funct7) in self.riscv_encoding_map:
            return self.riscv_encoding_map[(opcode, funct3, funct7)]
        
        elif (opcode, funct3, None) in self.riscv_encoding_map:
            return self.riscv_encoding_map[(opcode, funct3, None)]
        
        elif (opcode, None, None) in self.riscv_encoding_map:
            return self.riscv_encoding_map[(opcode, None, None)]
        else:
            raise ValueError(f"Invalid instruction: opcode={opcode}, funct3={funct3}, funct7={funct7}")

    def execute(self, instr):
        try:
            instr_name, instr_type = self.instr_type(instr)
            
            #bonus
            if instr_type == "Bonus-Type":
                if instr_name=='mul':
                    rd = instr[20:25]
                    rs1 = instr[12:17]
                    rs2 = instr[7:12]
                    self.register_values[rd] = self.register_values[rs1] * self.register_values[rs2]
                    self.PC += 4
            
                elif instr_name == "rst":
                    for reg in self.register_values:
                        if reg != '00010':  
                            self.register_values[reg] = 0
                    self.PC += 4
            
                elif instr_name == "halt":
                    return "terminate"
            
                elif instr_name == "rvrs":
                    register = instr[20:25]  
                    self.register_values[register] = rvrs(self.register_values[register])
                    self.PC += 4
            
            # Standard
            elif instr_type == 'R-Type':
                funct7 = instr[0:7]
                rs2 = instr[7:12]
                rs1 = instr[12:17]
                funct3 = instr[17:20]
                rd = instr[20:25]

                rs1_val = self.register_values[rs1]
                rs2_val = self.register_values[rs2]

                if funct7 == '0100000' and funct3 == '000':  # sub
                    result = rs1_val - rs2_val
                else:
                    result = self.alu(rs1_val, rs2_val, funct3)

                if rd != '00000':
                    self.register_values[rd] = result

                self.PC += 4

            elif instr_type == 'I-Type':
                imm_val = instr[0:12]
                rs1 = instr[12:17]
                funct3 = instr[17:20]
                rd = instr[20:25]

                if instr_name == 'lw':
                    # Sign extend the immediate value
                    imm_dec = bin_dec(imm_val)
                    addr = f'000{dec_hex(self.register_values[rs1] + imm_dec)}'
                    if addr not in self.data_memory:
                        value = imm_dec + self.register_values[rs1]
                        if value not in range(0,381):
                            print(value)
                            raise Exception('Invalid Memory Access')
                    self.register_values[rd] = self.data_memory[addr]
                    self.PC += 4

                elif instr_name == 'jalr':
                    if rd != '00000':
                        self.register_values[rd] = self.PC + 4
                    imm_dec = bin_dec(imm_val)
                    self.PC = (self.register_values[rs1] + imm_dec)
                    self.PC //= 2
                    self.PC *= 2

                elif instr_name == 'addi':
                    imm_dec = bin_dec(imm_val)
                    self.register_values[rd] = self.alu(self.register_values[rs1], imm_dec, funct3)
                    self.PC += 4

                else:
                    raise ValueError(f"Unsupported I-Type instruction: {instr_name}")

            elif instr_type == 'S-Type':
                imm_val = instr[0:7] + instr[20:25]
                rs1 = instr[12:17]
                rs2 = instr[7:12]

                # Sign extend the immediate value
                imm_dec = bin_dec(imm_val)
                addr = self.register_values[rs1] + imm_dec
                addr_hex = f'000{dec_hex(addr)}'
                if addr_hex not in self.data_memory:
                        if addr not in range(0,381):
                            raise Exception('Invalid Memory Access')

                self.data_memory[addr_hex] = self.register_values[rs2]

                self.PC += 4

            elif instr_type == 'B-Type':
                imm_val = instr[0] + instr[24] + instr[1:7] + instr[20:24] + '0'
                rs1 = instr[12:17]
                rs2 = instr[7:12]

                # Sign extend the immediate value
                imm_dec = bin_dec(imm_val)

                if instr_name == 'beq':
                    if self.register_values[rs1] == self.register_values[rs2]:
                        self.PC += imm_dec
                    else:
                        self.PC += 4

                elif instr_name == 'bne':
                    if self.register_values[rs1] != self.register_values[rs2]:
                        self.PC += imm_dec
                    else:
                        self.PC += 4

                if imm_dec == 0:
                    return "terminate"

            elif instr_type == 'J-Type':
                imm_val = instr[0] + instr[12:20] + instr[11] + instr[1:11] + '0'
                rd = instr[20:25]
                imm_dec = bin_dec(imm_val)
                if rd != '00000':
                    self.register_values[rd] = self.PC + 4

                self.PC += imm_dec
                self.PC //= 2
                self.PC *= 2

            else:
                raise ValueError(f"Unsupported instruction type: {instr_type}")
    
            
        except Exception as e:
            raise Exception(f"Error executing instruction {instr}: {str(e)}")


def main(input_file, output_file, output_readable_file):
    try:
        sim = Simul.load_file(input_file)
        with open(output_file, 'w') as f:
            f.write('')
        with open(output_readable_file, 'w') as f:
            f.write('')

        while sim.PC < len(sim.instructions) * 4:
            current_instr = sim.instructions[(sim.PC // 4)]
            terminate = sim.execute(current_instr)
            sim.register_values['00000'] = 0
            if terminate == "terminate":
                break

            sim.printrow(output_file)
            sim.test_printrow(output_readable_file)

        sim.printrow(output_file)
        sim.test_printrow(output_readable_file)
        sim.write_data_memory(output_file)
        sim.write_test_data_memory(output_readable_file)

    except Exception as e:
        print(f"Error in simulation: {str(e)}")


if __name__ == '__main__':
    input_file = None
    output_file = None
    output_readable_file = None
    if len(sys.argv) == 1:
        input_file = 'input.txt'
        output_file = 'output.txt'
        output_readable_file = 'output_r.txt'
    elif len(sys.argv) == 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        output_readable_file = output_file[0:-4]+'_r.txt'
    elif len(sys.argv) == 4:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        output_readable_file = sys.argv[3]
    else:
        print("Usage: python r5_test.py [input_file output_file]")
        sys.exit(1)

    main(input_file, output_file, output_readable_file)
