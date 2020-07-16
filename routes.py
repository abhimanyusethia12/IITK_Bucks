from classes import *


#assuming 
blockchain = [] # blockchain = list of block objects
pending_trans = []  # pending transaction = list of transaction objects
peers = []  # peers = list of strings, each of which is a URL
potential_peers = [] #potential peers = list of strings, each of which is a URL
peer_limit = 5 # peer_limit = an int, representing max number of peers allowed for a node
my_url = '' # my_url= string which has my URL
unused_output_dict = {} # unused_output_dict= dictionary consisting of {(transID,index_of_output):output_object}


#Flask server code
from flask import Flask, jsonify, Request, request, make_response
import requests
app = Flask(__name__)

#index
@app.route('/')
def index():
    print("index page accessed")
    return "<h1>\"Welcome to Abhimanyu's Blockchain\"</h1>"

#get block n
@app.route('/getBlock/<n>')
def send_block(n):
    print("returning nth block")
    block_data = make_response((blockchain[n]).block_bytearray())
    #nblock = block()
    #nblock.block_from_file(n)
    #block_data = make_response(nblock.block_bytearray)
    block_data.mimetype = 'application/octet-stream'
    return block_data

#get pending transaction
@app.route('/getPendingTransactions')
def send_pending_trans():
    pending_trans_dicts = []

    for transaction_obj in pending_trans:
        trans_dict = {}
        all_inputs = []
        all_outputs = []
        for input_obj in transaction_obj.array_of_inputs:
            single_input = {}
            single_input['transactionID'] = input_obj.transID
            single_input['index'] = input_obj.index
            single_input['signature'] = input_obj.sign
            all_inputs += single_input
        
        for output_obj in transaction_obj.array_of_outputs:
            single_output = {}
            single_output['amount'] = no_of_coins
            single_output['recipient'] = public_key
            all_outputs += single_output
        
        trans_dict['inputs'] = all_inputs
        trans_dict['outputs'] = all_outputs

        pending_trans_dicts += trans_dict
    
    return jsonify(pending_trans_dicts)

#new peer
@app.route('/newPeer',methods=["POST"])
def add_new_peer():
    req_dict = request.get_json()
    url = req_dict['url']
    if url in peers:
        print("url %s already in peers"%url)
        return "url %s already added in peers"%url, 500
    if len(peers)>peer_limit:
        print("Peer Limit reached! Can't add more peers")
        return "Peer Limit reached! Can't add more peers", 500
    peers += url
    print("url %s added to peers"%url)
    return "url %s added to peers"%url

#get peers
@app.route('/getPeers')
def send_peers():
    print("returned"+peers)
    return jsonify(peers= peers)

#new block
@app.route('/newBlock',methods=["POST"])
def add_new_block():
    new_block = block()
    binary_data = request.get_data()
    new_block.block_from_bytearray(binary_data)
    blockchain += new_block
    print("Block added")
    return "Block added"

#new transaction
@app.route('/newTransaction',methods=["POST"])
def add_new_trans():
    req_dict = request.get_json()

    no_of_inputs = 0
    array_of_inputs = []

    inputs = req_dict['inputs']
    for single_input in inputs:
        transID = single_input['transactionID']
        index = single_input['index']
        sign = single_input['signature']

        no_of_inputs += 1
        print("adding input no. %d"%no_of_inputs)
        array_of_inputs += input_class(transID,index,sign)  
    
    no_of_outputs = 0
    array_of_outputs = []

    outputs = req_dict['outputs']
    for single_output in outputs:
        no_of_coins = single_output['amount']
        public_key = single_output['recipient']

        no_of_outputs += 1
        print("adding output no. %d"%no_of_outputs)
        array_of_outputs += output_class(no_of_coins,public_key)
    
    pending_trans += transaction_class(no_of_inputs,array_of_inputs,no_of_outputs,array_of_outputs)
    print("added transaction object in list of pending transactions")
    return "added transaction object in list of pending transactions"


if __name__ == '__main__':
    app.run(debug = True, port = 8787)
