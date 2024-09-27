from web3 import Web3

# Connect to Ganache (or your preferred network)
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))  # Ganache URL

# Check connection to the Ethereum node
if w3.is_connected():
    print("Connected to the Ethereum node.")
else:
    print("Failed to connect to the Ethereum node.")

# Replace with your RentalContract address and ABI
contract_address = Web3.to_checksum_address('0x5d84a2c3a700422cc76b7b5197da40e9e29c0393')  # Replace with your contract address
contract_abi = [
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "_monthlyRent",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "_securityDeposit",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "_rentalPeriod",
                "type": "uint256"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "inputs": [],
        "name": "endRental",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "isActive",
        "outputs": [
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "landlord",
        "outputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "monthlyRent",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "payRent",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "rentalPeriod",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "securityDeposit",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "startRental",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "startTimestamp",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "tenant",
        "outputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

# Connect to the contract
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Set your account for sending transactions
# account = w3.eth.accounts[0]  # First account on Ganache (change this if needed)
account = Web3.to_checksum_address('0x71Afec87a81478ec2fbF3936D41c05F65FbA7A96')  # Your account address


def start_rental():
    is_active = contract.functions.isActive().call()
    if is_active:
        print("Error: Rental is already active. Please end the current rental first.")
        return

    print("Starting rental...")
    security_deposit = contract.functions.securityDeposit().call()
    tx_hash = contract.functions.startRental().transact({'from': account, 'value': security_deposit})
    w3.eth.wait_for_transaction_receipt(tx_hash)
    print("Rental started successfully.")


def pay_rent():
    is_active = contract.functions.isActive().call()
    if not is_active:
        print("Error: Rental is not active. Please start a rental first.")
        return

    # Get the current timestamp and start timestamp
    current_time = w3.eth.get_block('latest')['timestamp']
    start_timestamp = contract.functions.startTimestamp().call()
    rental_period = contract.functions.rentalPeriod().call()
    
    # Calculate the expected end timestamp
    expected_end_time = start_timestamp + (rental_period * 30 * 24 * 60 * 60)  # assuming rentalPeriod is in months

    # Check if the current time is beyond the expected end time
    if current_time >= expected_end_time:
        print("Error: Rental period has ended. You cannot pay rent.")
        return

    # Check if the rent for the current month has already been paid
    last_payment_time = contract.functions.startTimestamp().call()  # Replace with your actual method to get last payment time
    if current_time < last_payment_time + (30 * 24 * 60 * 60):  # assuming monthly rent payment
        print("Error: Rent for the current month has already been paid.")
        return

    monthly_rent = contract.functions.monthlyRent().call()
    print(f"Paying rent: {monthly_rent} Wei...")
    try:
        tx_hash = contract.functions.payRent().transact({'from': account, 'value': monthly_rent})
        w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Rent paid successfully. Transaction hash: {tx_hash.hex()}")
    except Exception as e:
        print(f"Error paying rent: {e}")



def end_rental():
    is_active = contract.functions.isActive().call()
    if not is_active:
        print("Error: Rental is not active. You cannot end a rental that has not started.")
        return

    # Get the current timestamp and rental start timestamp
    current_time = w3.eth.get_block('latest')['timestamp']
    start_timestamp = contract.functions.startTimestamp().call()
    rental_period = contract.functions.rentalPeriod().call()

    # Calculate the expected end timestamp
    expected_end_time = start_timestamp + (rental_period * 30 * 24 * 60 * 60)  # assuming rentalPeriod is in months

    if current_time < expected_end_time:
        print("Error: Cannot end rental before the rental period.")
        return

    print("Ending rental...")
    try:
        tx_hash = contract.functions.endRental().transact({'from': account})
        w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Rental ended successfully. Transaction hash: {tx_hash.hex()}")
    except Exception as e:
        print(f"Error ending rental: {e}")



def get_rental_info():
    landlord_address = contract.functions.landlord().call()
    tenant_address = contract.functions.tenant().call()
    monthly_rent = contract.functions.monthlyRent().call()
    security_deposit = contract.functions.securityDeposit().call()
    rental_period = contract.functions.rentalPeriod().call()
    is_active = contract.functions.isActive().call()

    print(f"Expected Security Deposit: {security_deposit} Wei")
    print(f"Landlord: {landlord_address}")
    print(f"Tenant: {tenant_address}")
    print(f"Monthly Rent: {monthly_rent} Wei")
    print(f"Rental Period: {rental_period} months")
    print(f"Is Active: {is_active}")

# Main interaction loop
while True:
    command = input("Enter 'start' to start rental, 'pay' to pay rent, 'end' to end rental, 'info' to get rental info (or 'exit' to quit): ")
    
    if command.lower() == 'start':
        start_rental()
    elif command.lower() == 'pay':
        pay_rent()
    elif command.lower() == 'end':
        end_rental()
    elif command.lower() == 'info':
        get_rental_info()
    elif command.lower() == 'exit':
        print("Exiting...")
        break
    else:
        print("Invalid command. Please try again.")
