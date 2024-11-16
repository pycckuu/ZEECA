import { createVlayerClient } from "@vlayer/sdk";
import proverSpec from "../out/WebProofProver.sol/WebProofProver";
import verifierSpec from "../out/WebProofVerifier.sol/WebProofVerifier";
import tls_proof from "./tls_proof.json";
import * as assert from "assert";
import { encodePacked, isAddress, keccak256 } from "viem";

import fs from "fs";

import {
  getConfig,
  createContext,
  deployVlayerContracts,
  writeEnvVariables,
} from "@vlayer/sdk/config";

const notaryPubKey =
  "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAExpX/4R4z40gI6C/j9zAM39u58LJu\n3Cx5tXTuqhhu/tirnBi5GniMmspOTEsps4ANnPLpMmMSfhJ+IFHbc3qVOA==\n-----END PUBLIC KEY-----\n";



const DEPLOYER = "0xb8793E17B2da0A7E86618d9bBca6d57679a4726c"


  const { prover, verifier } = await deployVlayerContracts({
  proverSpec,
  verifierSpec,
});

writeEnvVariables(".env", {
  VITE_PROVER_ADDRESS: prover,
  VITE_VERIFIER_ADDRESS: verifier,
});

// // Load contract addresses from .env
// const prover = process.env.VITE_PROVER_ADDRESS as `0x${string}`;
// const verifier = process.env.VITE_VERIFIER_ADDRESS as `0x${string}`;

if (!prover || !verifier) {
  throw new Error("Missing VITE_PROVER_ADDRESS or VITE_VERIFIER_ADDRESS in .env file");
}

console.log(`Prover: ${prover}`);
console.log(`Verifier: ${verifier}`);

const config = getConfig();
const { chain, ethClient, account, proverUrl, confirmations } =
  await createContext(config);

const vlayer = createVlayerClient({
  url: proverUrl,
});

await testSuccessProvingAndVerification();

async function testSuccessProvingAndVerification() {
  console.log("Proving...");

  const webProof = { tls_proof: tls_proof, notary_pub_key: notaryPubKey };

  const hash = await vlayer.prove({
    address: prover,
    functionName: "main",
    proverAbi: proverSpec.abi,
    args: [
    ],
    chainId: 84532,
  });
  const result = await vlayer.waitForProvingResult(hash);
  const [proof] = result;
  const proofJson = JSON.stringify(proof, (_, value) =>
    typeof value === 'bigint' ? value.toString() : value
  );
  console.log(proofJson);
  fs.writeFileSync("proof.json", proofJson);
  console.log("Has Proof");

  // if (!isAddress(address)) {
  //   throw new Error(`${address} is not a valid address`);
  // }

  console.log("Verifying...");

  const txHash = await ethClient.writeContract({
    address: verifier,
    abi: verifierSpec.abi,
    functionName: "verify",
    args: [DEPLOYER],
    chain,
    account: account,
  });

  await ethClient.waitForTransactionReceipt({
    hash: txHash,
    confirmations,
    retryCount: 60,
    retryDelay: 1000,
  });

  console.log("Verified!");

}

