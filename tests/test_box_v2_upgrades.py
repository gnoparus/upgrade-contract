from scripts.helpful_scripts import (
    encode_function_data,
    get_account,
    get_contract,
    upgrade,
)
from brownie import (
    Box,
    BoxV2,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
    exceptions,
)
import pytest


def test_proxy_upgrades():
    account = get_account()
    box = Box.deploy({"from": account})
    proxy_admin = ProxyAdmin.deploy({"from": account})
    box_encoded_initializer_function = encode_function_data()
    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer_function,
        {"from": account, "gas_limit": 1000000},
    )

    print(f"Deploying BoxV2")
    box_v2 = BoxV2.deploy({"from": account})
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)

    with pytest.raises(exceptions.VirtualMachineError):
        proxy_box.increment(
            {"from": account, "gas_limit": 1000000, "allow_revert": True}
        )

    upgrade_transaction = upgrade(
        account, proxy, box_v2.address, proxy_admin_contract=proxy_admin
    )
    value = proxy_box.retrieve({"from": account})
    assert value == 0
    upgrade_transaction.wait(1)
    proxy_box.increment({"from": account})
    assert proxy_box.retrieve() == value + 1
