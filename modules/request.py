import disnake
import configparser
import sqlite3

from disnake.ext import commands
from disnake import TextInputStyle

config = configparser.ConfigParser()
config.read('./config.ini', encoding='utf-8')

class RequestForm(disnake.ui.Modal, commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        components = [
            disnake.ui.TextInput(
                label="Никнейм",
                placeholder="Dream_Craft2013",
                custom_id="Nickname",
                style=TextInputStyle.short,
            ),
            disnake.ui.TextInput(
                label="Возраст",
                custom_id="age",
                style=TextInputStyle.short,
            ),
            disnake.ui.TextInput(
                label="Чем планируете заниматься на сервере?",
                placeholder="Краткое описание того, чем вы планируете заниматься",
                custom_id="plans",
                style=TextInputStyle.paragraph,
            ),
            disnake.ui.TextInput(
                label="Откуда узнали о проекте?",
                custom_id="inviter",
                style=TextInputStyle.short,
            ),
        ]
        super().__init__(title="Заявка", components=components)

    @commands.slash_command(
        name='form-create',
        description='Создание кнопки для подачи заявки',
    )
    @commands.has_permissions(administrator=True)
    async def buttonsForm(self, inter: disnake.ApplicationCommandInteraction):
        embed = disnake.Embed(
            title="Подать заявку.",
            description="Заполните форму, чтобы начать играть на нашем замечательном сервере!",
            colour=0xADFF2F,
        )
        await inter.channel.send(
            components=[
                disnake.ui.Button(label="Подать заявку", style=disnake.ButtonStyle.green, custom_id="request",
                            emoji="🪪"),
            ],
            embed=embed
        )
        await inter.send("Кнопка подачи заявки создана", ephemeral=True)

    async def callback(self, inter):
        conn = sqlite3.connect('./database/request.db')
        c = conn.cursor()
        c.execute('SELECT * FROM requests WHERE user_id = ?', (inter.user.id,))
        ids = c.fetchall()
        if not ids:
            channel = self.bot.get_channel(int(config["Auth"]["channel_id"]))
            await inter.response.send_message(content="Вы успешно заполнили анкету!", ephemeral=True)
            requestEmbed = disnake.Embed(
                title="Новая заявка!",
                description=f"**Отправитель: {inter.user.global_name}**",
                color=disnake.Colour.red(),
            )
            requestEmbed.set_thumbnail(url=inter.user.display_avatar.url)
            for key, value in inter.text_values.items():
                requestEmbed.add_field(
                    name=replaceName(key),
                    value=value[:1024],
                    inline=False,
                )
            buff = await channel.send(embed=requestEmbed, components=[
                disnake.ui.Button(label="Принять", style=disnake.ButtonStyle.green, custom_id="accept"),
                disnake.ui.Button(label="Отклонить", style=disnake.ButtonStyle.danger, custom_id="reject"),
            ])
            requestEmbed_id = buff.id
            requestCallBackEmbed = disnake.Embed(
                title="Ваша заявка отправлена на рассмотрение!",
                description="**На рассмотрение заявок уходит до 24-х часов**",
                color=disnake.Colour.purple(),
            )
            requestCallBackEmbed.set_image(file=disnake.File(str(config["Pictures"]["msg_picture"])))
            await inter.user.send(embed=requestCallBackEmbed)
            await reg(inter, requestEmbed_id)
        elif ids:
            await reg(inter, None)

def replaceName(arg: str):
    if arg == "Nickname":
        return "Ник"
    elif arg == "age":
        return "Возраст"
    elif arg == "plans":
        return "Планы"
    elif arg == "inviter":
        return "Откуда узнали о проекте?"

async def reg(inter: disnake.ModalInteraction, requestEmbed_id):
    conn = sqlite3.connect('./database/request.db')
    c = conn.cursor()
    c.execute('SELECT * FROM requests WHERE user_id = ?', (inter.user.id,))
    ids = c.fetchall()
    if ids:
        await inter.response.send_message("Вы уже подали заявку!", ephemeral=True)
    elif not ids:
        connect = sqlite3.connect('./database/request.db')
        c = connect.cursor()
        c.execute("INSERT INTO requests (user_id, message_id, nickname, status) VALUES (?, ?, ?, ?)",
                      (inter.author.id, requestEmbed_id, inter.text_values['Nickname'], 'pending'))
        connect.commit()
        connect.close()

def setup(bot: commands.Bot):
    bot.add_cog(RequestForm(bot))
