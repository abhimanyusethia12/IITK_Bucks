from classes import block, transaction_class


#assuming a blockchain as a list of block objects
blockchain = []

#assuming pending transaction as a list of transaction objects
pending_trans = []
#Flask server code
from flask import Flask, jsonify, Request, make_response
app = Flask(__name__)

@app.route('/getBlock/<n>')
def send_block(n):
    print("returning nth block")
    block_data = make_response((blockchain[n]).block_bytearray())
    block_data.mimetype = 'application/octet-stream'
    return block_data

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
