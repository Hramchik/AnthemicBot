import disnake
import configparser

from disnake.ext import commands

from functions.func import requestCallback
from modules.supports import SupportModal
from modules.request import RequestForm

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

bot = commands.InteractionBot(test_guilds=[int(config["Auth"]["guild_id"])])

bot.load_extensions("modules")

@bot.event
async def on_ready():
     await bot.change_presence(activity=disnake.Activity(
         type=disnake.ActivityType.streaming,
         name=config["Auth"]["activity"],
         url="https://www.youtube.com/watch?v=j-iheFkstFQ"
        )
     )
     print(f"Bot is ready! Logged in as {bot.user}")

@bot.listen("on_button_click")
async def support_listener(inter: disnake.MessageInteraction):
    if inter.component.custom_id not in ["+", "-"]:
        return
    if inter.component.custom_id == "+":
        await inter.response.send_modal(modal=SupportModal(bot=bot))
    elif inter.component.custom_id == "-":
        await inter.channel.delete()

@bot.listen("on_button_click")
async def request_listener(inter: disnake.MessageInteraction):
    if inter.component.custom_id not in ["request", "accept", "reject"]:
        return
    if inter.component.custom_id == "request":
        await inter.response.send_modal(modal=RequestForm(bot=bot))
    elif inter.component.custom_id == "accept":
       await requestCallback.accept(inter)
    elif inter.component.custom_id == "reject":
        await requestCallback.reject(inter)

bot.run(config["Auth"]["token"])
