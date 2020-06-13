# IITK_Bucks
A bitcoin-like cryptocurrency node

## classes.py 

Consists of the class definitions:

* block body
* block header
* block
* input_class 
* output_class
* transaction_class

## verify_txn.py

The function `verify_txn(transaction_object, unused_output_dict)` in the file verifies the validity of a transaction. 
It returns `True` if **all** of the following 3 conditions are met; else `False` is returned

- All its inputs exist in our list of unused outputs.
- All the signatures are correct.
- Coins output <= coins Input.

### List of Unused Outputs

The unused outputs are maintained as a dictionary with the following key:value pairs- 
`{(transactionID, index):output_object}`

### Verifying signatures

The program assumes that the user signs the following message for each input:

`[32 bytes for transaction ID of the input][4 bytes for the index of the input][32 bytes for the sha256 hash of the output data]`

Here the `output data` refers to the following:

`[number of outputs][number of coins in output 1][length of the public key for output 1][the public key for output 1][number of coins in output 2][length of the public key for output 2][the public key for output 2]...`

## node_addition.py 

Sets up a server on Flask with two endpoints- 

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
