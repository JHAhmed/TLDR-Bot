
import discord
from openai import OpenAI
from discord import app_commands

import os
from enum import Enum
from dotenv import load_dotenv
from typing import Optional, Literal

load_dotenv()

class Provider(Enum): # Not being used currently
    OPENAI = 'openai'
    GOOGLE = 'google'

TOKEN = os.getenv('BOT_TOKEN')
MY_GUILD = discord.Object(id=os.getenv('GUILD_ID'))

BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai/"
# MODEL = "gemini-2.5-flash"
# PROVIDER = "Google"
MODEL = "gpt-5-nano"
PROVIDER = "OpenAI"

with open('exclude_list.txt', 'r') as f:
    exclude_list = [int(line.strip()) for line in f.readlines()]

client = OpenAI(
    # api_key=os.getenv('GEMINI_API_KEY'),
    # base_url=BASE_URL
)

class Bot(discord.Client):
    def __init__(self, *, intents: discord.Intents, activity: discord.Activity):
        super().__init__(intents=intents, activity=activity)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        '''Used to instantly sync commands to given guild, remove function in prod'''

        # # Clear commands from guild
        # self.tree.clear_commands(guild=None)
        # await self.tree.sync()

        # sync commands to guild
        if (MY_GUILD):
            self.tree.copy_global_to(guild=MY_GUILD)
            await self.tree.sync(guild=MY_GUILD)

intents = discord.Intents.all()
bot = Bot(intents = intents, activity = discord.Game(name="/tldr {number} {style}"))

async def chunk_string(input_string, max_length=2048):
    if len(input_string) <= max_length:
        return [input_string]

    chunks = []
    current_chunk = ''

    for char in input_string:
        current_chunk += char

        # Break the chunk if it exceeds the maximum length and ends with a period or a newline
        if len(current_chunk) >= max_length and (char == '.' or char == '\n'):
            chunks.append(current_chunk.strip())
            current_chunk = ''

    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


async def summarize_messages (chat, variation=None) :

    variations = {
        'normal': "normally as a block of text: ",
        'pirate': "in the tone of a stereotypical pirate: ",
        'list': "as a bullet list of points discussed: ",
        'dramatised': "but exagerrated and dramatised: ",
        'cowboy': "as a wild west Texan cowboy: "
    }
    
    prompt = f'''
        The following is chat from a discord server. Summarize (or TL;DR) the given text {variations[variation]}\n {chat}
        \n
        The TL;DR must contain all imporant bits of information, 
        you can ignore (or give less preference to) any messages that are not useful or constructive.

        The messages might be in English or in transliterated Tamil (using English letters). You must be able to understand both languages and summarize accordingly.
        You don't need to include point out when you're summarizing Tamil messages, just include them as normal.
    '''

    response = client.responses.create(
        model=MODEL,
        input=prompt
    )

    # response = client.chat.completions.create(
    #     model=MODEL,
    #     messages=[
    #         {"role": "user", "content": prompt}
    #     ]
    # )

    return response.output_text, response.usage.total_tokens
    # return response.choices[0].message.content, response.usage.total_tokens

async def send_summary(num_mesgs, channel, variation=None) :
    history = ""
    async for msg in channel.history(limit = num_mesgs):
        if msg.author.id not in exclude_list:
            history = f"{msg.author.display_name}: {msg.content} \n{history} "

    response = "Error, kindly try later!"
    total_tokens = 0

    try:
        response, total_tokens = await summarize_messages(history, variation)
    except Exception as e :
        print("Summary error:", e)
        # response already set to friendly error; total_tokens stays 0

    return response, total_tokens



async def send_summary_test(num_mesgs, channel, variation=None):
    async def summarize_chunk(start, end):
        response = ""
        history = []

        async for msg in channel.history(limit=end-start, after=channel.last_message_id):
            if msg.author.id not in exclude_list:
                history.append({
                    'author': msg.author.display_name,
                    'content': msg.content
                })

        try:
            response += await summarize_messages(history, variation)
        except Exception as e:
            print(f"Error summarizing messages {start} to {end}: {e}")
            return None

        return response

    chunk_size = 100
    summaries = ""

    for i in range(0, num_mesgs, chunk_size):
        chunk_start = i
        chunk_end = min(i + chunk_size, num_mesgs)
        
        chunk_summary = await summarize_chunk(chunk_start, chunk_end)
        if chunk_summary is None:
            return "Error, kindly try later!"
        summaries += chunk_summary

    # If we have multiple summaries, we need to summarize them again
    # if len(summaries) > 1:
    #     try:
    #         final_summary = await summarize_messages(summaries, variation)
    #         return final_summary
    #     except Exception as e:
    #         print(f"Error in final summarization: {e}")
    #         return "Error, kindly try later!"
    
    return summaries if summaries else "Error!"


async def get_messages_up_to(channel_id, up_to_message_id):
    """
    Fetches all messages in a channel up to a specific message ID.

    Parameters:
    - channel_id: The ID of the channel from which to fetch messages.
    - up_to_message_id: The ID of the message up to (and including) which messages should be fetched.

    Returns:
    A list of discord.Message objects.
    """
    channel = bot.get_channel(channel_id)
    if channel is None:
        print("Channel not found.")
        return []

    messages = []
    async for message in channel.history(limit=None):
        messages.append(message)
        if message.id == up_to_message_id:
            break

    return messages


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('---------------')

@bot.tree.command()
@app_commands.describe(num_messages='Number of messages to summarize!')
@app_commands.rename(num_messages='number')
@app_commands.describe(variation='Spice up the summary!')
async def tldr(interaction: discord.Interaction, num_messages: int, variation: Literal['normal', 'pirate', 'list', 'dramatised', 'cowboy']):
    """Summarizes messages!"""
    await interaction.response.send_message(f'Summarizing messages...', ephemeral=False)

    if (num_messages < 5 or num_messages > 200):
        await interaction.followup.send("Please provide a number between 5 and 200.")
        return

    response, response_total_tokens = await send_summary(num_messages, interaction.channel, variation)
    response = str(response)
    
    cost_per_token = (0.25 * 85) / 1000000 # ((Input + Output) / 2) * USD to INR / million tokens
    # cost_per_token = (1 * 85) / 1000000 # ((Input + Output) / 2) * USD to INR / million tokens

    cost = response_total_tokens * cost_per_token if response_total_tokens else 0.0


    print(f"Total tokens used: {response_total_tokens}, Estimated cost: ₹{round(cost, 1)}")

    # last_msg = None
    # async for chunk in await chunk_string(response):
    #     # ensure a message object is returned
    #     last_msg = await interaction.followup.send(chunk, wait=True)

    beep = f"-# ~~          ~~\n-# Beep boop, this summary was generated by {PROVIDER}'s `{MODEL}` and cost roughly ₹{round(cost, 2)}."

    # if last_msg:
    #     await last_msg.edit(content=last_msg.content + "\n" + beep)
    # else:
    #     await interaction.followup.send(beep)



    for chunk in await chunk_string(response):
        await interaction.followup.send(chunk + "\n" + beep)


@bot.tree.command()
async def hi(interaction: discord.Interaction):
    """Sends a greeting!"""
    await interaction.response.send_message(f'Sending reply...', ephemeral=True)

    response = "Hello! I am TLDR Bot, here to help you summarize your Discord conversations. Use the /tldr command followed by the number of messages you want to summarize and the style of summary you prefer. For example, /tldr 50 pirate will give you a pirate-themed summary of the last 50 messages. Let's make your chats concise and fun!"
    await interaction.followup.send(response)        


# @bot.tree.command()
# @app_commands.describe(num_messages='Number of messages to summarize!')
# @app_commands.rename(num_messages='number')
# @app_commands.describe(variation='Spice up the summary!')
# async def user_tldr(interaction: discord.Interaction, num_messages: int, user: discord.Member, variation: Literal['normal', 'pirate', 'list', 'dramatised', 'cowboy']):
#     """Summarizes messages from a given user!"""
#     await interaction.response.send_message(f'Summarizing messages...', ephemeral=True)
#     response = await send_summary(num_messages + 1, interaction.channel, variation)
#     await interaction.followup.send(response)

bot.run(TOKEN)