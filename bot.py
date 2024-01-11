from typing import Optional, Literal
import google.generativeai as genai
from discord import app_commands
import discord
import os
from dotenv import load_dotenv

load_dotenv()

GENAI_API_KEY = os.getenv('GENAI_API_KEY')
TOKEN = os.getenv('BOT_TOKEN')

MY_GUILD = discord.Object(id=1016759347583393882)

genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

intents = discord.Intents.all()
client = MyClient(intents=intents)

async def summarize_messages (chat, variation=None) :

    variations = {
        'normal': "normally as text: ",
        'pirate': "in the tone of a stereotypical pirate: ",
        'list': "as a bullet list of topics: ",
        'dramatised': "but exagerrated and dramatised: "
    }
    
    response = model.generate_content("The following is chat from a discord server. Summarize the given text " + variations[variation] + chat)
    try:
        return response.text
    except:
        return response.prompt_feedback

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

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('---------------')

# TODO - Remove Appa from conversations - Dad Bot#2189
# TODO - Use tokenizer to break messages into chunks.

@client.tree.command()
@app_commands.describe(num_messages='Number of messages to summarize!')
@app_commands.rename(num_messages='number')
@app_commands.describe(variation='Spice up the summary!')
async def summarize(interaction: discord.Interaction, num_messages: int, variation: Literal['normal', 'pirate', 'list', 'dramatised']):
    """Summarizes messages!"""
    await interaction.response.send_message(f'Summarizing messages...', ephemeral=False)
    response = await send_summary(num_messages, interaction.channel, variation)
    await interaction.edit_original_response(content=response)

@client.tree.command()
@app_commands.describe(prompt='Enter prompt...')
async def prompt(interaction: discord.Interaction, prompt: str):
    """Unleash the power of LLMs in your messages!"""
    await interaction.response.send_message(f'Generating...', ephemeral=False)
    response = model.generate_content(prompt)
    await interaction.edit_original_response(content=response.text)

client.run(TOKEN)