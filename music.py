###import
import discord
from discord.ext import commands

import youtube_dl
import pafy
import datetime

###klasa


class music(commands.Cog):

    ##początek

    def __init__(self, client):
        self.client = client
        self.song_queue = {}

        self.is_playing = False

        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        self.FFMPEG_OPTIONS = {
            'before_options':
            '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

        self.setup()

    #kolejka

    def setup(self):
        for guild in self.client.guilds:
            self.song_queue[guild.id] = []

    async def check_queue(self, ctx):

        print(' * checking queue')
        if len(self.song_queue[ctx.guild.id]) > 0:
            await self.play_song(ctx, self.song_queue[ctx.guild.id][0])
            self.song_queue[ctx.guild.id].pop(0)

    #wyszukiwarka

    async def search_song(self, amount, song, get_url=False):

        print(' * searching for:', song)

        info = await self.client.loop.run_in_executor(
            None, lambda: youtube_dl.YoutubeDL(self.YDL_OPTIONS).extract_info(
                f'ytsearch{amount}:{song}',
                download=False,
                ie_key='YoutubeSearch'))

        if len(info['entries']) == 0:
            return None

        return [entry['webpage_url']
                for entry in info['entries']] if get_url else info

    #puszczanie muzyki

    async def play_song(self, ctx, song):

        url = pafy.new(song).getbestaudio().url
        print(url)

        ctx.voice_client.play(discord.FFmpegPCMAudio(url,
                                                     **self.FFMPEG_OPTIONS),
                              after=lambda error: self.client.loop.create_task(
                                  self.check_queue(ctx)))

        print(' * playing song:', (song))

        embed = discord.Embed(description=f'🎶 | Teraz odtwarzam: {song}',
                              colour=discord.Colour.blue())

        queue_len = len(self.song_queue[ctx.guild.id])
        if queue_len != 0:
            queue_len += -1

        embed.set_footer(text=f'(Obecnie w kolejce: {queue_len})')
        embed.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=embed)

    #zabezpieczenia

    async def zabezpieczenia(self, ctx):
        if ctx.voice_client is None:
            await ctx.message.add_reaction("❌")

            embed1 = discord.Embed(
                description='Nie ma mnie na żadnym kanale głosowym!',
                colour=discord.Colour.dark_purple())

            await ctx.send(embed=embed1)

        elif ctx.author.voice is None or ctx.author.voice.channel.id != ctx.voice_client.channel.id:
            await ctx.message.add_reaction("❌")

            embed2 = discord.Embed(
                description='Musisz być na kanale głosowym razem ze mną!',
                colour=discord.Colour.dark_purple())

            await ctx.send(embed=embed2)

        else:
            return True

##slash commands

#puszczanie muzyki

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, song=None):

        result = await self.search_song(1, song, get_url=True)

        if ctx.author.voice is None:
            await ctx.message.add_reaction("❌")

            embed = discord.Embed(
                description='Musisz najpierw dołączyć na kanał głosowy!',
                colour=discord.Colour.dark_purple())

            await ctx.send(embed=embed)

        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()

        else:
            await ctx.voice_client.move_to(ctx.author.voice.channel)

        if song is None:
            await ctx.message.add_reaction("❌")

            embed = discord.Embed(
                description=
                'Musisz jeszcze wpisać nazwę utworu lub link YouTube!',
                colour=discord.Colour.dark_purple())

            await ctx.send(embed=embed)

        if song is not None and not ('youtube.com/watch?' in song
                                     or 'youtu.be/' in song):
            await ctx.message.add_reaction("✅")

            embed1 = discord.Embed(
                description=f'🔍 | Szukam: `{song}`, może to chwilę zająć...',
                colour=discord.Colour.dark_purple())

            await ctx.send(embed=embed1)

            if result is None:

                embed2 = discord.Embed(
                    description='Nie znalazłem takiego utworu.',
                    colour=discord.Colour.red())

                await ctx.send(embed=embed2)

            else:
                song = result[0]

                embed = discord.Embed(description=f'🎶 | Znalazłem: {song}',
                                      colour=discord.Colour.blue())

                await ctx.send(embed=embed)

        if ctx.voice_client.source is not None:
            queue_len = len(self.song_queue[ctx.guild.id])

            if queue_len < 20 and song is not None and result is not None:
                await ctx.message.add_reaction("✅")
                self.song_queue[ctx.guild.id].append(song)

                embed1 = discord.Embed(
                    description=
                    f'➕ | Dodałem twój utwór do kolejki. (**{queue_len+1}**/20)',
                    colour=discord.Colour.purple())

                await ctx.send(embed=embed1)
                print(' * added to queue')

            elif song is not None and result is not None:

                embed2 = discord.Embed(
                    description=
                    'Osiągnięto **limit 20 utworów** w kolejne. Poczekaj, aż zwolni się miejsce.',
                    colour=discord.Colour.purple())

                await ctx.send(embed=embed2)

        #warunkowanie puszczanie muzyki

        if song is None or result is None:
            print(' * wrong name of song')

        elif ctx.voice_client.is_playing():
            print(' * bot is already playing music')

        elif song is not None and result is not None:
            await self.play_song(ctx, song)

    #kolejka

    @commands.command(aliases=['q'])
    async def queue(self, ctx):

        if ctx.voice_client is None:
            await ctx.message.add_reaction("❌")

            embed1 = discord.Embed(
                description='Nie ma mnie na żadnym kanale głosowym!',
                colour=discord.Colour.purple())
            await ctx.send(embed=embed1)

        elif len(self.song_queue[ctx.guild.id]) == 0:
            await ctx.message.add_reaction("✅")

            embed1 = discord.Embed(
                description='Obecnie nie ma żadnych utworów w kolejce.',
                colour=discord.Colour.purple())

            await ctx.send(embed=embed1)

        else:
            await ctx.message.add_reaction("✅")

            embed2 = discord.Embed(title='Kolejka utworów:',
                                   description='',
                                   colour=discord.Colour.purple())

            i = 1
            for url in self.song_queue[ctx.guild.id]:
                embed2.description += f'{i}) {url}\n'
                i += 1
            await ctx.send(embed=embed2)

    #pomijanie

    @commands.command(aliases=['s'])
    async def skip(
        self,
        ctx,
    ):

        zabezpieczenia = await self.zabezpieczenia(ctx)
        if zabezpieczenia is True:

            if ctx.voice_client.is_playing():

                await ctx.message.add_reaction("✅")
                ctx.voice_client.stop()

                embed1 = discord.Embed(description='⏭️ | Pominiąłem utwór.',
                                       colour=discord.Colour.dark_purple())

                await ctx.send(embed=embed1)
                await self.check_queue(ctx)

                print(' * song skipped')

            else:
                await ctx.message.add_reaction("❌")
                embed2 = discord.Embed(
                    description='Obecnie nie gram żadnego utworu!',
                    colour=discord.Colour.dark_purple())

                await ctx.send(embed=embed2)

    #wstrzymanie muzyki

    @commands.command()
    async def pause(self, ctx):

        zabezpieczenia = await self.zabezpieczenia(ctx)
        if zabezpieczenia is True:

            if ctx.voice_client.is_playing():

                await ctx.message.add_reaction("✅")
                ctx.voice_client.pause()

                embed1 = discord.Embed(
                    description='⏸️ | Wstrzymałem odtwarzanie.',
                    colour=discord.Colour.dark_purple())

                await ctx.send(embed=embed1)

            elif ctx.voice_client.is_paused():

                await ctx.message.add_reaction("✅")
                ctx.voice_client.resume()

                embed2 = discord.Embed(
                    description='▶️ | Wznowiłem odtwarzanie.',
                    colour=discord.Colour.dark_purple())

                await ctx.send(embed=embed2)

            else:
                await ctx.message.add_reaction("❌")
                embed3 = discord.Embed(
                    description='Obecnie nie gram żadnego utworu!',
                    colour=discord.Colour.dark_purple())

                await ctx.send(embed=embed3)

    #wznowienie muzyki

    @commands.command()
    async def resume(self, ctx):

        zabezpieczenia = await self.zabezpieczenia(ctx)
        if zabezpieczenia is True:

            if ctx.voice_client.is_paused():

                await ctx.message.add_reaction("✅")
                ctx.voice_client.resume()

                embed1 = discord.Embed(
                    description='▶️ | Wznowiłem odtwarzanie.',
                    colour=discord.Colour.dark_purple())

                await ctx.send(embed=embed1)

            else:
                await ctx.message.add_reaction("❌")
                embed2 = discord.Embed(
                    description='Obecnie nie jest zatrzymany żaden utwór.',
                    colour=discord.Colour.dark_purple())

                await ctx.send(embed=embed2)

    #obecnie odtwarzanie
    @commands.command(aliases=['n', 'now', 'nowplaying'])
    async def now_playing(self, ctx):

        embed = discord.Embed(description=f'💿T | eraz odtwarzam:',
                              colour=discord.Colour.blue())

        await ctx.send(embed=embed)

    #wyczyść kolejkę
    @commands.command(aliases=['c'])
    async def clear(self, ctx):

        zabezpieczenia = await self.zabezpieczenia(ctx)
        if zabezpieczenia is True:

            await ctx.message.add_reaction("✅")
            for guild in self.client.guilds:
                self.song_queue[guild.id] = []

            embed = discord.Embed(description='Wyczyściłem kolejkę utworów.',
                                  colour=discord.Colour.dark_purple())

            await ctx.send(embed=embed)

            print(' * queue cleared')

    #opuszczanie kanału

    @commands.command(aliases=['l'])
    async def leave(self, ctx):

        zabezpieczenia = await self.zabezpieczenia(ctx)
        if zabezpieczenia is True:

            await ctx.message.add_reaction('✅')
            await ctx.voice_client.disconnect()

            embed = discord.Embed(description='Opuściłem kanał głosowy.',
                                  colour=discord.Colour.dark_purple())

            await ctx.send(embed=embed)


##koniec


def setup(client):
    client.add_cog(music(client))
