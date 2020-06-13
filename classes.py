
class block:
    def __init__(self, block_body, block_header):
        self.block_body = block_body #assuming block body will be a bytearray
        self.block_header = block_header
    
    def block_bytearray(self):
        return self.block_header.header_bytearray() + self.block_body

class block_body:
    def __init__(self, body):
        self.body = body

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
    def __init__(self, no_of_inputs, array_of_inputs, no_of_outputs, array_of_outputs):
        self.no_of_inputs = no_of_inputs
        self.array_of_inputs = array_of_inputs
        self.no_of_outputs = no_of_outputs
        self.array_of_outputs = array_of_outputs

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
            #finalbytes.extend((input_obj.transID).encode())
            finalbytes.extend(bytearray.fromhex(input_obj.transID))
            finalbytes.extend((input_obj.index).to_bytes(4,'big'))
            finalbytes.extend((input_obj.len_of_sign).to_bytes(4,'big'))
            #finalbytes.extend((input_obj.sign).encode())
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



        
