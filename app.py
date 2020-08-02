from classes import *
from routes import *
from flask import Flask
import requests
import time

def mining():
    while True:
        #checking for transactions
        while len(pending_trans) == 0:
            print("No pending transactions")
            time.sleep(1)

        #getting transactions from pending_trans
        trans_bytes = bytearray()
        buffer_trans_list = [] #will subtract from pending trans if mining successful
        input_coins = 0
        output_coins = 0
        
        for transaction_obj in pending_trans:
            if trans_bytes + transaction_obj.transactionToByteArray() < max_blockbody_size-4 -20 -len(my_pub_key): 
            #the bits subtracted are for: no_of_transaction (4bits) + coinbase transaction (20+len(my_pub_key))
                trans_bytes += transaction_obj.transactionToByteArray()
                buffer_trans_list.append(transaction_obj) 
                
                for output_obj in transaction_obj.array_of_outputs:
                    output_coins += output_obj.no_of_coins
                for input_obj in transaction_obj.array_of_inputs:
                    input_coins += unused_output_dict[(input_obj.transID,input_obj.index)]

        #making coinbase transaction
        output_obj = output_class(input_coins-output_coins+block_reward, my_pub_key)
        coinbase_trans = transaction_class(no_of_inputs=0,array_of_inputs=[],no_of_outputs=1,array_of_outputs=[output_obj])
        
        # making block
        body = (len(buffer_trans_list)+1).to_bytes(4,'big')+ coinbase_trans.transactionToByteArray + trans_bytes
        block_body = block_body(body)
        index = len(blockchain)
        parent_block_hash = blockchain[-1].block_header.calc_hash()
        block_body_hash = body.calc_hash()
        target_value = target_value
        #finding nonce
        nonce = 1
        while True:
            timestamp = time.time_ns()
            block_header = block_header(index,parent_block_hash,block_body_hash,target_value,timestamp,nonce)
            if int(block_header.calc_hash,16) < int(target_value,16):
                break
            nonce += 1
        #newblock steps
        process_block(block(block_body,block_header))
        print("block mined, processed and sent to peers;continuing to mine")
    return None


def find_peers():
    #check if peer limit is reached
    if len(peers)>peer_limit:
        print("Peer limit reached")
        return "Peer Limit reached"
    
    for peer in potential_peers:
        #sending requests at /newPeer to potential peers
        res = requests.post(url = peer + '/newPeer', json={'url': my_url})
        print("sent POST request to endpoint /newPeer of URL- %s"%url)
        print("received status code %d"%res.status_code)

        #if accepted, added to peers and removed from potential peers
        if res.status_code == 200:
            peers.append(peer)
            potential_peers.remove(peer)
            print("added in peers and removed from potential peers- url %s"%peer)
            return "added in peers and removed from potential peers- url %s"%peer
        
        #if rejected, send request at /getPeers to send more peer requests
        if res.status_code == 500:
            res2 = requests.get(url = peer + '/getPeers') 
            for x in res2.json()['peers']:
                if x in potential_peers:
                    continue
                if x in peers:
                    continue
                potential_peers.append(x)
            print("added non-repeating potential peers")
            potential_peers.remove(peer)
            find_peers()

def process_block(block_object):
    if block_object in blockchain:
        print("block already in blockchain")
        return "block already in blockchain"
    
    for transaction_object in block_object.block_body.transaction_list:
        # remove transaction from pending transactions
        pending_trans.remove(transaction_object)

        # remove inputs from unused outputs
        for input_object in transaction_object.array_of_inputs:
            pub_key = unused_output_dict[(input_object.transID,input_object.index)].public_key
            unused_output_dict.pop((input_object.transID,input_object.index))
            unused_output_pubkey[pub_key].remove((input_object.transID,input_object.index)) 

        #adding outputs to unused outputs list
        index = 0 
        for output_object in transaction_object.array_of_outputs:
            unused_output_dict[(transaction_object.transID,index)] = output_object
            unused_output_pubkey[output_object.public_key].append((transaction_object.transID,index)) 
            index += 1

    #adding block to local blockchain
    blockchain.append(block_object)

    #sending new block to peers
    for url in peers:
        res = requests.post(
            url= url+'/newBlock',
            data= block_object.block_bytearray(),
            headers={'Content-Type': 'application/octet-stream'}
        )   
    return None

def initialize():
    if len(potential_peers) <= 0:
        print("Can't initialize due to no potential peers")
        return "Can't initialize due to no potential peers"
    
    #finding peers
    find_peers()

    #checking if there are any peers
    if len(peers) <= 0:
        print("Can't initialize due to no peers")
        return "Can't initialize due to no peers"
    
    #asking for pending transactions
    res2 = requests.get(url = peers[0]+'/getPendingTransactions')
    for trans_dict in res2.json():
        #inputs
        no_of_inputs = 0
        array_of_inputs = []
        for input_dict in trans_dict['inputs']:
            array_of_inputs.append(input_class(input_dict['transactionId'],input_dict['index'],input_dict['signature']))
            no_of_inputs += 1

        #outputs
        no_of_outputs = 0
        array_of_outputs = []
        for output_dict in trans_dict['outputs']:
            array_of_outputs.append(output_class(int(output_dict['amount']),output_dict['recipient']))
            no_of_outputs += 1
        
        transaction_obj = transaction_class(no_of_inputs,array_of_inputs,no_of_outputs, array_of_outputs)
        if verify_txn(transaction_obj):
            pending_trans.append(transaction_obj)
        else:
            print("transaction not verified")

    #asking for blocks and processing them
    index = 0
    while(1):
        res = requests.get(url = peers[0] + '/getBlock/'+ str(index))   
        if res.status_code == 404:
            break
        else:
            new_block = block()
            binary_data = res.content
            new_block.block_from_bytearray(binary_data)
            if verify_block(new_block):
                process_block(new_block)
                index += 1
            else:
                print("block no. %d not verified during initialisation"%n)
                break
    return None

def verify_block(block_object):

    #Cond 1- Every transaction in the block is valid 
    flag =0
    input_coins = 0
    output_coins = 0 
    for transaction_obj in block_object.block_body.transaction_list:
        if flag == 0: #coinbase transaction
            flag += 1
            continue
        for input_object in transaction_obj.array_of_inputs:
            input_coins += (unused_output_dict[(input_object.transID,input_object.index)]).no_of_coins
        for output_object in transaction_obj.array_of_outputs:
            output_coins += output_object.no_of_coins
        if verify_txn(transaction_obj) == False:
            return False
    
    #Cond 1(a)- verifying the coinbase transaction - the first transaction in every block
    if block_object.block_body.transaction_list[0].array_of_outputs[0].no_of_coins > output_coins - input_coins + block_reward:
        return False
    
    #Cond 2- hash of the parent block is correct
    if block_object.block_header.index == 0:
        if block_object.block_header.parent_block_hash != 0000000000000000000000000000000000000000000000000000000000000000:
            return False
    elif block_object.block_header.parent_block_hash != blockchain[block_object.block_header.index].block_header.calc_hash():
        return False

    #Cond 3- The header of the block has been correctly calculated
    if block_object.block_body.calc_hash() != block_object.block_header.block_body_hash:
        return False
    
    #Cond 4- The specified nonce creates a hash which is less than the target.
    if block_object.block_header.calc_hash() >= block_object.block_header.nonce:
        return False
    
    return True



                #### CODE FOR TRANSACTION VERIFICATION ####

#Verification Cond 1- All its inputs exist in our list of unused outputs 
def ver_correct_input(transaction_object):
    for input in transaction_object.array_of_inputs:
        if (input.transID,input.index) in unused_output_dict.keys():
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

def ver_sign(transaction_object):

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
                    #salt_length=padding.PSS.MAX_LENGTH
                    salt_length=32
                ),
                hashes.SHA256()
            )
            print("Signature Verified!")
        except InvalidSignature:
            print("Signature Verification Failed!")
            return False
    return True

#Verification Cond 3- It doesn't spend more coins than it is allowed to.

def ver_output_less_than_input(transaction_object):
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
def verify_txn(transaction_object):
    if ver_correct_input(transaction_object,unused_output_dict) and ver_output_less_than_input(transaction_object,unused_output_dict) and ver_sign(transaction_object,unused_output_dict):
        return True
    else:
        return False