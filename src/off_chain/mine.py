import dataclasses
import json
import random
import time
from copy import copy
from hashlib import sha256
from pathlib import Path
from typing import List

import click
from pycardano import (
    OgmiosChainContext,
    TransactionBuilder,
    Redeemer,
    Network,
    ScriptHash,
    Address,
    AssetName,
    PlutusData,
    MultiAsset,
)

from src.utils import get_signing_info, ogmios_url, kupo_url
from src.utils.keys import get_or_create_address


def half_difficulty_number(a):
    new_a = a[1] // 2  # BigInt division
    if new_a < 4096:
        return (a[0] + 1, new_a * 16)
    else:
        return (a[0], new_a)


def calculate_interlink(currentHash: bytes, a, b, currentInterlink: List[bytes]):
    b_half = half_difficulty_number(b)
    interlink = currentInterlink
    currentIndex = 0

    while b_half[0] < a[0] or (b_half[0] == a[0] and b_half[1] > a[1]):
        if currentIndex < len(interlink):
            interlink[currentIndex] = currentHash
        else:
            interlink.append(currentHash)

        b_half = half_difficulty_number(b_half)
        currentIndex += 1

    return interlink


def get_difficulty(hash: bytes):
    leading_zeros = 0
    difficulty_number = 0
    for indx, chr in enumerate(hash):
        if chr != 0:
            if (chr & 0x0F) == chr:
                leading_zeros += 1
                difficulty_number += chr * 4096
                difficulty_number += hash[indx + 1] * 16
                difficulty_number += hash[indx + 2] // 16
                return leading_zeros, difficulty_number
            else:
                difficulty_number += chr * 256
                difficulty_number += hash[indx + 1]
                return leading_zeros, difficulty_number
        else:
            leading_zeros += 2
    return 32, 0


@dataclasses.dataclass
class FortunaState(PlutusData):
    nonce: bytes
    block_number: int
    current_hash: bytes
    leading_zeroes: int
    difficulty: int
    epoch_time: int


@dataclasses.dataclass
class FortunaParams(PlutusData):
    block_number: int
    current_hash: bytes
    leading_zeroes: int
    difficulty: int
    epoch_time: int
    real_time_now: int
    message: bytes
    interlink: List[bytes]


@dataclasses.dataclass
class FortunaRedeemer(PlutusData):
    CONSTR_ID = 1
    nonce: bytes


@click.command()
@click.option("--preview", is_flag=True, help="Use the preview network")
def main(preview: bool):
    network = Network.TESTNET if preview else Network.MAINNET
    # Load chain context
    context = OgmiosChainContext(ogmios_url, network=network, kupo_url=kupo_url)
    script_utxo = context.utxo_by_tx_id(
        "01751095ea408a3ebe6083b4de4de8a24b635085183ab8a2ac76273ef8fff5dd", 0
    )

    genesis_path = Path(__file__).parent.parent.parent.joinpath(
        "genesis", f"{'preview' if network == Network.TESTNET else 'mainnet'}.json"
    )
    with genesis_path.open("r") as f:
        genesis = json.load(f)

    script_hash = ScriptHash(bytes.fromhex(genesis["validatorHash"]))
    script_address = Address.from_primitive(genesis["validatorAddress"])

    # Get payment address
    payment_address = get_or_create_address("miner", network=network)

    # Request funding address
    print("Checking balance...")
    utxo = context.utxos(payment_address)
    balance = sum(u.output.amount.coin for u in utxo)
    if balance < 10_000_000:
        print(
            f"Miner address should be funded with at least 10 ADA, currently has {balance / 1_000_000} ADA"
        )
        print(f"Send funds to {payment_address} to proceed")
        while balance < 10_000_000:
            utxo = context.utxos(payment_address)
            balance = sum(u.output.amount.coin for u in utxo)
            time.sleep(5)
    print(f"Found {balance / 1_000_000} ADA in miner address")

    validator_out_ref = None
    print("Mining...")
    last_time = 0
    nonce = int.from_bytes(random.randbytes(16), "big")
    i = 0
    while True:
        i += 1
        if time.time() - last_time > 10:
            print(f"New block not found in 10 seconds, updating state after {i} tries")
            i = 0
            last_time = time.time()
            validator_out_ref_new = [
                u
                for u in context.utxos(script_address)
                if u.output.amount.multi_asset.get(script_hash).get(
                    AssetName(b"lord tuna")
                )
            ][0]

            if validator_out_ref_new != validator_out_ref:
                validator_out_ref = [
                    u
                    for u in context.utxos(script_address)
                    if u.output.amount.multi_asset.get(script_hash).get(
                        AssetName(b"lord tuna")
                    )
                ][0]

                validator_state = FortunaParams.from_cbor(
                    validator_out_ref.output.datum.cbor
                )
                assert validator_state is not None, "Datum is missing"
                target_state = FortunaState(
                    nonce=nonce.to_bytes(16, "big"),
                    block_number=validator_state.block_number,
                    current_hash=validator_state.current_hash,
                    leading_zeroes=validator_state.leading_zeroes,
                    difficulty=validator_state.difficulty,
                    epoch_time=validator_state.epoch_time,
                )
        target_state.nonce = nonce.to_bytes(16, "big")
        target_hash = sha256(sha256(target_state.to_cbor()).digest()).digest()
        leading_zeroes, difficulty = get_difficulty(target_hash)
        if leading_zeroes > target_state.leading_zeroes or (
            leading_zeroes == target_state.leading_zeroes
            and difficulty < target_state.difficulty
        ):
            break
        nonce += 1

    print(f"Found block with nonce {nonce}")
    realtimenow = int(time.time()) * 1000 - 60000
    interlink = calculate_interlink(
        target_hash,
        (leading_zeroes, difficulty),
        (validator_state.leading_zeroes, validator_state.difficulty),
        validator_state.interlink,
    )

    epoch_time = (
        (validator_state.difficulty)
        + (realtimenow + 90000)
        - validator_state.epoch_time
    )
    difficulty_number = validator_state.difficulty
    leading_zeroes = validator_state.leading_zeroes
    if validator_state.block_number % 2016 == 0 and validator_state.block_number > 0:
        adjustment = get_difficulty_adjustment(epoch_time, 1_209_600_000)
        epoch_time = 0
        difficulty_number, leading_zeroes = calculate_difficulty(
            (validator_state.leading_zeroes, validator_state.difficulty),
            adjustment,
        )

    post_datum = FortunaParams(
        block_number=validator_state.block_number + 1,
        current_hash=target_hash,
        leading_zeroes=leading_zeroes,
        difficulty=difficulty_number,
        epoch_time=epoch_time,
        real_time_now=90_000_000 + realtimenow,
        message=b"AlL HaIl tUnA",
        interlink=interlink,
    )

    # Make redeemer
    redeemer = Redeemer(FortunaRedeemer(nonce.to_bytes(16, "big")))

    # Build the transaction
    builder = TransactionBuilder(context)
    builder.add_script_input(validator_out_ref, script=script_utxo, redeemer=redeemer)
    # we must specify at least the start of the tx valid range in slots
    builder.validity_start = realtimenow
    # This specifies the end of tx valid range in slots
    builder.ttl = builder.validity_start + 1000
    builder.add_minting_script(script_utxo, Redeemer(PlutusData()))
    builder.mint = MultiAsset({script_hash: {AssetName(b"TUNA"): 5_000_000_000}})
    new_output = copy(validator_out_ref.output)
    new_output.datum = post_datum
    builder.add_output(new_output)

    # Sign the transaction
    payment_vkey, payment_skey, _ = get_signing_info("miner")
    signed_tx = builder.build_and_sign(
        signing_keys=[payment_skey],
        change_address=payment_address,
    )

    # Submit the transaction
    context.submit_tx(signed_tx.to_cbor())

    # context.submit_tx(signed_tx.to_cbor())
    print(f"transaction id: {signed_tx.id}")
    if network == Network.TESTNET:
        print(f"Cexplorer: https://preview.cexplorer.io/tx/{signed_tx.id}")
    else:
        print(f"Cexplorer: https://cexplorer.io/tx/{signed_tx.id}")


if __name__ == "__main__":
    main()
