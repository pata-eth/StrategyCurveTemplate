from brownie import StrategyCurveTwoPool, accounts, config, Contract, convert, network
import click

activeNetwork = network.show_active()

assert "arb" in activeNetwork, f"Strategy meant to be deployed to Arbitrum only."


def main():

    vaultAddress = convert.to_address("0x49448d2B94fb9C4e41a30aD8315D32f46004A34b")

    print(f"You are deploying the strategy to the '{activeNetwork}' network")
    dev = accounts.load(click.prompt("Account", type=click.Choice(accounts.load())))
    print(f"You are using: 'dev' [{dev.address}]")

    apiVersion = config["dependencies"][0].split("@")[-1]

    # Vault contract created with './deploy_vault.py'
    vault = Contract(vaultAddress, owner=dev)

    # strategy API version must align with vault version
    assert vault.apiVersion() == apiVersion

    print(
        f"""
    Strategy Parameters

       api: {apiVersion}
     token: {vault.token()}
      name: '{vault.name()}'
    symbol: '{vault.symbol()}'
    """
    )

    publish_source = click.confirm("Verify source on arbiscan?")

    strategy = StrategyCurveTwoPool.deploy(
        vault.address,
        config["strategy"]["name"],
        {"from": dev},
        publish_source=publish_source,
    )

    # By default, the `strategist`, `rewards` and `keeper` addresses are initialized to `dev`
    # We update `keeper` and `rewards`. Only the strategist or governance can make this change.
    strategy.setKeeper(
        convert.to_address("0x1DEb47dCC9a35AD454Bf7f0fCDb03c09792C08c1"), {"from": dev}
    )

    # Only the strategist can make this change.
    strategy.setRewards(
        convert.to_address("0x1DEb47dCC9a35AD454Bf7f0fCDb03c09792C08c1"), {"from": dev}
    )

    print(f"Strategy created at {strategy.address}")
