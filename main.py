#!/usr/bin/env python
# pylint: disable=unused-argument
# written by ccznn

"""
Simple Bot to handle '(my_)chat_member' updates.
Greets new users & keeps track of which chats the bot is in.

Usage:
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
from typing import Optional, Tuple
import os
import requests
from dotenv import load_dotenv

from telegram import Chat, ChatMember, ChatMemberUpdated, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    ChatMemberHandler,
    CommandHandler,
    ContextTypes,
)

load_dotenv()

# Enable logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def extract_status_change(chat_member_update: ChatMemberUpdated) -> Optional[Tuple[bool, bool]]:
    """Takes a ChatMemberUpdated instance and extracts whether the 'old_chat_member' was a member
    of the chat and whether the 'new_chat_member' is a member of the chat. Returns None, if
    the status didn't change.
    """
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get("is_member",
                                                                       (None, None))

    if status_change is None:
        return None

    old_status, new_status = status_change
    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.RESTRICTED and new_is_member is True)

    return was_member, is_member


async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Tracks the chats the bot is in."""
    result = extract_status_change(update.my_chat_member)
    if result is None:
        return
    was_member, is_member = result

    # Let's check who is responsible for the change
    cause_name = update.effective_user.full_name

    # Handle chat types differently:
    chat = update.effective_chat
    if chat.type == Chat.PRIVATE:
        if not was_member and is_member:
            # This may not be really needed in practice because most clients will automatically
            # send a /start command after the user unblocks the bot, and start_private_chat()
            # will add the user to "user_ids".
            # We're including this here for the sake of the example.
            logger.info("%s unblocked the bot", cause_name)
            context.bot_data.setdefault("user_ids", set()).add(chat.id)
        elif was_member and not is_member:
            logger.info("%s blocked the bot", cause_name)
            context.bot_data.setdefault("user_ids", set()).discard(chat.id)
    elif chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
        if not was_member and is_member:
            logger.info("%s added the bot to the group %s",
                        cause_name, chat.title)
            context.bot_data.setdefault("group_ids", set()).add(chat.id)
        elif was_member and not is_member:
            logger.info("%s removed the bot from the group %s",
                        cause_name, chat.title)
            context.bot_data.setdefault("group_ids", set()).discard(chat.id)
    elif not was_member and is_member:
        logger.info("%s added the bot to the channel %s",
                    cause_name, chat.title)
        context.bot_data.setdefault("channel_ids", set()).add(chat.id)
    elif was_member and not is_member:
        logger.info("%s removed the bot from the channel %s",
                    cause_name, chat.title)
        context.bot_data.setdefault("channel_ids", set()).discard(chat.id)


async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Buy $ZNN token"""
    uniswap_znn = "https://app.uniswap.org/#/swap?inputCurrency=ETH&amp;outputCurrency=0xb2e96a63479c2edd2fd62b382c89d5ca79f572d3"
    uniswap_qsr = "https://app.uniswap.org/#/swap?inputCurrency=0x96546AFE4a21515A3a30CD3fd64A70eB478DC174&amp;outputCurrency=0xb2e96a63479c2edd2fd62b382c89d5ca79f572d3"
    text = f"""
---------------------
*Buy $ZNN or $QSR*
---------------------
[ETH <> wZNN on Uniswap]({uniswap_znn})
[wQSR <> wZNN on Uniswap]({uniswap_qsr})
"""
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)


async def websites(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List Project Websites"""
    urls = [
        "https://zenon.network",
        "https://zenon.org",
        "https://zenon.tools",
        "https://zenon.info",
        "https://ask.zenon.wiki",
        "https://my.znn.link/",
        "https://zenonhub.io",
        "https://attribute.zenon.org",
        "https://explorer.zenon.org",
        "https://explorer.zenon.info",
        "https://forum.zenon.org",
        "https://forum.hypercore.one",
    ]
    text = f"""
---------------------
*Project Websites*
---------------------
Websites
[{urls[0]}]({urls[0]})
[{urls[1]}]({urls[1]})
[{urls[2]}]({urls[2]})
[{urls[3]}]({urls[3]})
[{urls[4]}]({urls[4]})
[{urls[5]}]({urls[5]})
[{urls[6]}]({urls[6]})
[{urls[7]}]({urls[7]})

Explorers
[{urls[8]}]({urls[8]})
[{urls[9]}]({urls[9]})

Forums
[{urls[10]}]({urls[10]})
[{urls[11]}]({urls[11]})
"""
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)


async def nodes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List of Public Nodes"""
    urls = [
        "wss://my.hc1node.com:35998",
        "wss://node.zenonhub.io:35998"
    ]
    text = f"""
---------------------
*Public Nodes*
---------------------
[{urls[0]}]({urls[0]})
[{urls[1]}]({urls[1]})
"""
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)


async def wallets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Download s y r i u s wallet"""
    url = "https://github.com/zenon-network/syrius/releases/tag/v0.1.0-alphanet"
    text = f"""
---------------------
*Link to Wallet*
---------------------
[Download s y r i u s]({url})
"""
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)


async def p2p(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """How to p2p swap in syrius"""
    url = "https://www.youtube.com/watch?v=L2UCjT9X8TI"
    text = f"""
---------------------
*P2P Swaps in s y r i u s*
---------------------
[How to P2P Swap in s y r i u s]({url})
"""
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)


async def decks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Investor Decks"""
    urls = [
        "https://d1fdloi71mui9q.cloudfront.net/hBEx1tHQxeFlmlQpZCIK_Zenon%20VC%20Deck.pdf",
        "https://d1fdloi71mui9q.cloudfront.net/H8euegDSThSnnlx4tNhu_The%20Zenon%20Deck.pdf"
    ]
    text = f"""
---------------------
*Zenon Network Decks*
---------------------
[VC Deck Book (short)]({urls[0]})
[Full Deck Book (long)]({urls[1]})
"""
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)


async def trackers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Telegram Trackers"""
    urls = [
        "https://t.me/pillar_tracker",
        "https://t.me/az_tracker",
        "https://t.me/znnhub",
        "https://t.me/zenonwhalealerts",
        "https://t.me/wZNN_wQSR",
        "https://t.me/zenon_bridge_alerts"
    ]
    text = f"""
---------------------
*Telegram Trackers*
---------------------
[{urls[0]}]({urls[0]})
[{urls[1]}]({urls[1]})
[{urls[2]}]({urls[2]})
[{urls[3]}]({urls[3]})
[{urls[4]}]({urls[4]})
[{urls[5]}]({urls[5]})
"""
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)


async def explorers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Blockchain Explorer"""
    urls = [
        "https://zenonhub.io/explorer",
        "https://explorer.zenon.org/",
        "https://explorer.zenon.info/",
        "https://explorer.zenon.network/",
    ]
    text = f"""
---------------------
*Explorers*
---------------------
[{urls[0]}]({urls[0]})
[{urls[1]}]({urls[1]})
[{urls[2]}]({urls[2]})
[{urls[3]}]({urls[3]})
"""
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)


async def chart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Price Chart"""
    url = "https://www.dextools.io/app/en/ether/pair-explorer/0xdac866a3796f85cb84a914d98faec052e3b5596d"
    text = f"""
---------------------
*Price Chart*
---------------------
[Dextools Price Chart - $wZNN]({url})
"""
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)


async def whitepaper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Download Whitepaper"""
    url = "https://znn.link/whitepaper"
    text = f"""
---------------------
*Whitepaper*
---------------------
[Download Whitepaper]({url})
"""
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)


async def marketing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Performance Marketing Links"""
    urls = [
        "https://attribute.zenon.org",
        "https://attribute.zenon.org/link-builder",
        "https://support.zenon.org/en/collections/5920226-marketing"
    ]
    text = f"""
---------------------
*Performance Marketing*
---------------------
[{urls[0]}]({urls[0]})
[{urls[1]}]({urls[1]})
[{urls[2]}]({urls[2]})
"""
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)


async def links(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Important Links"""
    urls = [
        "https://zenon.network/",
        "https://zenon.org/",
        "https://zenon.tools/",
        "https://zenonhub.io/",
        "https://zenon.info/",
        "https://bridge.mainnet.zenon.community/",
        "https://status.bridge.zenon.community/",
        "https://app.uniswap.org/#/swap?inputCurrency=ETH&amp;outputCurrency=0xb2e96a63479c2edd2fd62b382c89d5ca79f572d3",
        "https://forum.zenon.org",
        "https://forum.hypercore.one",
        "https://github.com/zenon-network/syrius/releases/tag/v0.1.0-alphanet",
        "https://www.dextools.io/app/en/ether/pair-explorer/0xdac866a3796f85cb84a914d98faec052e3b5596d"
    ]
    text = f"""
---------------------
*Important Links*
---------------------
[zenon.network]({urls[0]})
[zenon.org]({urls[1]})
[zenon.tools]({urls[2]})
[zenonhub.io]({urls[3]})
[zenon.info]({urls[4]})
[Bridge (ZNN <-> wZNN)]({urls[5]})
[Bridge Status]({urls[6]})
[Buy $ZNN]({urls[7]})
[Marketing Forum]({urls[8]})
[Developers Forum]({urls[9]})
[Wallet]({urls[10]})
[Chart]({urls[11]})
"""
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)


async def bridge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Bridge Command"""
    urls = [
        "https://bridge.mainnet.zenon.community/?referral=2f5b37014d6f3e26323c33670233014a6f2777263876255223040a3b3e76633b753b19281b123c36",
        "https://status.bridge.zenon.community/",
        "https://affiliate.zenon.community/",
        "https://youtu.be/Ui2x1IECwys",
        "https://forum.hypercore.one/t/steps-to-troubleshoot-the-wznn-znn-bridge/237",
        "https://zenonhub.io/tools/api-playground?request=Bridge.getAllWrapTokenRequestsByToAddress",
        "https://zenonhub.io/tools/api-playground?request=Bridge.getAllUnwrapTokenRequestsByToAddress",
        "https://t.me/nom_mt"
    ]
    text = f"""
---------------------
*Zenon Network Bridge*
---------------------
*Website*
[https://bridge.mainnet.zenon.community/]({urls[0]})

*Status*
[{urls[1]}]({urls[1]})

*Generate Affiliate Link*
[{urls[2]}]({urls[2]})

*How to Bridge wZNN to ZNN*
[Youtube Video]({urls[3]})

*Troubleshooting*
[Steps to Troubleshoot]({urls[4]})
[Check Wrap Status (ZNN > wZNN)]({urls[5]})
[Check Unwrap Status (wZNN > ZNN)]({urls[6]})

*Support Channel*
[NoM Multichain Technology Feedback]({urls[6]})
"""
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)


async def github(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Github Repositories"""
    urls = [
        "https://github.com/zenon-network",
        "https://github.com/hypercore-team",
        "https://github.com/hypercore-one"
    ]
    text = f"""
---------------------
*Github Repositories*
---------------------
[{urls[0]}]({urls[0]})
[{urls[1]}]({urls[1]})
[{urls[2]}]({urls[2]})
"""
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)


async def ca(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ethereum Contract Address"""
    urls = [
        "https://etherscan.io/address/0xb2e96a63479c2edd2fd62b382c89d5ca79f572d3",
        "https://app.uniswap.org/swap?inputCurrency=0xb2e96a63479c2edd2fd62b382c89d5ca79f572d3&amp;outputCurrency=ETH",
        "https://etherscan.io/address/0x96546AFE4a21515A3a30CD3fd64A70eB478DC174",
        "https://app.uniswap.org/swap?inputCurrency=0x96546AFE4a21515A3a30CD3fd64A70eB478DC174&amp;outputCurrency=0xb2e96a63479c2edd2fd62b382c89d5ca79f572d3",
        "https://www.zenon.org/en/phases/1/tokens/znn",
        "https://www.zenon.org/en/phases/1/tokens/qsr",
    ]
    text = f"""
---------------------
*Contract Addresses*
---------------------
*$wZNN - Ethereum Contract Addresses*
[wZNN Token | 0xb2e96a63479C2Edd2FD62b382c89D5CA79f572d3]({urls[0]})
[Buy wZNN on Uniswap]({urls[1]})
[wQSR Token | 0x96546AFE4a21515A3a30CD3fd64A70eB478DC174]({urls[2]})
[Buy wQSR on Uniswap]({urls[3]})

*Learn More*
[Learn About $ZNN]({urls[4]})
[Learn About $QSR]({urls[5]})

"""
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)


async def forums(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List of Forums"""
    urls = [
        "https://forum.zenon.org",
        "https://forum.hypercore.one",
    ]
    text = f"""
---------------------
*Community Forums*
---------------------
[Marketing - {urls[0]}]({urls[0]})
[Development - {urls[1]}]({urls[1]})
"""
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)


async def pricechat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Price Chat"""
    url = "https://t.me/NoM_Community"
    text = f"""
---------------------
*Degen Price Chat*
---------------------
[NoM Community Group]({url})
"""
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fetch and display the price of znn, qsr, btc, and eth."""
    url = "https://api.hc1.tools/price"
    response = requests.get(url)
    data = response.json()["data"]

    text = f"""
    ------------------
    *ZNN & QSR Price*
    ------------------
    ZNN: ${data["znn"]["usd"]}
    QSR: ${data["qsr"]["usd"]}
    BTC: ${data["btc"]["usd"]}
    ETH: ${data["eth"]["usd"]}
    """


async def supply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fetch and display the supply of znn & qsr"""
    url = "https://zenonhub.io/api/nom/token/get-by-owner?address=z1qxemdeddedxt0kenxxxxxxxxxxxxxxxxh9amk0"
    response = requests.get(url)
    data = response.json()["data"]

    znn_total_supply = data["list"][1]["totalSupply"][:-8]
    znn_max_supply = data["list"][1]["maxSupply"][:-8]
    qsr_total_supply = data["list"][0]["totalSupply"][:-8]
    qsr_max_supply = data["list"][0]["maxSupply"][:-8]

    text = f"""
    -----------------------
    *ZNN & QSR Supply*
    -----------------------
    ZNN Current Supply: {format(znn_total_supply, ',')}
    ZNN Max Supply: {format(znn_max_supply, ',')}
    QSR Current Supply: {format(qsr_total_supply, ',')}
    QSR Max Supply: {format(qsr_max_supply, ',')}
    """


async def mc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fetch and display the market cap of znn and qsr."""
    url = "https://api.hc1.tools/price"
    response = requests.get(url)
    price_data = response.json()["data"]

    supply_url = "https://zenonhub.io/api/nom/token/get-by-owner?address=z1qxemdeddedxt0kenxxxxxxxxxxxxxxxxh9amk0"
    supply_response = requests.get(supply_url)
    supply_data = supply_response.json()["data"]

    znn_price = float(price_data["znn"]["usd"])
    qsr_price = float(price_data["qsr"]["usd"])

    znn_total_supply = int(supply_data["list"][1]["totalSupply"]) // 10**8
    qsr_total_supply = int(supply_data["list"][0]["totalSupply"]) // 10**8

    znn_market_cap = znn_price * znn_total_supply
    qsr_market_cap = qsr_price * qsr_total_supply

    text = f"""
    ----------------------
    *ZNN & QSR Market Cap*
    ----------------------
    ZNN: ${format(znn_market_cap, ',.2f')}
    QSR: ${format(qsr_market_cap, ',.2f')}
    """


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.getenv('TOKEN')).build()

    # Keep track of which chats the bot is in
    application.add_handler(ChatMemberHandler(
        track_chats, ChatMemberHandler.MY_CHAT_MEMBER))
    application.add_handler(CommandHandler("buy", buy))
    application.add_handler(CommandHandler("websites", websites))
    application.add_handler(CommandHandler("nodes", nodes))
    application.add_handler(CommandHandler("wallets", wallets))
    application.add_handler(CommandHandler("p2p", p2p))
    application.add_handler(CommandHandler("decks", decks))
    application.add_handler(CommandHandler("trackers", trackers))
    application.add_handler(CommandHandler("explorers", explorers))
    application.add_handler(CommandHandler("chart", chart))
    application.add_handler(CommandHandler("whitepaper", whitepaper))
    application.add_handler(CommandHandler("marketing", marketing))
    application.add_handler(CommandHandler("links", links))
    application.add_handler(CommandHandler("bridge", bridge))
    application.add_handler(CommandHandler("github", github))
    application.add_handler(CommandHandler("ca", ca))
    application.add_handler(CommandHandler("forums", forums))
    application.add_handler(CommandHandler("pricechat", pricechat))
    application.add_handler(CommandHandler("price", price))
    application.add_handler(CommandHandler("supply", supply))
    application.add_handler(CommandHandler("mc", mc))

    # Handle members joining/leaving chats.
    # application.add_handler(ChatMemberHandler(
    #    greet_chat_members, ChatMemberHandler.CHAT_MEMBER))

    # Run the bot until the user presses Ctrl-C
    # We pass 'allowed_updates' handle *all* updates including `chat_member` updates
    # To reset this, simply pass `allowed_updates=[]`
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
