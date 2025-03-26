import disnake
import sqlite3
import configparser

from mcrcon import MCRcon

from database import dbCreate
from disnake.ext import commands

config = configparser.ConfigParser()
config.read('./config.ini', encoding='utf-8')

connect = sqlite3.connect('./database/request.db')
cursor = connect.cursor()

cursor.execute('SELECT user_id, message_id FROM requests')
ids = cursor.fetchall()

class requestCallback(commands.Cog):
    async def accept(inter: [disnake.MessageInteraction, disnake.ApplicationCommandInteraction]):
        connection = sqlite3.connect('./database/request.db')
        cursord = connection.cursor()
        cursord.execute('SELECT user_id, nickname FROM requests WHERE message_id = ?', (inter.message.id,))
        result = cursord.fetchone()
        user_id = result[0]
        nickname = result[1]
        if result:
            user = await inter.bot.fetch_user(int(user_id))
            embed = disnake.Embed(
                title='Заявка одобрена!',
                description='**Желаем приятной игры на нашем сервере!**',
                color=disnake.Colour.green()
            )
            embed.set_image(file=disnake.File(str(config["Pictures"]["msg_picture_accept"])))
            await user.send(embed=embed)

            guild = inter.guild
            member = await guild.fetch_member(user_id)
            role_id = int(config["Roles"]["role_id"])
            role = guild.get_role(role_id)
            await member.add_roles(role)

            rcon_host = config["RCON"]["host"]
            rcon_port = int(config["RCON"]["port"])
            rcon_password = config["RCON"]["password"]

            with MCRcon(rcon_host, rcon_password, port=rcon_port) as mcr:
                mcr.command(f'whitelist add ' + str(nickname))
                print(f'successfully added in whitelist ' + str(nickname))

            connection.commit()
            connection.close()

        cursor.execute('UPDATE requests SET status = ? WHERE message_id = ?', ('accepted', inter.message.id,))
        connect.commit()

        await inter.response.edit_message(f'Принял {inter.user.mention}', view=None)
    async def reject(inter: disnake.MessageInteraction):
        connection = sqlite3.connect('./database/request.db')
        cursord = connection.cursor()
        cursord.execute('SELECT user_id FROM requests WHERE message_id = ?', (inter.message.id,))
        result = cursord.fetchone()
        if result:
            user_id = result[0]
            user = await inter.bot.fetch_user(user_id)
            embed = disnake.Embed(
                title='Заявка отклонена!',
                description='**Заявка была отклонена, скорее всего это связано с тем что какой-то из пунктов не правильно оформлен**',
                color=disnake.Colour.green()
            )
            embed.set_image(file=disnake.File(str(config["Pictures"]["msg_picture_reject"])))
            await user.send(embed=embed)
            connection.commit()
            connection.close()
        cursor.execute('DELETE FROM requests Where message_id = ?', (inter.message.id,))
        connect.commit()

        await inter.response.edit_message(f'Отклонил {inter.user.mention}', view=None)

def setup(bot: commands.Bot):
    bot.add_cog(requestCallback(bot))

