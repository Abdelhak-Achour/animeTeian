import discord
from discord.ext import commands
from discord.ext.commands.errors import MissingRequiredArgument
import discord.utils
import random
from mal import Anime
from mal import AnimeSearch

bot  = commands.Bot(command_prefix = "ota ",case_insensitive = True) # the bot client

#executes when bot is online
@bot.event
async def on_ready():
    await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = "mln anime_suggest genre/genre."))
    print("OtaBot online.")

#command for adding anime to "database"

@bot.command(hidden = True)
@commands.is_owner()
async def atdb(ctx,*,name):
    anime = Anime(AnimeSearch(name).results[0].mal_id)
    te = "None:no english title or other title."
    if not anime.title_english == None:
        te = anime.title_english
    malids = open("animelistfiles/malids.txt","a")
    malids.write(f'{AnimeSearch(name).results[0].mal_id}\n')
    malids.close()
    cats = open("animelistfiles/cats.txt","a")
    cats.write(f'{"/".join(x for x in anime.genres)}\n')
    cats.close()
    titles = open("animelistfiles/titles.txt","a",encoding = 'utf-8')
    titles.write(f'{anime.title}\n')
    titles.close()
    tes = open("animelistfiles/tes.txt","a",encoding = 'utf-8')
    tes.write(f'{te}\n')
    tes.close()
    await ctx.send(f'added {anime.title} ({te}) to the DataBase\nmalid = {AnimeSearch(name).results[0].mal_id}\ncats = {"/".join(y for y in anime.genres)}')
    anime.reload()

#error handler for atdb

@atdb.error
async def info_error(ctx,error):
    await ctx.send("either an error occured or you are not the bot owner.")

#command that searches for anime with the given genres and suggests the anime for the user

@bot.command(aliases = ["animesuggest","as"])
async def anime_suggest(ctx,*,genres):
    """mln anime_suggest genre/genre/genre or mln as genre/genre/genre"""
    g = genres.split("/")
    nmatches = [] # variable that will save in each element how much a line in cats file matches the given genres
    cats = open("animelistfiles/cats.txt","r")
    cats01  = cats.read().splitlines()

    #after reading the genres file and spiltting the lines we start searching

    for x in cats01:
        l = x.split("/")
        c = 0
        for y in g:
            if y == "slice of life" or y == "sol" or y == "Slice of life" or y == "Slice Of Life":
                y = "Slice of Life"
            elif y == "Slice of Life":
                pass
            elif y == "science fiction" or y == "Science Fiction" or y == "Science fiction" or y == "sci-fi" or y == "Sci-fi" or y == "science-fiction" or y == "Science-Fiction" or y == "Science-fiction":
                y = "Sci-Fi"
            elif y == "Sci-Fi":
                pass
            elif y == "martial arts" or y == "Martial arts":
                y = "Martial Arts"
            elif y == "Martial Arts":
                pass
            elif y == "Super power" or y == "super power":
                y = "Super Power"
            elif y == "Super Power":
                pass
            else:
                y = y[0].upper()+y[1:]
            if y in l:
                c += 1 # c increments in case there's a match of one genre of the given genres in the current line of the file's lines we are looping through.
            else:
                pass
        nmatches.append(c)

    #in case there are no matches this happens:

    if max(nmatches) == 0:
        await ctx.send("sorry i don't have any to recommend of those genres.")
        return

    #else this:

    cats.close()
    indexes = [z for z in range(len(nmatches)) if nmatches[z] == max(nmatches)]
    idindex = random.choice(indexes)
    malids = open("animelistfiles/malids.txt","r")
    malids01 = malids.read().splitlines()
    te = "no english title or other title."
    anime = Anime(malids01[idindex])
    malids.close()
    if not anime.title_english == None:
        te = anime.title_english

    #creating the embed for the discord messages
    
    panel = discord.Embed(title = f'{anime.title} ({te}):',description = anime.synopsis,color = discord.Color.blue())
    panel.set_thumbnail(url = anime.image_url)
    panel.add_field(name = ":medal:Score:",value = anime.score)
    panel.add_field(name = ":trophy:Rank:",value = anime.rank)
    panel.add_field(name = ":bar_chart:Popularity:",value = anime.popularity)
    panel.add_field(name = ":dividers:Type:",value = anime.type)
    panel.add_field(name = ":film_frames:Episodes:",value = anime.episodes)
    panel.add_field(name = ":label:Genres:",value = ", ".join(x for x in anime.genres))
    panel.add_field(name = ":clapper:Status:",value = anime.status)
    panel.add_field(name = ":satellite_orbital:Aired",value = anime.aired)
    panel.add_field(name = ":pencil2:Studios:",value = ", ".join(y for y in anime.studios))
    panel.add_field(name = ":stopwatch:Duration:",value = anime.duration)
    panel.add_field(name = ":bookmark_tabs:Source:",value = anime.source)
    panel.add_field(name = "URL for further info:",value = anime.url)
    panel.set_footer(text = "Info source: MyAnimeList. Visit site for further info.")
    await ctx.send(embed = panel)
    anime.reload()

#error handler for anime_suggest

@anime_suggest.error
async def info_error(ctx,error):
    if isinstance(error,commands.BadArgument):
        msg = discord.Embed(title = "error:",description = "non-valid entry.",color = discord.Color.red())
        await ctx.send(embed = msg,delete_after = 15)
    elif isinstance(error,MissingRequiredArgument):
        msg = discord.Embed(title = "error:",description = "give me some genres so i can choose one for you.\nif u want any anime from whatever genre then use the command any_anime_suggest.",color = discord.Color.red())
        await ctx.send(embed = msg,delete_after = 15)
    elif isinstance(error,TimeoutError):
        msg = discord.Embed(title = "error:",description = "request timed out, please try again. Better entry is better for this.",color = discord.Color.red())
        await ctx.send(embed = msg,delete_after = 15)
    else:
        msg_1 = discord.Embed(title = "error:",description = "an unknown error occured.",color = discord.Color.red())
        await ctx.send(embed = msg_1,delete_after = 15)
        print(error)

#command that will suggest any anime existing in the "database" 

@bot.command(aliases = ["anyanimesuggest","aas"])
async def any_anime_suggest(ctx):
    """mln anyanimesuggest or mln aas"""
    malids = open("animelistfiles/malids.txt","r")
    l = malids.read().splitlines()
    id = random.choice(l)
    te = "no english title or other title."
    anime = Anime(id)
    if not anime.title_english == None:
        te = anime.title_english
    panel = discord.Embed(title = f'{anime.title} ({te}):',description = anime.synopsis,color = discord.Color.blue())
    panel.set_thumbnail(url = anime.image_url)
    panel.add_field(name = ":medal:Score:",value = anime.score)
    panel.add_field(name = ":trophy:Rank:",value = anime.rank)
    panel.add_field(name = ":bar_chart:Popularity:",value = anime.popularity)
    panel.add_field(name = ":dividers:Type:",value = anime.type)
    panel.add_field(name = ":film_frames:Episodes:",value = anime.episodes)
    panel.add_field(name = ":label:Genres:",value = ", ".join(x for x in anime.genres))
    panel.add_field(name = ":clapper:Status:",value = anime.status)
    panel.add_field(name = ":satellite_orbital:Aired",value = anime.aired)
    panel.add_field(name = ":pencil2:Studios:",value = ", ".join(y for y in anime.studios))
    panel.add_field(name = ":stopwatch:Duration:",value = anime.duration)
    panel.add_field(name = ":bookmark_tabs:Source:",value = anime.source)
    panel.add_field(name = "URL for further info:",value = anime.url)
    panel.set_footer(text = "Info source: MyAnimeList. Visit site for further info.")
    await ctx.send(embed = panel)
    anime.reload()

#error handler for any_anime_suggest command

@any_anime_suggest.error
async def info_error(ctx,error):
    if isinstance(error,commands.BadArgument):
        msg = discord.Embed(title = "error:",description = "non-valid entry.",color = discord.Color.red())
        await ctx.send(embed = msg,delete_after = 15)
    elif isinstance(error,TimeoutError):
        msg = discord.Embed(title = "error:",description = "request timed out, please try again.",color = discord.Color.red())
        await ctx.send(embed = msg,delete_after = 15)
    else:
        msg_1 = discord.Embed(title = "error:",description = "an unknown error occured.",color = discord.Color.red())
        await ctx.send(embed = msg_1,delete_after = 15)
        print(error)

#run the bot with the hidden token

bot.run("TOKEN")