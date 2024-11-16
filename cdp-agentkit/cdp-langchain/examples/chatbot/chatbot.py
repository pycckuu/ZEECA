import os
import sys
import time
from typing import Dict, Any, Optional
import json


from cdp import Wallet
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain.agents import Tool
from langchain_community.document_loaders import WebBaseLoader

from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper
from cdp.smart_contract import SmartContract

# Configuration constants
WALLET_DATA_FILE = "wallet_data.txt"
THREAD_ID = "ZEECA — ZK & TEE Enabled Enforce Compliance Agent"
MODEL_NAME = "gpt-4o"


def load_webpage(url: str) -> str:
    """Load and return content from a webpage."""
    loader = WebBaseLoader(url)
    docs = loader.load()
    return docs[0].page_content


def save_wallet_data(wallet_data: str) -> None:
    """Save wallet data to file."""
    with open(WALLET_DATA_FILE, "w") as f:
        f.write(wallet_data)


def initialize_agent():
    """Initialize the agent with CDP Agentkit."""
    llm = ChatOpenAI(model=MODEL_NAME)
    agentkit = CdpAgentkitWrapper()

    wallet_data = agentkit.export_wallet()

    save_wallet_data(wallet_data)

    cdp_toolkit = CdpToolkit.from_cdp_agentkit_wrapper(agentkit)
    tools = cdp_toolkit.get_tools()

    agentkit.wallet.create_address()

    web_loader_tool = Tool(
        name="webpage_loader",
        description="Load and read content from a webpage. Input should be a valid URL.",
        func=load_webpage,
    )
    tools.append(web_loader_tool)

    memory = MemorySaver()
    config = {"configurable": {"thread_id": THREAD_ID}}

    return (
        create_react_agent(
            llm,
            tools=tools,
            checkpointer=memory,
        ),
        config,
    )


def get_autonomous_instructions() -> str:
    """Return the instructions for autonomous mode."""
    return (
        "Follow these steps carefully and provide detailed output for each:\n"
        "but important! do not output the content of the urls you visited\n"
        "1. Visit and analyze CNN's election results page at "
        "https://edition.cnn.com/election/2024/results/president?"
        "election-data-id=2024-PG&election-painting-mode=projection-with-lead&"
        "filter-key-races=false&filter-flipped=false&filter-remaining=false\n"
        "   - Report the current vote counts and percentages for each candidate\n"
        "   - Identify which states have reported and their results\n"
        "   - Calculate the electoral vote distribution\n\n"
        "2. Based on the results:\n"
        "   If Republican candidate is leading:\n"
        "   - Check https://gop.com/\n"
        "   - Summarize key policy positions and campaign updates\n"
        "   - Note any reactions to current results\n\n"
        "   If Democratic candidate is leading:\n"
        "   - Check https://democrats.org/\n"
        "   - Summarize key policy positions and campaign updates\n"
        "   - Note any reactions to current results\n\n"
        "   If results are unclear:\n"
        "   - Check https://www.politico.com/\n"
        "   - Analyze expert commentary and predictions\n"
        "   - Summarize key factors affecting the race\n\n"
        "3. If Republicans have secured victory:\n"
        "   - Request funds from the faucet\n"
        "   - wait for confirmation and check the balances\n"
        "   - Generate, verify the zkTls proof, and mint NFT of success\n"
        "   - Provide transaction details and confirmation\n\n"
        "For each step, provide:\n"
        "- Detailed observations and data\n"
        "- Your reasoning process\n"
        "- Any challenges encountered\n"
        "- Specific actions taken and their outcomes\n"
        "- your response should be in markdown format and include the urls visited\n"
        "- do not show the content of the urls you visited\n"
        "- provide transaction details and confirmation as the last message\n"
        "- do not ask for more instructions"
    )


def process_agent_chunk(chunk: Dict[str, Any]) -> None:
    """Process and print agent response chunks."""
    if "agent" in chunk:
        print(chunk["agent"]["messages"][0].content)
    elif "tools" in chunk:
        print(chunk["tools"]["messages"][0].content)
    print("-------------------")


def run_autonomous_mode(agent_executor, config):
    """Run the agent autonomously."""
    print("Starting autonomous mode...")
    try:
        thought = get_autonomous_instructions()
        for chunk in agent_executor.stream(
            {"messages": [HumanMessage(content=thought)]}, config
        ):
            process_agent_chunk(chunk)
    except KeyboardInterrupt:
        print("Goodbye Agent!")
        sys.exit(0)


def run_chat_mode(agent_executor, config):
    """Run the agent interactively based on user input."""
    print("Starting chat mode... Type 'exit' to end.")
    while True:
        try:
            user_input = input("\nUser: ")
            if user_input.lower() == "exit":
                break

            for chunk in agent_executor.stream(
                {"messages": [HumanMessage(content=user_input)]}, config
            ):
                process_agent_chunk(chunk)

        except KeyboardInterrupt:
            print("Goodbye Agent!")
            sys.exit(0)


def choose_mode() -> str:
    """Choose whether to run in autonomous or chat mode."""
    return "auto"


def main():
    """Start the chatbot agent."""
    agent_executor, config = initialize_agent()
    mode = choose_mode()

    if mode == "chat":
        run_chat_mode(agent_executor=agent_executor, config=config)
    elif mode == "auto":
        run_autonomous_mode(agent_executor=agent_executor, config=config)


if __name__ == "__main__":
    print("Starting Agent...")
    main()
