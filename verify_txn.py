
#input class
class input_class:
    def __init__(self, transID, index, sign):
        self.transID = transID
        self.index = index
        self.len_of_sign = len(sign)
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

#assuming unused_output_dict is a dictionary consisting of {(transID,index_of_output):output_object}
unused_output_dict = {} 

#Verification Cond 1- All its inputs exist in our list of unused outputs 
def ver_correct_input(transaction_object, unused_output_dict):
    array_of_inputs = transaction_object.array_of_inputs
    for input in array_of_inputs:
        if (input.transID,input.index) in unused_output_dict:
            continue
        else:
            return False
    return True

#Verification Cond 2 - All the signatures are correct.


from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature

def ver_sign(transaction_object,unused_output_dict):

    array_of_inputs = transaction_object.array_of_inputs
    array_of_outputs = transaction_object.array_of_outputs

    #output data   
    output_bytes = bytearray()
    output_bytes.extend((transaction_object.no_of_outputs).to_bytes(4,'big'))
    for output_obj in array_of_outputs:
        output_bytes.extend()
        output_bytes.extend((output_obj.no_of_coins).to_bytes(8,'big'))
        output_bytes.extend((output_obj.len_of_pubkey).to_bytes(4,'big'))
        output_bytes.extend((output_obj.public_key).encode())
    
    #finding SHA256 hash of the output data
    import hashlib
    hash_bytes = hashlib.sha256(output_bytes)

    #input data
    for input_obj in array_of_inputs:

        # message
        final_bytes = bytearray()
        finalbytes.extend((input_obj.transID).encode())
        finalbytes.extend((input_obj.index).to_bytes(4,'big'))
        final_bytes.extend(hash_bytes)

        #sign
        signature_hex = input_obj.sign

        #public key
        output_obj2 = unused_output_dict[(input_obj.transID,input_obj.index)]
        public_key_string = output_obj2.public_key

        #deserializing public key
        public_key = load_pem_public_key(
            public_key_string, 
            backend=default_backend()
        )

        #converting signature to bytes
        signature = bytes.fromhex(signature_hex)

        #verifying
        try:    
            public_key.verify(
                signature,
                final_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            print("Signature Verified!")
        except InvalidSignature:
            print("Verification Failed!")
            return False
    return True

#Verification Cond 3- It doesn't spend more coins than it is allowed to.

def ver_output_less_than_input(transaction_object, unused_output_dict):
    input_coins = 0
    output_coins = 0
    for input in transaction_object.array_of_inputs:
        output_obj = unused_output_dict[(input.transID,input.index)]
        input_coins += output_obj.no_of_coins
    for output in transaction_object.array_of_outputs:
        output_coins += output.no_of_coins
    
    if output_coins<= input_coins:
        return True
    else:
        return False


#verifying a transaction (all three conditions)
def verify_txn(transaction_object,unused_output_dict):
    if ver_correct_input(transaction_object,unused_output_dict) and ver_output_less_than_input(transaction_object,unused_output_dict) and ver_sign(transaction_object,unused_output_dict):
        return True
    else:
        return False