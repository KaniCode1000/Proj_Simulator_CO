import re,sys

class Assembler():
    pc_multiplier = 4
    def __init__(self):
        self.register_encoding = {'zero':'00000','ra':'00001','sp':'00010','gp':'00011','tp':'00100','t0':'00101','t1':'00110','t2':'00111','s0':'01000','fp':'01000','s1':'01001','a0':'01010',
        'a1':'01011','a2': '01100', 'a3': '01101', 'a4': '01110', 'a5': '01111', 'a6': '10000', 'a7': '10001'
        ,'s2': '10010', 's3': '10011', 's4': '10100', 's5': '10101', 's6': '10110', 's7': '10111', 's8': '11000', 's9': '11001', 's10': '11010', 's11': '11011',
         't3': '11100','t4': '11101','t5': '11110','t6': '11111'}
        self.errorcame = False
        self.inp_file = None
        self.out_file = None
        self.riscv_instructions = {"R-type": {
                                        "add": {"opcode": "0110011", "funct3": "000", "funct7": "0000000"},
                                        "sub": {"opcode": "0110011", "funct3": "000", "funct7": "0100000"},
                                        "and": {"opcode": "0110011", "funct3": "111", "funct7": "0000000"},
                                        "or": {"opcode": "0110011", "funct3": "110", "funct7": "0000000"},
                                        "slt": {"opcode": "0110011", "funct3": "010", "funct7": "0000000"},
                                        "srl": {"opcode": "0110011", "funct3": "101", "funct7": "0000000"},
                                        "mul": {"opcode": "1111100", "funct3": "000","funct7": "0000000"},
                                        "rst": {"opcode": "1111101", "funct3": "000" ,"funct7": "0000000"},
                                        "halt": {"opcode": "1111110", "funct3": "000","funct7": "0000000"},
                                        "rvrs": {"opcode": "1111111", "funct3": "000","funct7": "0000000"}},
                                    "I-type": {
                                        "addi": {"opcode": "0010011", "funct3": "000"},
                                        "jalr": {"opcode": "1100111", "funct3": "000"},
                                        "lw": {"opcode": "0000011", "funct3": "010"}},

                                    "S-type":{
                                        "sw": {"opcode": "0100011", "funct3": "010"},
                                        "sh": {"opcode": "0100011", "funct3": "001"},
                                        "sb": {"opcode": "0100011", "funct3": "000"}},

                                    "B-type": {
                                        "beq": {"opcode": "1100011", "funct3": "000"},
                                        "bne": {"opcode": "1100011", "funct3": "001"}},
                                    "J-type": {
                                        "jal": {"opcode": "1101111"}}}
        # }

        self.data = None #will be updated during runtime
        self.ins_type_dict = dict()
        self.pc_multiplier = 4
        self.la = dict() #label:address key value pair

    @classmethod
    def dec_bin(cls,num,length=0):
        '''returns a binary representation of the decimal number in string format (in 2 complement representation)'''
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

    def read_file(self, filename):
        """Reads the file and extracts label addresses."""
        with open(filename,'r') as f:
            data = list(map(lambda x:x.strip(),f.readlines()))
        data = [x for x in data if x]
        tempdata = [z for z in data]
        for index,i in enumerate(tempdata):
            if ':' in i:
                labelname,instruction = i.split(':')
                data[index] = instruction
                if labelname not in self.la:
                    self.la[labelname] = self.pc_multiplier*index
                else:
                    raise Exception(f"Same label defined twice! at PC address {self.la[labelname]}")
        return data #only the set of instructions, label extracted out

    def parse_labels(self, data):
        for line in data:
            parts = line.split(':')
            if len(parts) > 2:
                with open(self.out_file,'w') as f:
                    f.write('')
                raise Exception("Multiple labels found in a single line or syntax error involving ':'")

    def find_command(self,data):
        '''Takes the data from file and checks for command'''
        command = re.split(r'[\s,]+', data.strip())[0]
        for ins_type in self.riscv_instructions:
            if command in self.riscv_instructions[ins_type].keys():
                return command,ins_type
        else:
            with open(self.out_file,'w') as f:
                f.write('')
            raise Exception("Invalid Instructions or invalid label")
    
    def update_dict(self):
        '''Maps each of the instruction types to their implementation in this class'''
        pass

    def Rtypeins(self,data):
        aux_data = re.split(r'[,\s]+',data)
        aux_data = [i for i in aux_data if i]
        command,rd,rs1,rs2 = aux_data 
        other_info = self.riscv_instructions["R-type"][command] #funct7,funct3,opcode
        try:
            return f'{other_info["funct7"]}{self.register_encoding[rs2]}{self.register_encoding[rs1]}{other_info["funct3"]}{self.register_encoding[rd]}{other_info["opcode"]}'
        except Exception as e:
            with open(self.out_file,'w') as f:
                f.write('')
            print("ERROR FOUND",e,"Invalid Register Name")
    
    def Stypeins(self, data):
        aux_data = re.split(r'[,\s()]+', data.strip())
        command = aux_data[0]
        rs2 = aux_data[1]
        imm = aux_data[2]
        rs1 = aux_data[3]
        
        other_info = self.riscv_instructions["S-type"][command]
        
        try:
            # Fix: Remove any leading zeros or non-numeric characters
            imm = imm.lstrip('0') if imm.lstrip('0') else '0'
            imm_val = self.dec_bin(int(imm),12)
            imm_upper = imm_val[0:-5].strip()
            imm_lower = imm_val[-5:].strip()


            return f'{imm_upper}{self.register_encoding[rs2]}{self.register_encoding[rs1]}{other_info["funct3"]}{imm_lower}{other_info["opcode"]}'
        except Exception as e:
            with open(self.out_file,'w') as f:
                f.write('')
            print("ERROR FOUND", e, "Invalid Register Name or Immediate")

    def Itypeins(self, data):
        aux_data = re.split(r'[\s,()]+', data.strip())

        command = aux_data[0]
        rd = aux_data[1]

        # Load instructions have offset(rs1) format
        if command in ["lw"]:
            imm = aux_data[2]  # Immediate (offset)
            rs1 = aux_data[3]  # Base register
        else:
            rs1 = aux_data[2]
            imm = aux_data[3]

        other_info = self.riscv_instructions["I-type"][command]

        try:
            imm_val = int(imm,0) if imm.startswith(('0x','0b')) else int(imm)
            imm_bin = self.dec_bin(imm_val, 12)

            return f'{imm_bin}{self.register_encoding[rs1]}{other_info["funct3"]}{self.register_encoding[rd]}{other_info["opcode"]}'
        except Exception as e:
            with open(self.out_file,'w') as f:
                f.write('')
            raise Exception(f"Invalid I-type instruction parameters: {e}")

    
    def Jtypeins(self, data, address):
        aux_data = re.split(r'[,\s()]+', data.strip())
        command = aux_data[0].strip()
        rd=aux_data[1].strip()
        imm=aux_data[2].strip()
        other_info = self.riscv_instructions["J-type"][command]
        try:
            if imm in self.la:
                imm_val = self.la[imm] - address  
            else:
                imm_val = int(imm)  
    
            imm_bin = self.dec_bin(imm_val >> 1, 20)  # Shift right by 1 for word alignment
  
            imm_final = (
                imm_bin[0] +         # imm[20] (sign bit)
                imm_bin[10:20] +     # imm[10:1]
                imm_bin[9] +         # imm[11]
                imm_bin[1:9]         # imm[19:12]
            )
    
            return f'{imm_final}{self.register_encoding[rd]}{other_info["opcode"]}'
        
        except Exception as e:
            with open(self.out_file,'w') as f:
                f.write('')
            print(f"ERROR: {e} - Invalid Register Name or Immediate")

    
    def Btypeins(self, data,address):
        aux_data = re.split(r'[,\s()]+', data.strip())
        command = aux_data[0]
        rs1 = aux_data[1]
        rs2 = aux_data[2]
        imm = aux_data[3]
        other_info = self.riscv_instructions["B-type"][command]
        try:
            if imm in self.la:
                imm_val = self.la[imm] - address 
            else:
                imm_val = int(imm) 
    
            imm_bin = self.dec_bin(imm_val >> 1, 12)  
    
            imm_final = (
                imm_bin[0] +         # imm[12] (sign bit)
                imm_bin[2:8] +       # imm[10:5]
                self.register_encoding[rs2] +
                self.register_encoding[rs1] +
                other_info["funct3"] +
                imm_bin[8:12] +      # imm[4:1]
                imm_bin[1] +         # imm[11]
                other_info["opcode"]
            )
    
            return imm_final
        
        except Exception as e:
            with open(self.out_file,'w') as f:
                f.write('')
            print(f"ERROR: {e} - Invalid Register Name or Immediate")



if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit("Usage: python pagerank.py corpus")
    filename = sys.argv[1]
    output_file = sys.argv[2]
    assembler = Assembler()
    assembler.inp_file = filename
    assembler.out_file = output_file
    assembler.data = assembler.read_file(filename)
    assembler.parse_labels(assembler.data)
    errordone = False

    with open(output_file, 'w') as out:
        for address, line in enumerate(assembler.data):
            try:
                eachpart = re.split(r'[,\s]+',line)              
                command, ins_type = assembler.find_command(line)
                if ins_type == "R-type":
                    ans = assembler.Rtypeins(line)
                elif ins_type == "S-type":
                    ans = assembler.Stypeins(line)
                elif ins_type == "I-type":
                    ans = assembler.Itypeins(line)
                elif ins_type == "B-type":
                    ans = assembler.Btypeins(line, address * Assembler.pc_multiplier)
                elif ins_type == "J-type":
                    ans = assembler.Jtypeins(line, address * Assembler.pc_multiplier)
                # if command == "beq" and len(eachpart) == 4 and eachpart[1].strip() == 'zero' and eachpart[2].strip() == 'zero' and eval(eachpart[3]) == 0 and address != len(assembler.data)-1:
                #     errordone = True
                #     print("Virtual Halt encountered. Stopping execution.\n")
                #     break
                if address == len(assembler.data) - 1:
                    if command == "beq" and len(eachpart) == 4 and eachpart[1].strip() == 'zero' and eachpart[2].strip() == 'zero' and eval(eachpart[3]) == 0:
                        pass
                    else:
                        errordone = True
                        print('Missing virtual Halt')
                        break
                out.write(ans + '\n')
            except Exception as e:
                with open(output_file,'w') as f:
                    f.write('')
                raise Exception(f"Error in line '{line}': {e}\n")
    if errordone:
        with open(output_file,'w') as f:
            f.write('')
        
