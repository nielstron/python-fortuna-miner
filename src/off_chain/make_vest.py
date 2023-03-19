import subprocess
import time
from pathlib import Path

import click
from pycardano import (
    OgmiosChainContext,
    Network,
    Address,
    TransactionBuilder,
    TransactionOutput,
    VerificationKeyHash,
    PlutusData,
)

from src.on_chain import vesting


@click.command()
@click.argument("name")
@click.argument("beneficiary")
@click.option(
    "--amount",
    type=int,
    default=3000000,
    help="Amount of lovelace to send to the script address.",
)
@click.option(
    "--wait_time",
    type=int,
    default=0,
    help="Time to wait in seconds for the validation to succeed.",
)
@click.option("--ogmios", default="localhost:1337", help="Set the ogmios host")
def main(name: str, beneficiary: str, amount: int, wait_time: int, ogmios: str):
    # Load chain context
    context = OgmiosChainContext(f"ws://{ogmios}", network=Network.TESTNET)

    # Get payment address
    payment_address = get_address(name)

    # Get the beneficiary VerificationKeyHash (PubKeyHash)
    beneficiary_address = get_address(beneficiary)
    vkey_hash: VerificationKeyHash = beneficiary_address.payment_part

    # Create the vesting datum
    params = vesting.VestingParams(
        beneficiary=bytes(vkey_hash),
        deadline=int(time.time() + wait_time) * 1000,  # must be in milliseconds
    )

    script_path = Path("./build/vesting/testnet.addr")

    # Load script info
    with open(script_path) as f:
        script_address = Address.from_primitive(f.read())

    # Make datum
    datum = params

    # Build the transaction
    builder = TransactionBuilder(context)
    builder.add_input_address(payment_address)
    builder.add_output(
        TransactionOutput(address=script_address, amount=amount, datum=datum)
    )

    # Sign the transaction
    payment_vkey, payment_skey, payment_address = get_signing_info(name)
    signed_tx = builder.build_and_sign(
        signing_keys=[payment_skey],
        change_address=payment_address,
    )

    # Submit the transaction
    context.submit_tx(signed_tx.to_cbor())

    print(f"transaction id: {signed_tx.id}")
    print(f"Cardanoscan: https://preview.cardanoscan.io/transaction/{signed_tx.id}")


if __name__ == "__main__":
    main()
