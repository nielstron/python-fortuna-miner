# Python Fortuna Miner

This repo provides basic code to mine [Fortuna on Cardano](https://github.com/aiken-lang/fortuna).

PyCardano is a Cardano library written in Python. It allows users to create and sign transactions without depending on third-party Cardano serialization tools, such as cardano-cli and cardano-serialization-lib, making it a lightweight library, which is simple and fast to set up in all types of environments.

opshin is a Smart Contract language based on Python. It allows users to define and compile Smart Contracts directly within a python environment.
It also interacts seemlessly with PyCardano.

## Dev Environment

For executing the scripts in this starter kit you'll need access to a running [Ogmios](https://ogmios.dev/) instance.

In case you don't want to install the required components yourself, you can use [Demeter.run](https://demeter.run) platform to create a cloud environment with access to common Cardano infrastructure. The following command will open this repo in a private, web-based VSCode IDE with access to a running Ogmios instance in the preview network.

[![Code in Cardano Workspace](https://demeter.run/code/badge.svg)](https://demeter.run/code?repository=https://github.com/opshin/opshin-starter-kit.git&template=python&source=demeter&key=opshin-starter-kit)


## Setup


1. Install Python 3.8, 3.9 or 3.10.

On demeter.run or Linux/Ubuntu, this version of python is usually already pre-installed. You can skip this step.
For other Operating Systems, you can download the installer [here](https://www.python.org/downloads/release/python-3810/).

2. Ensure `python3 --version` works in your command line. Open a Terminal in the browser VSCode interface (F1 -> Terminal: Create New Terminal)
In Windows, you can do this by copying the `python.exe` file to `python3.exe` in your `PATH` environment variable.

3. Install python poetry.

On demeter.run or Linux/Ubuntu run 
```bash
curl -sSL https://install.python-poetry.org | python3 -
echo 'export PATH=/config/.local/bin:$PATH' >> ~/.bashrc
bash
```

Otherwise, follow the official documentation [here](https://python-poetry.org/docs/#installation).


4. Install a python virtual environment with poetry:
```bash
# install python dependencies
poetry install
# run a shell with the virtual environment activated
poetry shell
```

5. Set up [ogmios](https://ogmios.dev/) and optionally [kupo](https://cardanosolutions.github.io/kupo/). 

On demeter.run, simply add the Ogmios Extension for the Preview network
through the project console website (the page that shows you demeter.run project -> Connected Extensions -> Browse Extensions -> Cardano Ogmios)
If you want to add kupo, use the Kupo Extension as well.

Make sure the following environment variables are set (defaults are displayed):

```bash
OGMIOS_URL=ws://localhost:1337

KUPO_URL=http://localhost:80
```

## Running the scripts

> Fair warning: this code handles cryptocurrency. Make sure to read the code and understand what it does before running it.
> There is always a risk of loosing part of or all of your funds when interacting with tools that handle crypto wallets for you.

If you want to know how to start the miner, please read the code and ensure yourself that it properly handles your funds.
Hence, it is not recommended to simply run the script like this:

```bash
python3 src/off_chain/mine.py
```

This will start the miner, show you a locally generated address that needs to be funded and then donate all funds to OpShin and PyCardano development.
Contact me or the OpShin team if you are reading this after donating larger amounts than you are comfortable with.
