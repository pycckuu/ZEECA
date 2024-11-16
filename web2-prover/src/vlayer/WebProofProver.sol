// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Strings} from "@openzeppelin-contracts-5.0.1/utils/Strings.sol";

import {Proof} from "vlayer-0.1.0/Proof.sol";
import {Prover} from "vlayer-0.1.0/Prover.sol";
import {Web, WebProof, WebProofLib, WebLib} from "vlayer-0.1.0/WebProof.sol";

contract WebProofProver is Prover {
    using Strings for string;
    using WebProofLib for WebProof;
    using WebLib for Web;


    string constant DATA_URL = "https://raw.githubusercontent.com/brandly/presidential-election-data/refs/heads/master/json/2020.json";

    function main()
        public
        view
        returns (Proof memory)
    {
        // require(msg.sender == agentProoverAddress, "Only Agent account can prove");

        // Web memory web = webProof.verify(DATA_URL);
        // int256 democratVotes = web.jsonGetInt("votes.AL.popular.democrat");
        // int256 republicanVotes = web.jsonGetInt("votes.AL.popular.republican");
        // require(republicanVotes > democratVotes, "Republican votes must be greater than Democrat votes");

        return (proof());
    }
}


