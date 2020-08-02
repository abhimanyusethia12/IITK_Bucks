import pyfiglet

ascii_banner = pyfiglet.figlet_format("Abhimanyu's Blockchain Node")


print("HELLO USER!")
print("Welcome to")
print(ascii_banner)
print("This is Abhimanyu's node in the IITK Bucks network")
print("developed by Abhimanyu Sethia (abhimanyusethia12@gmail.com)")
print("\n\n\n")

import requests
from classes import *
my_url = "https://6655b7af40ea.ngrok.io"
def check_balance():
    x= int(input("\nFor checking balance \nvia alias press 1\nvia public key .pem file press 2\nYour choice: "))
    if x == 1:
        alias = input("Enter your alias: ")
        res = requests.post(url = my_url+ '/getUnusedOutputs', json={'alias': alias})
    elif x==2:
        pub_key_file_path = input("Enter path to .pem public key file: ") 
        res = requests.post(
            url= my_url + '/getUnusedOutputs',
            json={'publicKey':open(pub_key_file_path,"rb").read().decode()}
        )
    else: 
        print("Operation terminated due to invalid input :(")
        return None
    balance = 0
    try:
        for output in res.json()["unusedOutputs"]:
            balance += int(output["amount"])
        print("BALANCE IN ACCOUNT: %d"%balance)
    except:
        print("Either alias doesn't exist or has 0 balance or improper input")
    return balance

def create_account():
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import default_backend


    # generate private/public key pair
    private_key = rsa.generate_private_key(
        backend=default_backend(), 
        public_exponent=65537,
        key_size=2048)

    # get public key in OpenSSH format
    #public_key = key.public_key().public_bytes(serialization.Encoding.OpenSSH, \
    #    serialization.PublicFormat.OpenSSH)
    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # get private key in PEM container format
    pem = private_key.private_bytes(encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption())

    # decode to printable strings
    private_key_str = pem.decode('utf-8')
    public_key_str = public_key.decode('utf-8')

    print('Private key = ')
    print(private_key_str)
    print('Public key = ')
    print(public_key_str)

    with open("private_key.pem",'w') as priv_file:
        print(private_key_str, file = priv_file)
    with open("public_key.pem","w") as pem_file:
        print(public_key_str,file=pem_file)
    
    print("SAVED KEYS IN FILE- private_key.pem and public_key.pem")

def transfer_coins():
    #getting inputs: pub key, private key of sender, number of output(s), transaction fee, for each output, pub key of receiver and amount
    print("For transfering coins, there are three steps")
    print("1. your (sender's) details")
    print("2. transaction details")
    print("3. Output details (receiver's details)\n\n")
    
    #Step 1
    while True:
        unused_output_list = step1()
        if unused_output_list == None:
            y = int(input("Press 1 to retry\n press 0 to terminate operation: \n"))
            if y== 0:
                return None
        else:
            break
    private_key_path = input("Enter path to your private key file (.pem): ")

    #Step 2
    print("\n\n STEP 2- Transaction Details")
    trans_fee = int(input("transaction fee (no. of coins): "))
    ouput_no = int(input("Number of outputs/ No. of Users you want to give coins to: "))

    #Step 3
    while True:
        _ = step3(ouput_no) 
        if _ == None:
            y = int(input("Press 1 to retry\n press 0 to terminate operation: \n"))
            if y== 0:
                return None
        else:
            output_list = _[0]
            output_coins = _[1]
            break
    #creating a transaction item
    input_coins = 0
    flag = 0
    input_list = [] 
    for output in unused_output_list:
        if input_coins > output_coins +trans_fee:
            flag =1
            break
        input_list.append({
            "transactionId": output['transactionId'],
            "index":output['index'],
            'signature':sign(output_list,output,private_key_path)
        })
        input_coins += int(output['amount'])
        input_list
    if flag ==0:
        print("Not enough balance to perform transaction- terminating operation")
        return None
    
    #sending a /newTransaction request
    res = requests.post(
        url=my_url + '/newTransaction',
        json={
            'inputs':input_list,
            'outputs':output_list
        }
    )
    if res.status_code == 200:
        print("new transaction successful, wait for trans to get included in a block")
    else:
        print("request to server failed :(")

def sign(output_list,output_input,private_key_path):
    output_bytes = bytearray()
    output_bytes.extend(len(output_list).to_bytes(4,'big'))
    for output in output_list:
        output_bytes.extend(int(output["amount"]).to_bytes(8,'big'))
        output_bytes.extend(len(output["recipient"]).to_bytes(4,'big'))
        output_bytes.extend(output["recipient"].encode())
    
    #finding SHA256 hash of the output data
    import hashlib
    hash_bytes = hashlib.sha256(output_bytes)

    #input data
    final_bytes = bytearray()
    final_bytes.extend(bytearray.fromhex(output_input['transactionId']))
    final_bytes.extend(output_input['index'].to_bytes(4,'big'))
    final_bytes.extend(hash_bytes.digest())

    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization

    #retrieving and deserialising private key from a .pem file
    
    with open(private_key_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None,
        backend=default_backend()
    )

    #asking user for message and signing the message using the private key obtained above
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding

    signature = private_key.sign(
        final_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=32
        ),
        hashes.SHA256()
    )

    return signature.hex()



def step1():
    print("STEP 1- Your (sender's) details")
    x= int(input("To transact with your alias press 1\n to transact with your public key press 2:\n"))
    if x == 1:
        alias = input("Enter your alias: ")
        res = requests.post(url = my_url+ '/getUnusedOutputs', json={'alias': alias})
    elif x==2:
        pub_key_file_path = input("Enter path to .pem public key file: ") 
        res = requests.post(
            url= my_url + '/getUnusedOutputs',
            json={'publicKey':open(pub_key_file_path,"rb").read().decode()}
        )
    else: 
        print("invalid input :(")
        return None
    
    if res.status_code != 200:
        print("request to server failed :(")
        return None
    try:
        unused_output_list = res.json()["unusedOutputs"]
        return unused_output_list
    except:
        print("Either you have no balance or alias/public_key doesn't exist")
        return None

def step3(ouput_no):
    print("\n\n STEP 3- Output Details")
    output_list = []
    output_coins = 0
    for i in range(ouput_no):
        print("\nFor output no. %d"%(i+1))
        x = int(input("to enter recipient's alias press 1\n to enter recipient's public key file path press 2\n Press any other key to exit: "))
        if x==1:
            alias = input("Enter alias of recipient: ")
            res = requests.post(url = my_url+ '/getPublicKey', json={'alias': alias})
            if res.status_code == 404:
                print("alias does not exist")
                return None
            elif res.status_code == 200:
                pub_key = (res.json()["publicKey"].encode()).decode()
        elif x==2:
            pub_key_file_path = input("Enter path to recipient no. %d's public key (.pem) file: "%(i+1))
            try:
                pub_key = open(pub_key_file_path,"rb").read().decode()
            except:
                print("Invalid path")
                return None
        amount = int(input("Enter number of coins to be transferred to recipient no. %d: "%(i+1)))
        output_list.append({
            "amount":str(amount),
            "recipient":pub_key
        })
        output_coins += amount
    return (output_list, output_coins)


def add_alias():
    pub_key_file_path = input("\nEnter path to your public key (.pem) file: ")
    pub_key = open(pub_key_file_path,"rb").read().decode()
    alias = input("Enter your alias: ")
    res = requests.post(
        url=my_url + '/addAlias',
        json={
            'alias':alias,
            'publicKey':pub_key
        }
    )
    if res.status_code == 200:
        print("ALIAS SET")
    else:
        print("Sorry request failed")


while(1):
    print("You have four options- press the number for each action")
    print("1- check balance")
    print("2- create account")
    print("3- tranfer coins")
    print("4- add an alias")
    print("0- to exit ")
    x = int(input("Please enter number corresponding to the action: "))
    if x == 1:
        print("received 1- initiating check balance")
        check_balance()
    elif x == 2:
        print("received 2- initiating create account")
        create_account()
    elif x==3 :
        print("received 3- initiating transfer coins")
        transfer_coins()
    elif x==4:
        print("received 4- initiating add alias")
        add_alias()
    elif x==0:
        break
    else:
        print("Invalid input, please enter any one of the following: 1,2,3,4,0 only")
    y = int(input("\n\nOperation completed; Enter 0 to exit and 1 to perform another operation: "))
    if y == 0:
        break
        