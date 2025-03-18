#modules

#functions
def dec_bin(num,length=0):
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

#classes
class Simul():
    def __init__(self,data):
        self.register_values = [{dec_bin(x,5):0 for x in range(0,32)}]
        self.PC = 0
        self.instructions = data #list of all lines
    
    @staticmethod
    def prep_string(string,bin=True):
        if bin:
            return '0b'+string
        return '0x'+string

    @classmethod
    def load_file(cls,filename):
        with open(filename,'r') as f:
            data = [x for x in f.readlines() if x.strip() != '']
        return cls(data)

    @staticmethod
    def mux(data,*selectors):
        value = 0
        counter = 1
        for s in selectors:
            value += counter*s
            counter *= 2
        return data[value]

    @staticmethod
    def alu(val1,val2,alucontrol):
        funcs = {'000':lambda x,y:x+y,'001':lambda x,y:x-y,'010':lambda x,y:x&y,'011':lambda x,y:x|y,'101':lambda x,y:1 if x<y else 0}
        return functs[alucontrol](val1,val2)

    def writeall(self,filename):
        string = Simul.prep_string(dec_bin(self.PC,length=32))+' '
        with open(filename,'a') as f:
            for x in range(0,32):
                string += Simul.prep_string(dec_bin(self.register_values[self.dec_bin(x,5)],32))+' '
            f.write(string + '\n')


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