import pytest

from starknet_py.net.client_models import TransactionStatusResponse, TransactionStatus
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.networks import TESTNET, MAINNET


@pytest.mark.asyncio
async def test_gateway_raises_on_both_block_hash_and_number(
    block_with_deploy_hash, gateway_client
):
    with pytest.raises(ValueError) as exinfo:
        await gateway_client.get_block(
            block_hash=block_with_deploy_hash, block_number=0
        )

    assert "block_hash and block_number parameters are mutually exclusive" in str(
        exinfo.value
    )


@pytest.mark.asyncio
async def test_get_class_hash_at(contract_address, gateway_client):
    class_hash = await gateway_client.get_class_hash_at(
        contract_address=contract_address
    )

    assert (
        class_hash
        == 3197248528421459336430560285234479619486870042069853528940753151314137720584
    )


@pytest.mark.asyncio
async def test_get_code(contract_address, gateway_client):
    code = await gateway_client.get_code(contract_address=contract_address)

    assert code.abi is not None
    assert len(code.abi) != 0
    assert code.bytecode is not None
    assert len(code.bytecode) != 0


@pytest.mark.asyncio
async def test_get_transaction_status(invoke_transaction_hash, gateway_client):
    tx_status_resp = await gateway_client.get_transaction_status(
        invoke_transaction_hash
    )
    assert isinstance(tx_status_resp, TransactionStatusResponse)
    assert tx_status_resp.transaction_status == TransactionStatus.ACCEPTED_ON_L2
    assert isinstance(tx_status_resp.block_hash, int)


# pylint: disable=protected-access
@pytest.mark.parametrize(
    "net, net_address, chain",
    (
        (TESTNET, "https://alpha4.starknet.io", StarknetChainId.TESTNET),
        (MAINNET, "https://alpha-mainnet.starknet.io", StarknetChainId.MAINNET),
    ),
)
def test_creating_client_from_predefined_network(net, net_address, chain):
    gateway_client = GatewayClient(net=net)

    assert gateway_client.net == net
    assert gateway_client._feeder_gateway_client.url == f"{net_address}/feeder_gateway"
    assert gateway_client._gateway_client.url == f"{net_address}/gateway"
    assert gateway_client.chain == chain


def test_creating_client_with_custom_net():
    custom_net = "custom.net"
    gateway_client = GatewayClient(net=custom_net, chain=StarknetChainId.TESTNET)

    assert gateway_client.net == custom_net
    assert gateway_client._feeder_gateway_client.url == f"{custom_net}/feeder_gateway"
    assert gateway_client._gateway_client.url == f"{custom_net}/gateway"
    assert gateway_client.chain == StarknetChainId.TESTNET


def test_creating_client_with_custom_net_dict():
    custom_net = "custom.net"
    net = {
        "feeder_gateway_url": f"{custom_net}/feeder_gateway",
        "gateway_url": f"{custom_net}/gateway",
    }

    gateway_client = GatewayClient(net=net, chain=StarknetChainId.TESTNET)

    assert gateway_client.net == net
    assert gateway_client._feeder_gateway_client.url == net["feeder_gateway_url"]
    assert gateway_client._gateway_client.url == net["gateway_url"]
    assert gateway_client.chain == StarknetChainId.TESTNET


@pytest.mark.parametrize(
    "net",
    (
        {
            "feeder_gateway_url": "custom.net/feeder_gateway",
            "gateway_url": "custom.net/gateway",
        },
        "custom.net",
    ),
)
def test_throwing_on_custom_net_without_chain(net):
    with pytest.raises(ValueError) as err:
        GatewayClient(net=net)

    assert "Chain is required when not using predefined networks." == str(err.value)