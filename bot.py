from typing import Optional, Literal
import google.generativeai as genai
from discord import app_commands
import discord
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
GENAI_API_KEY = os.getenv('GENAI_API_KEY')
MY_GUILD = discord.Object(id=os.getenv('GUILD_ID'))

exclude_list = []

genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

class Bot(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        '''Used to instantly sync commands to given guild, remove function in prod'''

        # # Clear commands from guild
        # self.tree.clear_commands(guild=None)
        # await self.tree.sync()

        # sync commands to guild
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

intents = discord.Intents.all()
client = Bot(intents=intents)

async def summarize_messages (chat, variation=None) :

    variations = {
        'normal': "normally as a block of text: ",
        'pirate': "in the tone of a stereotypical pirate: ",
        'list': "as a bullet list of topics: ",
        'dramatised': "but exagerrated and dramatised: ",
        'cowboy': "as a wild west Texan cowboy: "
    }
    
    response = model.generate_content("The following is chat from a discord server. Summarize the given text " + variations[variation] + chat)
    try:
        return response.text
    except:
        return response.prompt_feedback

async def send_summary(num_mesgs, channel, variation=None) :
    history = ""
    async for msg in channel.history(limit = num_mesgs):
        if msg.author.id not in exclude_list:
            history = f"{msg.author.display_name}: {msg.content} \n{history} "

    try:
        response = await summarize_messages(history, variation)
    except Exception as e :
        print(e)
        response = "Error, kindly try later!"

    return response

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('---------------')

@client.tree.command()
@app_commands.describe(num_messages='Number of messages to summarize!')
@app_commands.rename(num_messages='number')
@app_commands.describe(variation='Spice up the summary!')
async def tldr(interaction: discord.Interaction, num_messages: int, variation: Literal['normal', 'pirate', 'list', 'dramatised', 'cowboy']):
    """Summarizes messages!"""
    await interaction.response.send_message(f'Summarizing messages...', ephemeral=True)
    response = await send_summary(num_messages + 1, interaction.channel, variation)
    await interaction.followup.send(response)

client.run(TOKEN)