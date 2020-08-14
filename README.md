# IITK_Bucks
I have developed a **fully-functional blockchain-based cryptocurrency node** and have also written a script for **terminal-based User interface** for the node. All scripts are written in Python and use Flask framework for server code. 

The node here, is consistent with (and has been tested with) a network of 15 nodes [(list of nodes here)](https://iitkbucks.pclub.in/), each using different languages (Javascript, Go, Java, Python) and different backend frameworks. 

This README file has  two sections- Project Development Details and Technical Details

# Project Details
This Project was developed for the [Programming Club, IIT Kanpur](https://pclub.in), under @dryairship.
## Project Timeline
1. Assignments phase
    In the first phase, we learn about blockchains and solved assignments to singularly implement different parts of the project.
2. Project Building phase
    In the second phase, we put together the various parts implemented at assignments into a main application.
3. Deployment phase
    One node of the project had been deployed on https://iitkbucks.pclub.in from 13th July 2020 till 26th July 2020. Through trying to communicate with that node, we found and eliminated the bugs in our applications. In this phase, we brought our programs to completion.

## Learnings from the Project
1. I learnt about an entire new domain of **cryptocurrency and blockchain**- got hands-on learning on how cryptocurrencies and blockchains work. Also, looked at other real-life applications of blockchain
2. I learnt about and implemented **Multi-Threading** for effeciently mining blocks. Implementing Multi-threading in Python was truly one of the most challenging parts of the project. Since the `Threading` library in Python is not very well documented, I had to figure out how a number of methods and objects work by trying and iterating.
3. **Modelling a large project using appropriate Classes and Methods**- Thinking about how to best model the project so as to minimise writing repititive code and improve readability of code was a big challenge
4. I learnt a lot about Cryptography and **implemented Digital Signatures**- This included generating keys, signing a given message and verifying signatures. I got hands-on experience with the `cryptography` library in Python
5. I learnt **how to obtain universal hostnames through tunneling softwares like ngrok** 
6. I got firsthand experience with **using Flask framework to develop backend server**

## Scope of Improvement/Expansion
1. **Better OOP modelling** - In hindsight, I think the project could be modelled in a more effecient manner. Adding a number of methods in Block and transaction classes, might have eliminated repitive code and also, would have subsumed some independent functions. 
2. **Dynamic target**- In my node, the target for mining is fixed. However, in real cryptocurrencies the target is dynamically determined.
3. **Chain Reorganisation** - The node would face issues in case two blocks are mined with the same timestamp or with the same index. Adding a function for reorganisation of chain in case multiple valid blocks have the same index would be a nice feature.
4. **Developing Web-App based UI** - Currently, the frontend of the project is a Command Line Interface. However, it is not very user-friendly. A web-app would be much more handy for users.
5. **Write code to preferentially include Transactions in Block for mining**- The Miner of my node, simply picks up as many transactions as it can (within the maximum block size) starting from index 0. However, in reality, the miners usually pick up transactions in the decreasing order of the transaction fee, so as to maximise earning from mining. Implementing such a function which preferentially includes transactions in a block would make the Miner closer to real-life.

# Technical Details
The entire server code for the node is written in [`app.py`](./app.py). It consists of- 
* endpoints of server
* definition of various functions
* global blockchain variables
* code for initialisation of server

It inherits the classes from [`classes.py`](./classes.py).

[`user_interface_IITKBucks.py`](./user_interface_IITKBucks.py) consists of the script for terminal-based user-interface of the node. 

## User Interface 
The user is allowed to perform the following actions by running the [`user_interface_IITKBucks.py`](./user_interface_IITKBucks.py) script-

1. Check Balance - allows user to check balance for any public key or alias
2. Create Account - generates a pair of public and private keys
3. Transfer Coins - allows user to create a transaction with any number of outputs
4. Add Alias - alows user to add an alias for his public key

## Classes

The following classes, along with the respective methods are defined in [`classes.py`](./classes.py) :

* `block_body`
* `block_header`
* `block`
* `input_class` 
* `output_class`
* `transaction_class`

## Global Blockchain Variables

The blockchain data is stored in the following data structures as declared in [`app.py`](./app.py):

* `blockchain`: list = list of block objects
* `pending_trans`: list = list of (pending) transaction objects
* `peers`: list of strings = each string is a URL of a peer
* `potential_peers`: list = each string is a URL of a potential peer
* `peer_limit`: int = max number of peers allowed for a node
* `my_url`: string = my URL
* `unused_output_dict`: dict = dictionary consisting of {(transID,index_of_output):output_object}
* `block_reward`: int = no of coins set as block reward
* `max_blockbody_size`: int = maximum size of the block body, in number of bits
* `target_value`: string = target value for mining as a hexadecimal string
* `mining_thread`: `threading.Thread` object = worker thread for mining
* `unused_output_pubkey` : dict = {public key:[list of tuples (transID, index)] where each tuple represents an unused output of the public key]}
* `alias_dict`: dict = {'alias':public key}

## Endpoints of the Node  Server
Sets up a server on Flask with following endpoints- 

1. `/getBlock/<n>` - accepts a `GET request` and **sends back binary data of nth block**
2. `/getPendingTransactions`- accepts a `GET request` and **sends back pending transactions dictionary in JSON format**<sup>1</sup>
3. `/newPeer` - accepts a `POST request` with data as json file of the form `{url:url_string}` and **adds the url to list of peers**, unless peer_limit has been achieved or URL is already present in list of peers
4. `/getPeers` - accepts a `GET request` and **returns the list of peers** in JSON format <sup>2</sup>
5. `/newBlock`- accepts a `POST request` with block data (in binary format) when a new block is mined; **adds the block to the blockchain** after verification and processing
6. `/newTransaction`- accepts a `POST request` with transaction data in JSON format <sup>3</sup>; **adds transaction to the list of pending transactions**, after verification of transaction
7. `/addAlias`- accepts a `POST request` with alias and public key in JSON format<sup>4</sup>; **adds {alias:public key} mapping to `alias_dict`**
8. `/getPublicKey` - accepts a `POST request` with alias in JSON format ({'alias':alias}); **sends back public key** corresponding to the alias, in JSON format ({'publicKey':public key})
9. `/getUnusedOutputs`- accepts a `POST request` with either alias or public key or both ({'alias':alias, 'publicKey: public key}); **sends back list of unused outputs, corresponding to the public key**, in JSON format.

## Functions
The following functions have been defined in `app.py`-

* `mining()`- starts mining blocks
* `find_peers()`
* `process_block(block_object)` - 
    -removes transaction from pending transactions
    -removes inputs from unused outputs
    -adds outputs to unused outputs
    -adds block to local blockchain 
    -sends block to peers on `/newBlock` endpoint
* `initialize()` -
    -calls `finds_peers()`
    -asks for blockchain from peers and pending transactions 
* `verify_block(block_object)` - 
    -every transaction in the block must be valid (including the coinbase transaction)
    -hash of parent block must be correct
    -header of block must be rightly calculated
    -correctness of nonce i.e. it gives a hash less than the target
* `verify_txn(transaction_object)`
    -all inputs exist in list of unused outputs
    -verifies signatures<sup>5</sup>
    -verifies that number of output coins <= number of input coins

## Footnotes

1. Response format from `/getPendingTransaction` endpoint

Content-Type header for the HTTP response will be `application/json` 
The format of the data will be:
```
{
    [
        {
            "inputs": [
                {
                    "transactionID": "<hex representation of the transaction ID of this input>",
                    "index": <index of this input in the list of outputs of the transaction>,
                    "signature": "<hex representation of the signature for this input>"
                },
                {
                    "transactionID": "<hex representation of the transaction ID of this input>",
                    "index": <index of this input in the list of outputs of the transaction>,
                    "signature": "<hex representation of the signature for this input>"
                }
            ],
            "outputs": [
                {
                    "amount": <number of coins>,
                    "recipient": "<public key of recipient>"
                },
                {
                    "amount": <number of coins>,
                    "recipient": "<public key of recipient>"
                },
                {
                    "amount": <number of coins>,
                    "recipient": "<public key of recipient>"
                }
            ]
        },
        {
            "inputs": [
                {
                    "transactionID": "<hex representation of the transaction ID of this input>",
                    "index": <index of this input in the list of outputs of the transaction>,
                    "signature": "<hex representation of the signature for this input>"
                },
                ...
            ],
            "outputs": [
                {
                    "amount": <number of coins>,
                    "recipient": "<public key of recipient>"
                },
                ...
            ]
        },
        ...
    ]
}

```
2. Response format from `/newPeer` endpoint is :
```
{
    "peers": ["https://dryblockchain.com", "http://a38dc2.ngrok.io", "https://blockchain.pclub.in:8787", "http://202.23.145.3:5000"]
}
```
3. Format in which data is expected to be received at `/newTransaction` endpoint:
```
{
    "inputs": [
        {
            "transactionID": "<hex representation of the transaction ID of this input>",
            "index": <index of this input in the list of outputs of the transaction>,
            "signature": "<hex representation of the signature for this input>"
        },
        ...
    ],
    "outputs": [
        {
            "amount": <number of coins>,
            "recipient": "<public key of recipient>"
        },
        ...
    ]
}
```
4. Format in which data is expected to be received at `addAlias` endpoint:
```
{
    'alias':alias,
    'publicKey':pub_key
}
```
5. The signature verification function assumes that the user signs the following message for each input using `SHA256 hash` and `PSS padding` with salt length `32`.

`[32 bytes for transaction ID of the input][4 bytes for the index of the input][32 bytes for the sha256 hash of the output data]`

Here the `output data` refers to the following:

`[number of outputs][number of coins in output 1][length of the public key for output 1][the public key for output 1][number of coins in output 2][length of the public key for output 2][the public key for output 2]...`

