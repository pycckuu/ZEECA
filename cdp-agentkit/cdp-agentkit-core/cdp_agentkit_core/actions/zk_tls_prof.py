from collections.abc import Callable

from cdp import Wallet
from pydantic import BaseModel

from cdp_agentkit_core.actions import CdpAction
from cdp.smart_contract import SmartContract


abiProver = [
    {
        "type": "function",
        "name": "main",
        "inputs": [],
        "outputs": [
            {
                "name": "",
                "type": "tuple",
                "internalType": "struct Proof",
                "components": [
                    {
                        "name": "seal",
                        "type": "tuple",
                        "internalType": "struct Seal",
                        "components": [
                            {
                                "name": "verifierSelector",
                                "type": "bytes4",
                                "internalType": "bytes4",
                            },
                            {
                                "name": "seal",
                                "type": "bytes32[8]",
                                "internalType": "bytes32[8]",
                            },
                            {
                                "name": "mode",
                                "type": "uint8",
                                "internalType": "enum ProofMode",
                            },
                        ],
                    },
                    {
                        "name": "callGuestId",
                        "type": "bytes32",
                        "internalType": "bytes32",
                    },
                    {"name": "length", "type": "uint256", "internalType": "uint256"},
                    {
                        "name": "callAssumptions",
                        "type": "tuple",
                        "internalType": "struct CallAssumptions",
                        "components": [
                            {
                                "name": "proverContractAddress",
                                "type": "address",
                                "internalType": "address",
                            },
                            {
                                "name": "functionSelector",
                                "type": "bytes4",
                                "internalType": "bytes4",
                            },
                            {
                                "name": "settleBlockNumber",
                                "type": "uint256",
                                "internalType": "uint256",
                            },
                            {
                                "name": "settleBlockHash",
                                "type": "bytes32",
                                "internalType": "bytes32",
                            },
                        ],
                    },
                ],
            }
        ],
        "stateMutability": "view",
    },
]


abiVerifier = [
    {
        "type": "function",
        "name": "verify",
        "inputs": [
            {"name": "_address", "type": "address", "internalType": "address"},
        ],
        "outputs": [],
        "stateMutability": "nonpayable",
    }
]

class ZkTlsProve(BaseModel):
    """Input argument schema for zk_tls_prove action."""


def genetate_and_verify_proof(wallet: Wallet) -> str:

    prover_contract_address = "0xcf1da21f3a697ac02c946d243e69f483c07d728d"
    verifier_contract_address = "0xde9858008f3c05c161e525af757a428c47b01983"

    proof = SmartContract.read(
        "base-sepolia",
        prover_contract_address,
        "main",
        abiProver,
    )

    try:
        invocation = wallet.invoke_contract(
            contract_address=verifier_contract_address,
            method="verify",
            args={"_address": "0xb8793E17B2da0A7E86618d9bBca6d57679a4726c"},
            abi=abiVerifier,
        ).wait()

        if invocation and invocation.transaction:
            return f"Verified and generate zkTls proof using prover contract of the CNN page {prover_contract_address} and verifier contract {verifier_contract_address} on network {wallet.network_id}.\nTransaction hash for the mint: {invocation.transaction.transaction_hash}\nTransaction link for the mint: {invocation.transaction.transaction_link}"
        else:
            return f"Verified and generate zkTls proof using prover contract {prover_contract_address} and verifier contract {verifier_contract_address} on network {wallet.network_id}, but no transaction was generated."

    except Exception as e:
        return f"Error generating and verifying zkTls proof: {e!s}"

class GenerateAndVerifyZkTlsProve(CdpAction):

    name: str = "generate_and_verify_zk_tls_proof"
    description: str = "This tool will generate, verify a zkTls proof and mint NFT of succeess."
    args_schema: type[BaseModel] | None = ZkTlsProve
    func: Callable[..., str] = genetate_and_verify_proof

