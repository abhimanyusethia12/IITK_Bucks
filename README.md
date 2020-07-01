# IITK_Bucks
A bitcoin-like cryptocurrency node

## Data in `routes.py`
The blockchain data will be stored in the following data structures as declared in `routes.py`:

* `blockchain`: list = list of block objects
* `pending_trans`: list = list of (pending) transaction objects
* `peers`: list of strings = each string is a URL of a peer
* `potential_peers`: list = each string is a URL of a potential peer
* `peer_limit`: int = max number of peers allowed for a node
* `my_url`: string = my URL
* `unused_output_dict`: dict = dictionary consisting of {(transID,index_of_output):output_object}
* `block_reward`: int = no of coins set as block reward

## classes.py 

Consists of the class definitions:

* `block_body`
* `block_header`
* `block`
* `input_class` 
* `output_class`
* `transaction_class`


## `routes.py`

Sets up a server on Flask with following endpoints- 

### `/getBlock/<n>`

* accepts a `GET request` 
* returns the binary data for the nth block 
* Content-Type header for the HTTP response will be `application/octet-stream`.

### `/getPendingTransactions`

* accepts a `GET request` 
* returns the pending transactions as JSON
* Content-Type header for the HTTP response will be `application/json` 

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
### `/newPeer`

* accepts a `POST request` 
* accepts data as json file of the form `{url:url_string}`
* adds the url to list of peers, unless peer_limit has been achieved or URL already present in list of peers

### `/getPeers`

* accepts a `GET request` 
* return the list of peers in JSON format
Response format is :
```
{
    "peers": ["https://dryblockchain.com", "http://a38dc2.ngrok.io", "https://blockchain.pclub.in:8787", "http://202.23.145.3:5000"]
}
```

### `/newBlock`

* accepts a `POST request` 
* accepts block data (in binary format) when a new block is mined
* adds the block to the blockchain


### `/newTransaction`

* accepts a `POST request` 
* accepts transaction data in JSON form 
* adds transaction to the list of pending transactions
Format in which data is expected to be received is:
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

## functions.py
The following functions have been implemented in this script-

* `find_peers()`
* `process_block(block_object)`
* `initialize()`
* `verify_block(block_object)`
* `verify_txn(transaction_object)`

Implementation details of some of these functions are- 
### `verify_block(block_object)`
verifies the following conditions in a block object

1 Every transaction in the block is valid
1(a) special verification for coinbase transaction
2 hash of parent block is correct
3 header of the block has been correctly calculated
4 specified nonce creates a hash which is less than the target

### `verify_txn(transaction_object)`

The function `verify_txn(transaction_object, unused_output_dict)` in the file verifies the validity of a transaction. 
It returns `True` if **all** of the following 3 conditions are met; else `False` is returned

- All its inputs exist in our list of unused outputs.
- All the signatures are correct.
- Coins output <= coins Input.
### Verifying signatures

The program assumes that the user signs the following message for each input:

`[32 bytes for transaction ID of the input][4 bytes for the index of the input][32 bytes for the sha256 hash of the output data]`

Here the `output data` refers to the following:

`[number of outputs][number of coins in output 1][length of the public key for output 1][the public key for output 1][number of coins in output 2][length of the public key for output 2][the public key for output 2]...`
