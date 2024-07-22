import sys

import pytest

from starknet_py.contract import Contract
from starknet_py.net.client_errors import ClientError


@pytest.mark.skipif(
    "--contract_dir=v1" in sys.argv,
    reason="Contract exists only in v2 directory",
)
@pytest.mark.asyncio
async def test_impersonate_account(
    devnet_forking_mode_client, account_impersonated, f_string_contract
):
    await devnet_forking_mode_client.impersonate_account(
        address=account_impersonated.address
    )

    contract = await Contract.from_address(
        provider=account_impersonated, address=f_string_contract.address
    )

    invocation = await contract.functions["set_string"].invoke_v1(
        "test", auto_estimate=True
    )

    await devnet_forking_mode_client.stop_impersonate_account(
        address=account_impersonated.address
    )

    assert invocation.invoke_transaction.sender_address == account_impersonated.address


@pytest.mark.skipif(
    "--contract_dir=v1" in sys.argv,
    reason="Contract exists only in v2 directory",
)
@pytest.mark.asyncio
async def test_auto_impersonate(
    devnet_forking_mode_client, account_impersonated, f_string_contract
):
    await devnet_forking_mode_client.auto_impersonate()

    contract = await Contract.from_address(
        provider=account_impersonated, address=f_string_contract.address
    )

    invocation = await contract.functions["set_string"].invoke_v1(
        "test", auto_estimate=True
    )

    await devnet_forking_mode_client.stop_auto_impersonate()

    assert invocation.invoke_transaction.sender_address == account_impersonated.address


@pytest.mark.skipif(
    "--contract_dir=v1" in sys.argv,
    reason="Contract exists only in v2 directory",
)
@pytest.mark.asyncio
async def test_impersonated_account_should_fail(
    account_impersonated, f_string_contract
):
    contract = await Contract.from_address(
        provider=account_impersonated, address=f_string_contract.address
    )

    try:
        await contract.functions["set_string"].invoke_v1("test", auto_estimate=True)
        assert False
    except ClientError:
        assert True