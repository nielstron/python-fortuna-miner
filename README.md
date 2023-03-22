# OpShin Starter-kit

This Starter-Kit is a small tutorial of how to use the [PyCardano](https://github.com/Python-Cardano/pycardano) library 
with [opshin](https://github.com/OpShin/opshin) for interacting with a simple vesting contract on Cardano.

PyCardano is a Cardano library written in Python. It allows users to create and sign transactions without depending on third-party Cardano serialization tools, such as cardano-cli and cardano-serialization-lib, making it a lightweight library, which is simple and fast to set up in all types of environments.

opshin is a Smart Contract language based on Python. It allows users to define and compile Smart Contracts directly within a python environment.
It also interacts seemlessly with PyCardano.

## Dev Environment

For executing the scripts in this starter kit you'll need access to a running [Ogmios](https://ogmios.dev/) instance.

In case you don't want to install the required components yourself, you can use [Demeter.run](https://demeter.run) platform to create a cloud environment with access to common Cardano infrastructure. The following command will open this repo in a private, web-based VSCode IDE with access to a running Ogmios instance in the preview network.

[![Code in Cardano Workspace](https://demeter.run/code/badge.svg)](https://demeter.run/code?repository=https://github.com/opshin/opshin-starter-kit&template=python)


## What is Included

We have included a number of python scripts for executing specific actions.
You can find scripts to initialize addresses and interact with the cardano-node in `scripts`.
`src` contains two folders, `on_chain` which hosts the actual opshin contract and `off-chain` which
hosts tooling to interact with the contract.


## Setup


1. Install Python 3.8.
Installer [download](https://www.python.org/downloads/release/python-3810/)

On demeter.run follow these instructions:
 - open a Terminal in the browser VSCode interface (F1 -> Terminal: Create New Terminal)
 - `wget https://www.python.org/ftp/python/3.8.10/Python-3.8.10.tgz`
 - `tar -xf Python-3.8.10.tgz`
 - `cd Python-3.8.10 && ./configure --prefix=/config/.local`
 - `make -j 8`
 - `make install`
 - `echo 'export PATH=/config/.local/bin:$PATH' >> ~/.bashrc`
 - `bash`

2. Ensure `python3.8 --version` works in your command line.
In Windows, you can do this by copying the `python.exe` file to `python3.8.exe` in your `PATH` environment variable.

3. Install python poetry.
Follow the official documentation [here](https://python-poetry.org/docs/#installation).

4. Install a python virtual environment with poetry:
```bash
# install python dependencies
poetry install
# run a shell with the virtual environment activated
poetry shell
```

5. Set up ogmios. On demeter.run, ogmios is already configured for you and the defaults in this repository will assume a Demeter.Run ogmios instance.

## Running the scripts

Once you have entered the poetry shell, you can start interacting with the contract through the prepared scripts.

First, we have to build the vesting contract and generate two key pairs, one for the
owner of funds and one for the intended beneficiary.

```bash
python3 src/off_chain/build.py
python3 scripts/create_key_pair.py owner
python3 scripts/create_key_pair.py beneficiary
```

Make sure that the beneficiary address is loaded up with some testnet ada before proceeding,
by using the [testnet faucet](https://docs.cardano.org/cardano-testnet/tools/faucet).

Then you can place a vested amount of ada at the contract

```bash
python3 src/off_chain/make_vest.py owner beneficiary 
```

By default the deadline is 0 seconds after the creation of the vesting, so you can directly proceed and unlock
the vested amount with the beneficiary!

```bash
python3 src/off_chain/collect_vest.py beneficiary
```

That's it! You successfully compiled a Smart Contract on cardano and interacted with it through off-chain tooling.
Feel free to dive into the provided scripts and start customizing them for your needs.
