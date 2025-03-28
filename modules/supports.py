import disnake
import configparser

from disnake.ext import commands
from disnake import TextInputStyle

config = configparser.ConfigParser()
config.read('./config.ini', encoding='utf-8')

class SupportModal(disnake.ui.Modal, commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        components = [
            disnake.ui.TextInput(
                label="Проблема",
                placeholder="Какова ваша проблема?",
                custom_id="theme",
                style=TextInputStyle.short,
            ),
            disnake.ui.TextInput(
                label="Описание проблемы",
                placeholder="Подробно опишите вашу проблему.",
                custom_id="description",
                style=TextInputStyle.paragraph,
            )
        ]
        super().__init__(title="Поддержка", components=components)

    @commands.slash_command(
        name="support-create",
        description="Создать кнопку поддержки"
    )
    @commands.has_guild_permissions(administrator=True)
    async def buttons(self, inter: disnake.ApplicationCommandInteraction):
        embed = disnake.Embed(
            title="Создать тикет.",
            description="Если у вас возникла проблема или вам нужна помощь. Вы можете создать тикет, для этого нажмите на кнопку ниже. Команда поддержки свяжется с вами и постарается Вам помочь.",
            color=0xADFF2F,
        )
        await inter.channel.send(
            components=[
                disnake.ui.Button(label="Открыть тикет", style=disnake.ButtonStyle.success, custom_id='+',
                                  emoji="🔓")],
            embed=embed,
        )
        await inter.send("Кнопка тикет системы создана", ephemeral=True)

    async def callback(self, inter: disnake.ModalInteraction):
        guild22 = inter.guild
        await inter.response.send_message("Ваш тикет создан.", ephemeral=True)
        techSupport = guild22.get_role(int(config["Roles"]["support"]))
        preTechSupport = guild22.get_role(int(config["Roles"]["sub_support"]))
        overwrites = {
            guild22.default_role: disnake.PermissionOverwrite(view_channel=False),
            inter.author: disnake.PermissionOverwrite(view_channel=True),
            techSupport: disnake.PermissionOverwrite(view_channel=True),
            preTechSupport: disnake.PermissionOverwrite(view_channel=True)
        }
        channel = await inter.channel.category.create_text_channel(name= f"ticket-{inter.author}", overwrites=overwrites)
        embed = disnake.Embed(
            title="Ваш тикет",
            color=disnake.Colour.green(),
        )
        for key, value in inter.text_values.items():
            embed.add_field(
                name=replaceName(key),
                value=value[:1024],
                inline=False,
            )
        await channel.send(embed = embed, components=[
            disnake.ui.Button(label="Закрыть тикет", style=disnake.ButtonStyle.danger, custom_id="-", emoji="🔒"),
        ])

def replaceName(arg: str):
    if arg == "theme":
        return "Тема"
    else:
        return "Описание"

def setup(bot: commands.Bot):
    bot.add_cog(SupportModal(bot))