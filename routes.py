from classes import *
#from functions import *
from threading import Thread
import requests
import time

#assuming 
blockchain = [] # blockchain = list of block objects
pending_trans = []  # pending transaction = list of transaction objects
peers = []  # peers = list of strings, each of which is a URL
potential_peers = ["https://iitkbucks.pclub.in"] #potential peers = list of strings, each of which is a URL
peer_limit = 5 # peer_limit = an int, representing max number of peers allowed for a node
my_url = 'http://ff62c2fb3dc7.ngrok.io' # my_url= string which has my URL
my_pub_key = '' # my public key
unused_output_dict = {} # unused_output_dict= dictionary consisting of {(transID,index_of_output):output_object}
block_reward = 100000 # block_reward = int = no of coins set as block reward
max_blockbody_size = 1000000 # maximum size of block body in number of bits = int
target_value = '0000004000000000000000000000000000000000000000000000000000000000' #target_value = string = target value in hexadecimal
#mining_thread = Thread(target=mining) #worker thread for mining
unused_output_pubkey = {} #maps {public key:[list of tuple (transID, index) each representing an unused output of the public key]}
alias_dict = {} #dict = {'alias':'public key'}

#Flask server code
from flask import Flask, jsonify, Request, request, make_response, Response

app = Flask(__name__)

#index
@app.route('/')
def index():
    print("ENDPOINT:/")
    return "<h1>\"Welcome to Abhimanyu's Blockchain\"</h1>"

#get block n
@app.route('/getBlock/<n>')
def send_block(n):
    print("ENDPOINT: /getBlock/%d"%n)
    if int(n)>=len(blockchain):
        print("E: %dth block doesn't exist"%n)
        return "%dth block doesn't exist"%n,404
    print("E: returning nth block")
    block_data = make_response(blockchain[n].block_bytearray())
    #nblock = block()
    #nblock.block_from_file(n)
    #block_data = make_response(nblock.block_bytearray)
    block_data.mimetype = 'application/octet-stream'
    return block_data

#get pending transaction
@app.route('/getPendingTransactions')
def send_pending_trans():
    print("ENDPOINT: /getPendingTransactions")
    pending_trans_dicts = []

    for transaction_obj in pending_trans:
        trans_dict = {}
        all_inputs = []
        all_outputs = []
        for input_obj in transaction_obj.array_of_inputs:
            single_input = {}
            single_input['transactionId'] = input_obj.transID
            single_input['index'] = input_obj.index
            single_input['signature'] = input_obj.sign
            all_inputs.append(single_input)
        
        for output_obj in transaction_obj.array_of_outputs:
            single_output = {}
            single_output['amount'] = str(no_of_coins)
            single_output['recipient'] = public_key
            all_outputs.append(single_output)
        
        trans_dict['inputs'] = all_inputs
        trans_dict['outputs'] = all_outputs

        pending_trans_dicts.append(trans_dict)
    
    return Response(pending_trans_dicts, mimetype='application/json')

#new peer
@app.route('/newPeer',methods=["POST"])
def add_new_peer():
    print("ENDPOINT: /newPeer")
    req_dict = request.get_json()
    url = req_dict['url']
    if url in peers:
        print("E: url %s already in peers"%url)
        return "url %s already added in peers"%url, 500
    if len(peers)>peer_limit:
        print("E: Peer Limit reached! Can't add more peers")
        return "Peer Limit reached! Can't add more peers", 500
    peers.append(url)
    print("E: url %s added to peers"%url)
    return "url %s added to peers"%url

#get peers
@app.route('/getPeers')
def send_peers():
    print("ENDPOINT: /getPeers")
    print("E: returned")
    print(peers)
    return jsonify(peers= peers)

#new block
@app.route('/newBlock',methods=["POST"])
def add_new_block():
    print("ENPOINT: /newBlock")
    new_block = block()
    binary_data = request.get_data()
    new_block.block_from_bytearray(binary_data)
    if new_block in blockchain:
        print("E:Block already exists in blockchain")
        return "E:Block already exists in blockchain"
    if not verify_block(new_block):
        print("E:Block not verified")
        return "E:Block not verified"
    #global mining_thread
    #mining_thread.join()
    #print("E:Mining thread joined")
    process_block(new_block)
    print("E:Block verified and processed")

    #mining_thread = Thread(target=mining)
    #mining_thread.start()
    print("E:Mining thread started")

    return "Block verified and processed"

#new transaction
@app.route('/newTransaction',methods=["POST"])
def add_new_trans():
    print("ENDPOINT: /newTransaction")
    req_dict = request.get_json()

    no_of_inputs = 0
    array_of_inputs = []

    inputs = req_dict['inputs']
    for single_input in inputs:
        transID = single_input['transactionId']
        index = single_input['index']
        sign = single_input['signature']

        no_of_inputs += 1
        print("E: adding input no. %d"%no_of_inputs)
        array_of_inputs.append(input_class(transID,index,sign))   
    
    no_of_outputs = 0
    array_of_outputs = []

    outputs = req_dict['outputs']
    for single_output in outputs:
        no_of_coins = int(single_output['amount'])
        public_key = single_output['recipient']

        no_of_outputs += 1
        print("E: adding output no. %d"%no_of_outputs)
        array_of_outputs.append(output_class(no_of_coins,public_key))
    
    if not verify_txn(transaction_class(no_of_inputs,array_of_inputs,no_of_outputs,array_of_outputs)):
        print("E: transaction not verified")
        return "transaction not verified"

    pending_trans.append(transaction_class(no_of_inputs,array_of_inputs,no_of_outputs,array_of_outputs))
    print("added transaction object in list of pending transactions")
    return "added transaction object in list of pending transactions"

@app.route('/addAlias',methods=["POST"])
def add_alias():
    print("ENDPOINT: /addAlias")
    alias = request.get_json()['alias']
    pub_key = request.get_json()['publicKey']
    if alias in alias_dict.keys():
        print("E: Alias already exists")
        return "Alias already exits", 400
    alias_dict[alias] = pub_key 
    print("E: added alias %s for pub key %s"%(alias, pub_key))
    return  "added alias %s for pub key %s"%(alias, pub_key)

@app.route('/getPublicKey',methods=["POST"])
def send_public_key():
    print("ENDPOINT: /getPublicKey")
    alias = request.get_json()['alias']
    if alias in alias_dict.keys():
        print("E: Returned pub key %s for alias %s"%(alias_dict[alias],alias))
        return jsonify({"publicKey":alias_dict[alias]})
    else:
        print("alias doesn't exist")
        return "alias doesn't exist",404

@app.route('/getUnusedOutputs',methods=["POST"])
def send_unused_output():
    print("ENDPOINT: /getUnusedOutputs")
    req_dict = request.get_json()
    if "alias" in req_dict.keys():
        pub_key = alias_dict[req_dict["alias"]]
    elif "publicKey" in req_dict.keys():
        pub_key = req_dict["publicKey"]
    else:
        print("E: POST request has neither alias nor publicKey")
        return "POST request has neither alias nor publicKey"
    
    list_of_unused_outputs= []
    for outputs in unused_output_pubkey[pub_key]:
        amount = unused_output_dict[outputs].no_of_coins
        list_of_unused_outputs.append({
            'transactionId': outputs[0],
            'index':outputs[1],
            'amount':str(amount)
        })
    print("E: returned list of unused Output of pub key %s"%pub_key)
    print(list_of_unused_outputs)
    return jsonify(unusedOutputs=list_of_unused_outputs)


def mining():
    print("FUN1: mining()")
    while True:
        #checking for transactions
        while len(pending_trans) == 0:
            print("F1: No pending transactions")
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
        print("F1: block mined, processed and sent to peers;continuing to mine")
    return None


def find_peers():
    #check if peer limit is reached
    print("FUN2:find_peers()")
    if len(peers)>peer_limit:
        print("F2:Peer limit reached")
        return "Peer Limit reached"
    
    for peer in potential_peers:
        #sending requests at /newPeer to potential peers
        res = requests.post(url = peer + '/newPeer', json={'url': my_url})
        print("F2:sent POST request to endpoint /newPeer of URL- %s"%peer)
        print("F2:received status code %d"%res.status_code)

        #if accepted, added to peers and removed from potential peers
        if res.status_code == 200:
            peers.append(peer)
            potential_peers.remove(peer)
            print("F2:added in peers and removed from potential peers- url %s"%peer)
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
            print("F2:added non-repeating potential peers")
            potential_peers.remove(peer)
            find_peers()

def process_block(block_object):
    print("FUN3: process_block()")
    if block_object in blockchain:
        print("F3:block already in blockchain")
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
            if output_object.public_key in unused_output_pubkey.keys():
                unused_output_pubkey[output_object.public_key].append((transaction_object.transID,index))
            else:
                unused_output_pubkey[output_object.public_key]= [(transaction_object.transID,index)]
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
    print("FUN4:initialize")
    if len(potential_peers) <= 0:
        print("F4:Can't initialize due to no potential peers")
        return "Can't initialize due to no potential peers"
    
    #finding peers
    find_peers()

    #checking if there are any peers
    if len(peers) <= 0:
        print("F4:Can't initialize due to no peers")
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
            print("F4:pending transaction added")
        else:
            print("F4:transaction not verified")

    #asking for blocks and processing them
    index = 0
    while(1):
        res = requests.get(url = peers[0] + '/getBlock/'+ str(index))   
        print("F4:working on block no. %d"%index)
        if res.status_code == 404:
            break
        else:
            block_object = block()
            binary_data = res.content
            block_object.block_from_bytearray(binary_data)
            #if verify_block(new_block):
            #process_block(new_block)
            if block_object in blockchain:
                print("F4:block already in blockchain")
                return "F4:block already in blockchain"
                
            for transaction_object in block_object.block_body.transaction_list:
                print("F4:Working on transaction_object.transID %s"%transaction_object.transID)
                # remove inputs from unused outputs
                for input_object in transaction_object.array_of_inputs:
                    pub_key = unused_output_dict[(input_object.transID,input_object.index)].public_key
                    unused_output_dict.pop((input_object.transID,input_object.index))
                    #print("removed (%s,%d) from unused_ouput_dict and unused output pubkey %s"%(input_object.transID[2:],input_object.index,pub_key))
                    unused_output_pubkey[pub_key].remove((input_object.transID,input_object.index)) 

                #adding outputs to unused outputs list
                index_output = 0 
                for output_object in transaction_object.array_of_outputs:
                    unused_output_dict[(transaction_object.transID,index_output)] = output_object
                    if output_object.public_key in unused_output_pubkey.keys():
                        unused_output_pubkey[output_object.public_key].append((transaction_object.transID,index_output))
                        #print("added (%s,%d) to unused output pubkey %s"%(transaction_object.transID,index,output_object.public_key))
                    else:
                        unused_output_pubkey[output_object.public_key] = [(transaction_object.transID,index_output)]
                        #print("added [(%s,%d)] to unused output pubkey %s"%(transaction_object.transID,index,output_object.public_key))
                    index_output += 1

            #adding block to local blockchain
            blockchain.append(block_object)
            index += 1
            #else:
            #    print("block no. %d not verified during initialisation"%index)
            #    break
    return None

def verify_block(block_object):
    print("FUN5:verify_block()")

    #Cond 1- Every transaction in the block is valid 
    flag =0
    input_coins = 0
    output_coins = 0 
    for transaction_obj in block_object.block_body.transaction_list:
        if flag == 0: #coinbase transaction
            flag += 1
            continue
        for input_object in transaction_obj.array_of_inputs:
            #input_coins += (unused_output_dict[(input_object.transID[2:],input_object.index)]).no_of_coins
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
    for input_obj in transaction_object.array_of_inputs:
        if (input_obj.transID,input_obj.index) in unused_output_dict.keys():
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
        final_bytes.extend((input_obj.transID).encode())
        final_bytes.extend((input_obj.index).to_bytes(4,'big'))
        final_bytes.extend(hash_bytes.digest())

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
    for input_obj in transaction_object.array_of_inputs:
        output_obj = unused_output_dict[(input_obj.transID,input_obj.index)]
        input_coins += output_obj.no_of_coins
    for output in transaction_object.array_of_outputs:
        output_coins += output.no_of_coins
    
    if output_coins<= input_coins:
        return True
    else:
        return False


#verifying a transaction (all three conditions)
def verify_txn(transaction_object):
    print("FUN6:verify_txn()")
    if ver_correct_input(transaction_object) and ver_output_less_than_input(transaction_object) and ver_sign(transaction_object):
        return True
    else:
        return False

print("App started!")
initialize()
print("Initialized blockchain")
#mining_thread = Thread(target=mining)
app.config['JSON_SORT_KEYS'] = False
if __name__ == '__main__':
    app.run(debug = True, port = 8787)
    #mining_thread.start()
    #print("Mining thread started")