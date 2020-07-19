import hashlib
class block:
    def __init__(self, block_body=None, block_header=None):
        self.block_body = block_body #block body object
        self.block_header = block_header #block header object
    
    def block_bytearray(self):
        return self.block_header.header_bytearray() + self.block_body.body

    def block_from_bytearray(self,bytestream):
        index = int.from_bytes(bytestream[:4],byteorder='big')
        parent_block_hash = bytestream[4:36]
        block_body_hash = bytestream[36:68]
        target_value = bytestream[68:100]
        timestamp = int.from_bytes(bytestream[100:108],byteorder='big')
        nonce = int.from_bytes(bytestream[108:116],byteorder='big')
        self.block_header = block_header(index,parent_block_hash,block_body_hash,target_value,timestamp,nonce)
        self.block_body = block_body(bytestream[116:])
        return None

    def export_to_file(self):
        f = open(self.block_header.index + '.dat', 'w+b')
        f.write(self.block_bytearray())
        f.close()
        return None

    def block_from_file(self, index):
        f = open(index + '.dat','rb')
        block_from_bytearray(f.read())
        f.close()
        return None


class block_body:
    def __init__(self, body):
        self.body = body #assuming body is a bytearray
        self.no_of_trans = int.from_bytes(body[:4],byteorder='big')
        counter = 4
        self.transaction_list = [] #list of transaction objects
        for i in range(0,self.no_of_trans):
            x = int.from_bytes(body[counter:counter+4],byteorder='big')
            counter += 4
            transaction_object = transaction_class()
            transaction_object.transactionFromByteArray(body[counter:counter+x])
            counter += x
            self.transaction_list.append(transaction_object)
            

    def calc_hash(self):
        #taking SHA256 hash of the bytearray
        result = hashlib.sha256(self.body)
        return result.hexdigest()

class block_header:
    def __init__(self, index, parent_block_hash, block_body_hash, target_value, timestamp, nonce):
        self.index = index
        self.parent_block_hash = parent_block_hash
        self.block_body_hash = block_body_hash
        self.target_value = target_value
        self.timestamp = timestamp
        self.nonce = nonce
    
    def header_bytearray(self):
        finalbytes = bytearray()
        
        #creating bytearray 
        finalbytes.extend((self.index).to_bytes(4,'big'))
        finalbytes.extend(bytearray.fromhex(self.parent_block_hash))
        finalbytes.extend(bytearray.fromhex(self.block_body_hash))
        finalbytes.extend(bytearray.fromhex(self.target_value))
        finalbytes.extend((self.timestamp).to_bytes(8,'big'))
        finalbytes.extend((self.nonce).to_bytes(8,'big'))

        return finalbytes

    def calc_hash(self):
        finalbytes =  self.header_bytearray()
        
        #taking SHA256 hash of the bytearray
        result = hashlib.sha256(finalbytes)
        return result.hexdigest()

#input class
class input_class:
    def __init__(self, transID, index, sign):
        self.transID = transID
        self.index = index
        self.len_of_sign =  int((len(sign))/2) #a hex string has two characters per byte
        self.sign = sign

#output class
class output_class:
    def __init__(self, no_of_coins, public_key):
        self.no_of_coins = no_of_coins
        self.len_of_pubkey = len(public_key)
        self.public_key = public_key
        
#transaction class
class transaction_class:
    def __init__(self, no_of_inputs=None, array_of_inputs=None, no_of_outputs=None, array_of_outputs=None):
        self.no_of_inputs = no_of_inputs
        self.array_of_inputs = array_of_inputs
        self.no_of_outputs = no_of_outputs
        self.array_of_outputs = array_of_outputs
        try:
            self.transID = self.calc_hash()
        except: 
            self.transID = None
        self.bytestream = None
    
    def calc_hash(self):
        finalbytes =  self.transactionToByteArray()
        #taking SHA256 hash of the bytearray
        result = hashlib.sha256(finalbytes)
        return result.hexdigest()

    def transactionToByteArray(self):
        no_of_inputs = self.no_of_inputs
        array_of_inputs = self.array_of_inputs
        no_of_outputs = self.no_of_outputs
        array_of_outputs = self.array_of_outputs
        finalbytes = bytearray()
    
        #no of inputs- 4 bytes
        finalbytes.extend(no_of_inputs.to_bytes(4, 'big'))
    
        #adding input data
        for i in range(0,no_of_inputs):
            input_obj = array_of_inputs[i]
            #finalbytes.extend(bytearray.fromhex(input_obj.transID[2:]))
            finalbytes.extend(bytearray.fromhex(input_obj.transID))
            finalbytes.extend((input_obj.index).to_bytes(4,'big'))
            finalbytes.extend((input_obj.len_of_sign).to_bytes(4,'big'))
            #finalbytes.extend(bytearray.fromhex(input_obj.sign[2:]))
            finalbytes.extend(bytearray.fromhex(input_obj.sign))
            
        
        #no of outputs- 4 bytes
        finalbytes.extend(no_of_outputs.to_bytes(4, 'big'))

        #adding output data 
        for i in range(0,no_of_outputs):
            output_obj = array_of_outputs[i]
            finalbytes.extend((output_obj.no_of_coins).to_bytes(8,'big'))
            finalbytes.extend((output_obj.len_of_pubkey).to_bytes(4,'big'))
            finalbytes.extend((output_obj.public_key).encode())
        return finalbytes
    
    def transactionFromByteArray(self, bytestream):    
        #no of inputs
        self.no_of_inputs = int.from_bytes(bytestream[:4], "big")
        counter = 4
        #input data
        self.array_of_inputs = []
        for i in range(0,self.no_of_inputs):
            transID = (hex(int.from_bytes(bytestream[counter:counter+32],'big'))[2:]).zfill(64)
            counter += 32
            index = int.from_bytes(bytestream[counter:counter+4], "big")
            counter += 4
            len_of_sign = int.from_bytes(bytestream[counter:counter+4], "big")
            counter += 4
            sign = (hex(int.from_bytes(bytestream[counter:counter+len_of_sign],'big'))[2:]).zfill(len_of_sign)
            counter += len_of_sign
            self.array_of_inputs.append(input_class(transID,index,sign))
        
        #no. of outputs
        self.no_of_outputs = int.from_bytes(bytestream[counter:counter+4], "big")
        counter += 4

        #output data
        self.array_of_outputs = []
        for i in range(0,self.no_of_outputs):
            no_of_coins = int.from_bytes(bytestream[counter:counter+8], "big")
            counter += 8
            len_of_pubkey = int.from_bytes(bytestream[counter:counter+4], "big")
            counter += 4
            public_key = bytestream[counter:counter+len_of_pubkey].decode('utf-8')
            counter += len_of_pubkey
            self.array_of_outputs.append(output_class(no_of_coins,public_key))
        self.bytestream = bytestream
        
        self.transID = hashlib.sha256(self.bytestream).hexdigest()
        return None

    #prints input
    def print_input(self):
        print("Number of inputs: %d"%self.no_of_inputs)
        for i in range(0,self.no_of_inputs):
            print("\tInput %d:"%(i+1))
            print("\t\tTransaction ID: %s"%(self.array_of_inputs[i]).transID)
            print("\t\tindex: %d"%(self.array_of_inputs[i]).index)
            print("\t\tsignature: %s"%(self.array_of_inputs[i]).sign)

    #print output
    def print_output(self):
        print("Number of outputs: %d"%self.no_of_outputs)
        for i in range(0,self.no_of_outputs):
            print("\tOutput %d"%(i+1))
            print("\t\tNumber of coins: %d"%(self.array_of_outputs[i]).no_of_coins)
            print("\t\tLength of public key: %d"%(self.array_of_outputs[i]).len_of_pubkey)
            print("\t\tPublic Key: %s"%(self.array_of_outputs[i]).public_key)