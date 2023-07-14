import discord
import responses
from discord.ext import commands

async def send_message (message, history, is_private) :

    try :
        response = await responses.handle_responses(history)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e :
        print(e)

def run_bot () :

    token = "YOUR_BOT_TOKEN"

    intent = discord.Intents.default()
    intent.message_content = True
    
    bot = commands.Bot(command_prefix = "!", intents = discord.Intents.all())

    @bot.event
    async def on_ready () :
        print(f"Bot is now running!")
        try :
            synced = await bot.tree.sync()
        except Exception as e:
            print(e)

    @bot.event
    async def on_message(message):

        history = []
        if message.author == bot.user:
            return
        user_message = str(message.content)

        if ("!tldr" in user_message.lower()) :
            num = int(user_message.split("!tldr")[1].split(" ")[1])
            if (num <= 100) :
                channel = message.channel

                async for msg in channel.history(limit = num + 1):
                    history.append(f"{msg.author}: {msg.content}")
    
                if (user_message[0] == "?") :
                    user_message = user_message[1:]
                    await send_message(message, history, is_private = True)
                else :
                    await send_message(message, history, is_private = False)

    bot.run(token)