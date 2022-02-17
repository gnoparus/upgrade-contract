from scripts.helpful_scripts import (
    get_account,
    get_contract,
    encode_function_data,
    upgrade,
)
from brownie import (
    Box,
    BoxV2,
    network,
    config,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
)
from web3 import Web3


def main():
    account = get_account()
    print(f"Deploying box to {network.show_active()}")
    box = Box.deploy({"from": account})

    proxy_admin = ProxyAdmin.deploy({"from": account})
    initializer = box.store, 1000
    box_encoded_initializer_function = encode_function_data(initializer=initializer)

    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {"from": account, "gas_limit": 1000000},
    )
    print(f"Proxy deployed to {proxy}, you can now upgrade to V2.")
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)

    val = proxy_box.retrieve()
    print(f"val = {val}")

    proxy_box.store(3, {"from": account})
    print(f"Stored 3")

    val = proxy_box.retrieve()
    print(f"val = {val}")

    ### Error because Box has no increment function
    # proxy_box.increment()

    val = proxy_box.retrieve()
    print(f"val = {val}")

    box_v2 = BoxV2.deploy({"from": account})
    initializer2 = box_v2.store, 2000
    upgrade_transaction = upgrade(
        account, proxy, box_v2.address, proxy_admin_contract=proxy_admin
    )
    upgrade_transaction.wait(1)
    print(f"Proxy has been upgraded")

    val = proxy_box.retrieve()
    print(f"val = {val}")

    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    print(f"Calling increment")
    proxy_box.increment({"from": account})

    val = proxy_box.retrieve()
    print(f"val = {val}")
