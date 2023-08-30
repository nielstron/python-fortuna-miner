from pathlib import Path

from pycardano import PaymentVerificationKey, PaymentSigningKey, Address, Network

keys_dir = Path(__file__).parent.parent.parent.joinpath("keys")


def get_address(name) -> Address:
    with open(keys_dir.joinpath(f"{name}.addr")) as f:
        address = Address.from_primitive(f.read())
    return address


def get_signing_info(name, network=Network.TESTNET):
    skey_path = str(keys_dir.joinpath(f"{name}.skey"))
    payment_skey = PaymentSigningKey.load(skey_path)
    payment_vkey = PaymentVerificationKey.from_signing_key(payment_skey)
    payment_address = Address(payment_vkey.hash(), network=network)
    return payment_vkey, payment_skey, payment_address


def get_or_create_address(name, network=Network.TESTNET) -> Address:
    keys_dir.mkdir(exist_ok=True)

    skey_path = keys_dir.joinpath(f"{name}.skey")
    vkey_path = keys_dir.joinpath(f"{name}.vkey")
    addr_path = keys_dir.joinpath(f"{name}.addr")

    if addr_path.exists():
        return get_address(name)

    if skey_path.exists():
        raise FileExistsError(f"signing key file ${skey_path} already exists")
    if vkey_path.exists():
        raise FileExistsError(f"verification key file ${vkey_path} already exists")
    if addr_path.exists():
        raise FileExistsError(f"address file ${addr_path} already exists")

    signing_key = PaymentSigningKey.generate()
    signing_key.save(str(skey_path))

    verification_key = PaymentVerificationKey.from_signing_key(signing_key)
    verification_key.save(str(vkey_path))

    address = Address(payment_part=verification_key.hash(), network=network)
    with open(addr_path, mode="w") as f:
        f.write(str(address))

    print(f"wrote signing key to: {skey_path}")
    print(f"wrote verification key to: {vkey_path}")
    print(f"wrote address to: {addr_path}")
    return address
