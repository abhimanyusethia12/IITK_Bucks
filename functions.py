from classes import *
from routes import *
from flask import Flask
import requests

def find_peers():
    if len(peers)>peer_limit:
        print("Peer limit reached")
        return "Peer Limit reached"
    for peer in potential_peers:
        res = requests.post(url = peer + '/newPeer', json={'url': my_url})
        print("sent POST request to endpoint /newPeer of URL- %s"%url)
        print("received status code %d"%res.status_code)
        if res.status_code == 200:
            peers += peer
            potential_peers -= peer
            print("added in peers and removed from potential peers- url %s"%peer)
            return "added in peers and removed from potential peers- url %s"%peer
        if res.status_code == 500:
            res2 = requests.get(url = peer + '/getPeers')
            potential_potential_peers += res2.json()['peers']
            for x in potential_potential_peers:
                if x in potential_peers:
                    continue
                if x in peers:
                    continue
                potential_peers += x
            print("added non-repeating potential peers")
            potential_peers -= peer
            find_peers()

def process_block(block_object):
    for transaction_object in block_object.block_body.transaction_list:
        # remove transaction from pending transactions
        pending_trans.remove(transaction_object)

        # remove inputs from unused outputs
        for input_object in transaction_object.array_of_inputs:
            unused_output_dict.pop((input_object.transID,input_object.index))

        #adding outputs to unused outputs list
        index = 0 
        for output_object in transaction_object.array_of_outputs:
            unused_output_dict[(transaction_object.transID,index)] = output_object
            index += 1

    #adding block to local blockchain
    blockchain.append(block_object)
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
    pending_trans = []
    for trans_dict in res2.json():

        #inputs
        no_of_inputs = 0
        array_of_inputs = []
        for input_dict in trans_dict['inputs']:
            array_of_inputs += input_class(input_dict['transactionID'],input_dict['index'],input_dict['signature'])
            no_of_inputs += 1

        #outputs
        no_of_outputs = 0
        array_of_outputs = []
        for output_dict in trans_dict['outputs']:
            array_of_outputs += output_class(output_dict['amount'],output_dict['recipient'])
            no_of_outputs += 1

        pending_trans += transaction_class(no_of_inputs,array_of_inputs,no_of_outputs, array_of_outputs)

    #asking for blocks and processing them
    index = 0
    while(1):
        res = requests.get(url = peers[0] + '/getBlock/'+ str(index))   
        if res.status_code = 404:
            break
        else:
            new_block = block()
            binary_data = res.content
            new_block.block_from_bytearray(binary_data)
            process_block(new_block)
            index += 1
    
    
   
    return None





    







