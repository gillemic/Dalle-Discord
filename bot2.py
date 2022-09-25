# Created by RawandShaswar @ 08/06/2022, 7:00
from Classes import Dalle

# Builtin
import asyncio
import os
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import Union
from datetime import datetime

# Discord
import discord

# PyYaml
import yaml
from discord import Embed
from discord.ext import commands
from discord import app_commands

""" Load the configuration file """
with open("data.yaml") as f:
    c = yaml.safe_load(f)

def del_dir(target: Union[Path, str], only_if_empty: bool = False):
    """
    Delete a given directory and its subdirectories.

    :param target: The directory to delete
    :param only_if_empty: Raise RuntimeError if any file is found in the tree
    """
    target = Path(target).expanduser()
    if not target.is_dir():
        raise RuntimeError(f"{target} is not a directory")

    for p in sorted(target.glob('**/*'), reverse=True):
        if not p.exists():
            continue
        p.chmod(0o666)
        if p.is_dir():
            p.rmdir()
        else:
            if only_if_empty:
                raise RuntimeError(f'{p.parent} is not empty!')
            p.unlink()
    target.rmdir()

class DallEDiscordBot(discord.Client):
    """
    Creates a discord bot.
    """

    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.synced = False

    async def on_ready(self):
        """
        When the bot is ready.
        :return:
        """
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync()
            self.synced = True
        print("Made with ❤️ by Rawand Ahmed Shaswar in Kurdistan")
        print("Bot is online!\nCall !dalle <query>")

    def create_embed(self, guild) -> Embed:
        """
        Creates an embed object.
        :param guild:
        :return:
        """
        footer = self.get_footer()

        embed = discord.Embed(title=footer[0], color=footer[2])
        embed.set_author(name="https://huggingface.co", url="https://huggingface.co/spaces/dalle-mini/dalle-mini")

        embed.set_thumbnail(url=footer[1])
        embed.set_footer(text=footer[0], icon_url=footer[1])

        return embed

    @staticmethod
    def get_footer() -> list:
        """
        Gets the footer information from the config file.
        :return:
        """
        return [c['embed_title'], c['icon_url'], c['embed_color']]

    @staticmethod
    async def _create_collage(interaction, query: str, source_image: Image, images: list) -> str:
        width = source_image.width
        height = source_image.height
        font_size = 30
        spacing = 16
        text_height = font_size + spacing
        new_im = Image.new('RGBA', (width * 3 + spacing * 2, height * 3 + spacing * 2 + text_height),
                           (0, 0, 0, 0))

        index = 0
        for i in range(0, 3):
            for j in range(0, 3):
                im = Image.open(images[index].path)
                im.thumbnail((width, height))
                new_im.paste(im, (i * (width + spacing), text_height + j * (height + spacing)))
                index += 1

        img_draw = ImageDraw.Draw(new_im)
        fnt = ImageFont.truetype("./FiraMono-Medium.ttf", font_size)
        img_draw.text((1, 0), query, font=fnt, fill=(0, 0, 0))
        img_draw.text((0, 1), query, font=fnt, fill=(0, 0, 0))
        img_draw.text((1, 2), query, font=fnt, fill=(0, 0, 0))
        img_draw.text((2, 1), query, font=fnt, fill=(0, 0, 0))
        img_draw.text((0, 0), query, font=fnt, fill=(0, 0, 0))
        img_draw.text((0, 2), query, font=fnt, fill=(0, 0, 0))
        img_draw.text((2, 0), query, font=fnt, fill=(0, 0, 0))
        img_draw.text((2, 2), query, font=fnt, fill=(0, 0, 0))
        img_draw.text((1, 1), query, font=fnt, fill=(255, 255, 255))
        new_im.save(f"./generated/{interaction.user.id}/art.png")
        return f"./generated/{interaction.user.id}/art.png"


bot = DallEDiscordBot()
tree = app_commands.CommandTree(bot)

async def background_task() -> None:
    """
    Any background tasks here.
    :return:
    """
    pass


@tree.command(name = "dalle", description = "send a blend")
async def self(interaction: discord.Interaction, query: str):
    # Check if query is empty
    if not query:
        await interaction.response.send_message("DALL·E: Invalid query\nPlease enter a query (e.g !dalle dogs on space).", ephemeral=True)
        return

    # Check if query is too long
    if len(query) > 100:
        await interaction.response.send_message("DALL·E: Invalid query\nQuery is too long.", ephemeral=True)
        return

    #check if not in specified channel
    if (interaction.channel.id not in [909957374045995038, 344317039160197124]):
        return

    #check if conor or justin
    if (interaction.author.id in [105884992055349248, 415407957371781123]):
        await interaction.response.send_message("Nope.")
        return

    #check if banned words
    if ((query.find("blackface") != -1) or (query.find("black face") != -1)):
        await interaction.response.send_message("Nope.", ephemeral=True)
        return

    print(f"[-] {interaction.user.nick} called !dalle {query}")

    message = await interaction.response.defer()

    try:
        dall_e = await Dalle.DallE(prompt=f"{query}", author=f"{interaction.user.id}")
        generated = await dall_e.generate()

        if len(generated) > 0:
            first_image = Image.open(generated[0].path)
            generated_collage = await bot._create_collage(interaction, '', first_image, generated)

            # Prepare the attachment
            now = datetime.now().strftime("%m-%d-%Y_%H:%M:%S")

            file = discord.File(generated_collage, filename=f"{now}_{query.replace(' ', '_')}.png")
            await interaction.followup.send(content=query, file=file)

            # Delete the message
            # await message.delete()

    except Dalle.DallENoImagesReturned:
        await interaction.followup.send(f"DALL·E mini api returned no images found for {query}.", ephemeral=True)
    except Dalle.DallENotJson:
        await interaction.followup.send("DALL·E API Serialization Error, please try again later.", ephemeral=True)
    except Dalle.DallEParsingFailed:
        await interaction.followup.send("DALL·E Parsing Error, please try again later.", ephemeral=True)
    except Dalle.DallESiteUnavailable:
        await interaction.followup.send("DALL·E API Error, please try again later.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send("Internal Error, please try again later.", ephemeral=True)
        await interaction.followup.send(repr(e), ephemeral=True)
    finally:
        # Delete the author folder in ./generated with author id, if exists
        del_dir(f"./generated/{interaction.user.id}")


async def main():
    async with bot:
        bot.loop.create_task(background_task())
        await bot.start(c['discord_token'])

# bot.run(c['discord_token'])
asyncio.run(main())
