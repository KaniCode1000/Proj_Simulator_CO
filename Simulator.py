#modules

#functions
def dec_bin(num,length=0):
        '''returns a binary representation of the decimal number in string format (in 2 complement representation)
        can perform sign extension as well'''
        string = ''
        msb = '0' if num >= 0 else '1'
        length -= 1
        num = abs(num)
        while num!=0:
            bit = num&1
            string += str(bit)
            num >>= 1
        if length != 0:
            string += '0'*(length-len(string))
        string = string[::-1]
        if msb == '1':
            newstring = ''
            first = False
            for i in range(length-1,-1,-1): #length -1 to 0
                if not first:
                    newstring += string[i]
                    first = True if string[i] == '1' else False
                else:
                    newstring += '1' if string[i] == '0' else '0'                
            string = newstring[::-1]
        return msb + string

def dec_hex(num):
    '''Decimal to hexadecimal conversion'''
    if num == 0:
        return '0'
    hex_digits = '0123456789abcdef'
    is_negative = False
    if num < 0:
        is_negative = True
        num = -num
    
    result = ''
    
    while num > 0:
        remainder = num % 16
        result = hex_digits[remainder] + result
        num = num // 16
    
    if is_negative:
        result = '-' + result
    
    return result[2:]
    #return hex(num)[2:]

def bin_dec(bin_str):
    '''Binary to decimal conversion'''
    decimal = 0
    power = len(binary_str) - 1 
    for digit in binary_str:
        if digit not in ('0', '1'):
            raise ValueError("Invalid binary digit: " + digit)
        
        decimal += int(digit) * (2 ** power)
        power -= 1
    return int('0b'+decimal ,2)

def hex_dec(hex_str):
    '''Hexadecimal to decimal conversion'''
    hex_str = hex_str.lower()
    decimal = 0
    hex_digits = '0123456789abcdef'
    power = len(hex_str) - 1     
    for char in hex_str:
        if char not in hex_digits:
            raise ValueError("Invalid hexadecimal digit: " + char)
        if char.isdigit():
            digit_value = int(char)
        else: 
            digit_value = 10 + ord(char) - ord('a')
        decimal += digit_value * (16 ** power)
        power -= 1 
    return int('0x'+decimal ,16)

#classes
class Simul():
    def __init__(self,data):
        self.register_values = {dec_bin(x,5):0 for x in range(0,32)} #dictionary of binary_names:values stored
        self.PC = 0
        self.instructions = data #list of all lines
        self.data_memory = {f'000{dec_hex(x)}':0 for x in range(65536,65536+32)} #starts from 65536 as per test cases
        self.riscv_encoding_map = {
                                ("0110011", "000", "0000000"): ("add","R-Type"),
                                ("0110011", "000", "0100000"): ("sub","R-Type"),
                                ("0110011", "111", "0000000"): ("and","R-Type"),
                                ("0110011", "110", "0000000"): ("or","R-Type"),
                                ("0110011", "010", "0000000"): ("slt","R-Type"),
                                ("0110011", "101", "0000000"): ("srl","R-Type"),
                                ("0010011", "000", None): ("addi","I-Type"),
                                ("1100111", "000", None): ("jalr","I-Type"),
                                ("0000011", "010", None): ("lw","I-Type"),
                                ("0100011", "010", None): ("sw","S-Type"),
                                ("1100011", "000", None): ("beq","B-Type"),
                                ("1100011", "001", None): ("bne","B-Type"),
                                ("1101111", None, None): ("jal","J-Type")
                            }
    
    @staticmethod
    def prep_string(string,binary=True):
        '''Prepares the binary/hexadecimal string by prepending with 0b/0x respectively'''
        if binary:
            return '0b'+string
        return '0x'+string

    @classmethod
    def load_file(cls,filename):
        '''Loads the file and simple returns a list of instructions (data)'''
        with open(filename,'r') as f:
            data = [x for x in f.readlines() if x.strip() != '']
        return cls(data)

    @staticmethod
    def alu(val1,val2,funct3):
        '''mimics the operation of alu, give it funct3 and values and it will return the value after performing the corresponding operation!'''
        funcs = {'000':lambda x,y:x+y,'001':lambda x,y:x-y,'010':lambda x,y:x&y,'011':lambda x,y:x|y,'101':lambda x,y:1 if x<y else 0}
        return funcs[funct3](val1,val2)

    def writeall(self,filename):
        '''Writes the final state of registers (to be called after every instruction execution)'''
        string = Simul.prep_string(dec_bin(self.PC,length=32))+' '
        with open(filename,'a') as f:
            for x in range(0,32):
                string += Simul.prep_string(dec_bin(self.register_values[dec_bin(x,5)],32))+' '
            f.write(string + '\n')

    def write_data_memory(self,filename):
        '''Writes the final state of complete data memory'''
        with open(filename,'a') as f:
            for key in self.data_memory:
                string = f'{Simul.prep_string(key,binary = False)}: {Simul.prep_string(dec_bin(self.data_memory[key],32))}'
                f.write(string + '\n')

    def instr_type(self,instr_bin):
        '''Returns a tuple with (instruction_name,instruction_type)'''
        keys = list(self.riscv_encoding_map.keys())
        opcode = instr_bin[-7:]
        funct3 = intsr_bin[-15:-12]
        funct7 = instr_bin[0:7]
        if (opcode,funct3,funct7) in keys:
            return self.riscv_encoding_map[(opcode,funct3,funct7)]
        elif (opcode,funct3,funct7) in keys:
            return self.riscv_encoding_map[(opcode,funct3,None)]
        elif (opcode,None,None) in keys:
            return self.riscv_encoding_map[(opcode,None,None)]
        else:
            raise Exception("Incorrect/ Invalid Instruction")
    
    def execute(self,instr): #TODO
        '''Input: Binary instruction
        Does: Executes the instruction'''
        try:
            instr_data = self.instr_type(instr) #tuple of format (instruction_name,instruction_type)

            if instr_data[1] == 'R-type': #perform corresponding alu operation, write value in rd
                rs2,rs1 = instr[7:12],instr[12:17]
                funct3 = instr[17:20]
                rd = instr[20:25]
                if instr_data[0] == 'sub':
                    funct3 = '001'
                #update the rd register with the corresponding value from rs1 and rs2 and perform the function using alu
                self.register_values[rd] = Simul.alu(self.register_values[rs1],self.register_values[rs2],funct3)
            
            elif instr_data[1] == 'I-type':
                imm_val = instr[0:12]
                rs1 = instr[12:17]
                funct3 = instr[17:20]
                rd = instr[20:25]
                if instr_data[0] == 'lw':
                    self.register_values[rd] = self.data_memory[f'000{65536+self.register_values[rs1]+bin_dec(imm_val)}']
                elif instr_data[0] == 'jalr':
                    self.register_values[rd] = Simul.alu(self.PC,4,funct3) #stores PC+4 to rd field
                    self.PC += bin_dec(imm_val) #updates pc value
                else:
                    self.register_values[rd] = Simul.alu(self.register_values[rs1],bin_dec(imm),funct3) #updates rd with imm+rs1

            elif instr_data[1] == 'S-Type':
                imm_val = instr[0:7] + instr[20:25]  # imm[11:5] + imm[4:0]
                rs1 = instr[12:17]
                rs2 = instr[7:12]
                addr = (65536 + self.register_values[rs1] + bin_dec(imm_val)) & 0xFFFFFFFC
                addr_hex = f'000{dec_hex(addr)}'
                self.data_memory[addr_hex] = self.register_values[rs2]

            elif instr_data[1] == 'B-Type':
                            imm_val = instr[0] + instr[24] + instr[1:7] + instr[20:24] + '0'
                            rs1 = instr[12:17]
                            rs2 = instr[7:12]
                            if instr_data[0] == 'beq' and self.register_values[rs1] == self.register_values[rs2]:
                                self.PC += bin_dec(imm_val)
                            elif instr_data[0] == 'bne' and self.register_values[rs1] != self.register_values[rs2]:
                                self.PC += bin_dec(imm_val)
            elif instr_data[1] == 'J-Type':
                            imm_val = instr[0] + instr[12:20] + instr[11] + instr[1:11] + '0'
                            rd = instr[20:25]
                            self.register_values[rd] = self.PC + 4
                            self.PC += bin_dec(imm_val)


        

            '''TODO implement S,B,J type instructions...REMEMBER THAT S type instruction loads FROM MEMORY (IMPLEMENTED USING HEX AS KEYS)'''

       # except: #TODO the implementation for exception handling
        except KeyError:
            # Handle invalid register or memory access
            print(f"Error: Invalid register or memory access in instruction: {instr}")
            raise

        except ValueError:
            # Handle invalid immediate values or conversions
            print(f"Error: Invalid value in instruction: {instr}")
            raise

        except Exception as e:
            # Handle any other unexpected errors
            print(f"Unexpected error executing instruction {instr}: {str(e)}")
            print(f"PC: {self.PC}, Instruction Type: {instr_data if 'instr_data' in locals() else 'Unknown'}")
            raise

#main 
if __name__ == '__main__':
    inp_filename = None #TODO
    out_filename = None #TODO
    sim = Simul.load_file(filename)

    #preprocessing
    with open(out_filename,'w') as f:
        f.write('')

    #actual implementation
    for instr in sim.instructions:
        sim.writeall(out_filename)

    #writing data memory part TODO
