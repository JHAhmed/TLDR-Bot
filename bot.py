from typing import Optional, Literal
from discord import app_commands
from dotenv import load_dotenv
from openai import OpenAI
from enum import Enum
import discord
import os

load_dotenv()

class Provider(Enum):
    OPENAI = 'openai'
    GOOGLE = 'google'

TOKEN = os.getenv('BOT_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
MY_GUILD = discord.Object(id=os.getenv('GUILD_ID'))

class Bot(discord.Client):
    def __init__(self, *, intents: discord.Intents, activity: discord.Activity):
        super().__init__(intents=intents, activity=activity)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        '''Used to instantly sync commands to given guild, for dev testing.'''

        if not MY_GUILD:
            print("Guild ID not set in environment variables.")
            return
        
        # # Clear commands from guild
        # self.tree.clear_commands(guild=None)
        # await self.tree.sync()

        # sync commands to guild
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

intents = discord.Intents.all()
bot = Bot(intents = intents, activity = discord.Game(name="/tldr {number} {style}"))

async def chunk_string(input_string, max_length=1950):
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

async def summarize_messages (chat, variation=None, provider=Provider.GOOGLE):

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
    '''

    llm_client = OpenAI(
        api_key=GEMINI_API_KEY if provider == Provider.GOOGLE else OPENAI_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/" if provider == Provider.GOOGLE else "https://api.openai.com/v1",
    )


    response = llm_client.chat.completions.create(
        model="gemini-2.0-flash" if provider == Provider.GOOGLE else "gpt-4.1-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

async def send_summary(num_mesgs, channel, variation=None) :
    history = ""
    async for msg in channel.history(limit = num_mesgs):
        history = f"{msg.author.display_name}: {msg.content} \n{history} "

    try:
        response = await summarize_messages(history, variation)
    except Exception as e :
        print(e)
        response = "Error, kindly try later!"

    return response


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
    await interaction.response.send_message(f'Summarizing messages...', ephemeral=True)
    response = await send_summary(num_messages, interaction.channel, variation)
    response = str(response)

    print(f"\nReponse: {len(response)}")

    for chunk in await chunk_string(response):
        await interaction.followup.send(chunk)

bot.run(TOKEN)
