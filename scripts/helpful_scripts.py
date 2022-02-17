import eth_utils
from brownie import (
    network,
    config,
    accounts,
    interface,
)
from web3 import Web3


FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]


def get_account(index=None, id=None):

    if index:
        return accounts[index]
    if id:
        return accounts.load(id)

    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        # use generaged fake account
        return accounts[0]

    # use mm account saved in brownie-config
    return accounts.add(config["wallets"]["from_key"])


def get_contract(contract_name):
    contract_type = contract_to_mock[contract_name]

    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        # MockV3Aggregator[-1 ] , VRFCoordinatorMock , LinkToken
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract

    # return {        _priceFeedAddress,
    #      _vrfCoordinator,
    #      _link,
    #      _fee,
    #      _keyHash,
    #     "from": account}


def upgrade(
    account,
    proxy,
    new_incrementaion_address,
    proxy_admin_contract=None,
    initializer=None,
    *args,
):
    if proxy_admin_contract:
        if initializer:
            encoded_function_call = encode_function_data(initializer, *args)
            transaction = proxy_admin_contract.upgradeAndCall(
                proxy.address,
                new_incrementaion_address,
                encoded_function_call,
                {"from": account},
            )
        else:
            transaction = proxy_admin_contract.upgrade(
                proxy.address,
                new_incrementaion_address,
                {"from": account},
            )
    else:
        if initializer:
            encoded_function_call = encode_function_data(initializer, *args)
            transaction = proxy.upgradeAndCall(
                new_incrementaion_address,
                encoded_function_call,
                {"from": account},
            )
        else:
            transaction = proxy.upgradeTo(
                new_incrementaion_address,
                {"from": account},
            )
    return transaction


def encode_function_data(initializer=None, *args):
    if len(args) == 0 or not initializer:
        return eth_utils.to_bytes(hexstr="0x")
    return initializer.encode_input(*args)
