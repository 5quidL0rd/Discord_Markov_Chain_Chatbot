import discord
from discord.ext import commands
import random
import re
from collections import defaultdict
from googleapiclient.discovery import build
import feedparser


# Wired RSS feed URL
WIRED_RSS_FEED = "https://www.wired.com/feed/rss"
# Intents give your bot the ability to access certain events
intents = discord.Intents.all()

# Create a bot instance with the specified command prefix
bot = commands.Bot(command_prefix='!', intents=intents)

# Markov chain data structure
markov_chain = defaultdict(list)

# YouTube API setup
YOUTUBE_API_KEY = 'key'  # Replace with your actual API key
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# List of space facts
space_facts = [
    "The Goldilocks zone is a misnomer!",
    "Jupiter and Saturn have no clear surface!",
    "Saturn has a density of less than water!",
    "The temperature of Venus is higher than that of Mercury.",
    "Venus has a higher concentration of deuterium in its atmosphere!"
]

launch_facts = [
    "The Falcon 9 is a workhorse rocket made by SpaceX.",
    "Starship, made by SpaceX, is a fully reusable spacecraft.",
    "Raptor Engines use a mixture of liquid methane and oxygen.",
    "Starlink is composed of over 4,000 satellites."
]

# YouTube channel IDs
CHANNEL_IDS = {
    'kurzgesagt': 'UCsXVk37bltHxD1rDPwtNM8Q',  # Kurzgesagt channel ID
    '3blue1brown': 'UCYO_jab_esuFRV4b17AJtAw',  # 3Blue1Brown channel ID
    'veritasium': 'UCHnyfMqiRRG1u-2MsSQLbXA',  # Veritasium channel ID
    'sebastian_lague': 'UCuWKHSHTHMFGkCFvU-zEDEA',  # Sebastian Lague channel ID
    'computerphile': 'UC9-y-6csu5WGm29I7JiwpnA',  # Computerphile channel ID
    'big_think': 'UCvQECJukTDE2i6aCoMnS-Vg'  # Big Think channel ID
}

# Music YouTube URLs
MUSIC_URLS = {
    'studymusic': 'https://www.youtube.com/watch?v=jfKfPfyJRdk',  # Lo-fi Girl 24/7 livestream
    'yoyoma': 'https://www.youtube.com/watch?v=qrdj2wplBWM',  # Yo-Yo Ma playlist
    'lambert': 'https://www.youtube.com/watch?v=qr1LMUKqVYs&list=OLAK5uy_lPs0FwC2QioQt7Y6At48aFqbIlzW0bnDs',  # Lambert's YouTube Channel
    'Warhammer': 'https://www.youtube.com/watch?v=aJIDqYZ7qM0', #Mechanicus whatever it is 
}


# Function to fetch the latest videos from a YouTube channel
def get_latest_video(channel_id):
    request = youtube.search().list(
        part='snippet',
        channelId=channel_id,
        maxResults=1,  # Fetch the latest video
        order='date',
        type='video'
    )
    response = request.execute()
    if response['items']:
        video = response['items'][0]
        video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
        return video_url
    return None


# Function to fetch the latest Wired articles
def get_latest_wired_articles(limit=5):
    feed = feedparser.parse(WIRED_RSS_FEED)
    articles = []
    
    for entry in feed.entries[:limit]:  # Limit to the number of articles you want to fetch
        title = entry.title
        link = entry.link
        articles.append(f"{title}: {link}")
    
    return articles


#Code modified from https://healeycodes.com/generating-text-with-markov-chains
# Function to build Markov chain
def build_markov_chain(text, state_size=2):
    words = text.split()
    for i in range(len(words) - state_size):
        current_state = tuple(words[i:i + state_size])
        next_word = words[i + state_size]
        markov_chain[current_state].append(next_word)

def generate_text(start_state, length=20):
    current_state = start_state
    result = list(current_state)
    for _ in range(length - len(current_state)):
        if current_state not in markov_chain:
            break
        next_word = random.choice(markov_chain[current_state])
        result.append(next_word)
        current_state = tuple(result[-len(current_state):])
    return ' '.join(result)

def remove_forbidden_word(text, forbidden_word="buzz"):
    return re.sub(r'\b' + re.escape(forbidden_word) + r'\b', '', text, flags=re.IGNORECASE)

def safe_generate_text(start_state, length=20):
    text = generate_text(start_state, length)
    return remove_forbidden_word(text)

# Event: When bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')

# Event: Handle messages
@bot.event
async def on_message(message):
    global space_fact_index
    global launch_fact_index

    if message.author.bot:
        return

    # Respond to "space fact"
    if message.content.lower() == "buzz space fact":
        if space_facts:
            await message.channel.send(space_facts[space_fact_index])
            space_fact_index = (space_fact_index + 1) % len(space_facts)
        else:
            await message.channel.send("No space facts available.")
        return

    # Respond to "launch fact"
    if message.content.lower() == "buzz launch fact":
        if launch_facts:
            await message.channel.send(launch_facts[launch_fact_index])
            launch_fact_index = (launch_fact_index + 1) % len(launch_facts)
        else:
            await message.channel.send("No launch facts available.")
        return

    # Markov chain handling
    if "buzz" in message.content.lower() and message.author.id != 1275576539689254983:
        clean_content = re.sub(r'<@!?(\d+)>', '', message.content)  # Remove mentions
        build_markov_chain(clean_content.lower())
        rng = random.randint(1, 480)
        if rng <= 340:
            response = buzz.get_appended_output(message.guild.id, 2)
        elif rng <= 415:
            response = buzz.get_appended_output(message.guild.id, 3)
        elif rng <= 465:
            response = buzz.get_appended_output(message.guild.id, 4)
        else:
            response = buzz.get_appended_output(message.guild.id, 5)
        await message.channel.send(response)

    await bot.process_commands(message)

# Command: Fetch the latest Kurzgesagt video
@bot.command(name="kurzgesagt")
async def fetch_kurzgesagt_video(ctx):
    video_url = get_latest_video(CHANNEL_IDS['kurzgesagt'])
    if video_url:
        await ctx.send(f"Latest Kurzgesagt video: {video_url}")
    else:
        await ctx.send("Couldn't fetch Kurzgesagt's latest video. Please try again later.")

# Command: Fetch the latest 3Blue1Brown video
@bot.command(name="3blue1brown")
async def fetch_3blue1brown_video(ctx):
    video_url = get_latest_video(CHANNEL_IDS['3blue1brown'])
    if video_url:
        await ctx.send(f"Latest 3Blue1Brown video: {video_url}")
    else:
        await ctx.send("Couldn't fetch 3Blue1Brown's latest video. Please try again later.")


# Command: Fetch the latest Veritasium video
@bot.command(name="veritasium")
async def fetch_veritasium_video(ctx):
    video_url = get_latest_video(CHANNEL_IDS['veritasium'])
    if video_url:
        await ctx.send(f"Latest Veritasium video: {video_url}")
    else:
        await ctx.send("Couldn't fetch Veritasium's latest video. Please try again later.")

# Command: Fetch the latest Sebastian Lague video
@bot.command(name="sebastian_lague")
async def fetch_sebastian_lague_video(ctx):
    video_url = get_latest_video(CHANNEL_IDS['sebastian_lague'])
    if video_url:
        await ctx.send(f"Latest Sebastian Lague video: {video_url}")
    else:
        await ctx.send("Couldn't fetch Sebastian Lague's latest video. Please try again later.")

# Command: Fetch the latest Computerphile video
@bot.command(name="computerphile")
async def fetch_computerphile_video(ctx):
    video_url = get_latest_video(CHANNEL_IDS['computerphile'])
    if video_url:
        await ctx.send(f"Latest Computerphile video: {video_url}")
    else:
        await ctx.send("Couldn't fetch Computerphile's latest video. Please try again later.")

# Command: Fetch the latest Big Think video
@bot.command(name="big_think")
async def fetch_big_think_video(ctx):
    video_url = get_latest_video(CHANNEL_IDS['big_think'])
    if video_url:
        await ctx.send(f"Latest Big Think video: {video_url}")
    else:
        await ctx.send("Couldn't fetch Big Think's latest video. Please try again later.")


# Command: Provide study music (Lo-fi Girl)
@bot.command(name="studymusic")
async def fetch_studymusic(ctx):
    await ctx.send(f"Here's some chill study music for you: {MUSIC_URLS['studymusic']}")

# Command: Provide Yo-Yo Ma music
@bot.command(name="yoyoma")
async def fetch_yoyoma(ctx):
    await ctx.send(f"Enjoy some Yo-Yo Ma music: {MUSIC_URLS['yoyoma']}")

# Command: Provide Lambert's music
@bot.command(name="lambert")
async def fetch_lambert(ctx):
    await ctx.send(f"Check out music from Lambert: {MUSIC_URLS['lambert']}")


@bot.command(name="mechanicus")
async def fetch_mechanicus(ctx):
    await ctx.send(f"Check out this weird music: {MUSIC_URLS['Warhammer']}")



    # Command: Fetch the latest Wired articles
@bot.command(name="wired")
async def fetch_wired_articles(ctx):
    articles = get_latest_wired_articles(limit=5)  # Fetch 5 articles
    if articles:
        response = "\n".join(articles)
        await ctx.send(f"Here are the latest Wired articles:\n{response}")
    else:
        await ctx.send("Couldn't fetch Wired articles at the moment. Please try again later.")

# Command: Respond to !ping with 'Pong!'
@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

# Replace with actual Markov logic for generating output
def get_appended_output(guild_id, state_size):
    if not markov_chain:
        return "No sufficient data to generate text."
    start_state = random.choice(list(markov_chain.keys()))
    return safe_generate_text(start_state, length=20)

# Define buzz object
buzz = type('Buzz', (object,), {'get_appended_output': get_appended_output})


# Run the bot with your token
TOKEN = 'key'  # Replace with your actual bot token
bot.run(TOKEN)

