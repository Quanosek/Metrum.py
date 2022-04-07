import discord
from discord.ext import commands

#komendy do pomocy


class commands(commands.Cog):
    def __init__(self, client):
        self.client = client

    #pomoc

    @commands.command(aliases=['h'])
    async def help(self, ctx):
        await ctx.message.delete()

        embed = discord.Embed(
            title='Pamiętaj, że ten bot jest wciąż rozwijany!',
            description=
            'Mój prefix to ``!``, wypróbuj go!\n\nLista dostępnych komend:\n``!play`` (``!p``) - odtwarzanie piosenki, można wpisać frazę do wyszukania lub link url do YouTube\n``!skip`` (``!s``) - pomijanie utworu\n``!queue`` (``!q``) - wyświetlanie iformacji o zapisanej kolejce utworów\n``!clear`` (``!c``) - wyczyszczenie kolejki utworów\n``!pause`` - wstrzymanie/wznowienie utworu\n``!resume`` - wznowienie utworu\n``!leave`` (``!l``) - opuszczenie kanału głosowego przez bota\n\n Odwiedź również moją [stronę internetową](https://bit.ly/3Eyef7F)',
            colour=discord.Colour.dark_blue())

        await ctx.author.send(embed=embed)

    #przedstawienie się

    @commands.command(aliases=['hej'])
    async def hejka(self, ctx):
        await ctx.message.delete()

        embed = discord.Embed(
            title='Hejka!',
            description=
            'Google i YouTube ostatnio mocno walczą z botami muzycznymi i zamykają najpopularniejsze z nich.\nNa szczęście pojawiłem się ja i jestem tu, aby zagrać dla was dosłownie każdy utwór na waszych ulubionych kanałach głosowych!\n\n Pamiętajcie, że jestem wciąż dynamicznie rozwijamy i mogą się pojawiać z mojej strony przeróżne błędy, za które z góry przepraszam.\nWięcej informacji możecie znaleźć na mojej  [stronie internetowej](https://bit.ly/3Eyef7F)!',
            colour=discord.Colour.dark_blue())
        embed.set_thumbnail(url="https://i.ibb.co/wpbcB1q/bot-muzyczny.jpg")

        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(commands(client))
