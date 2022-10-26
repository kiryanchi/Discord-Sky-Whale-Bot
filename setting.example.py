# 파일 이름을 setting.py 로 변경하고 사용
# setting.example.py -> setting.py

# Token
TOKEN = ""

# Debug Mode
# if True, set log level to 'debug'
# Command will be guild command only
DEBUG = True

# Commands
# src.cogs.{comamnd}.{command}.py
# ex) src.cogs.music.music.py -> ["music"]
COMMANDS = ["music"]

# Prefix
COMMAND_PREFIX = "."

# Enter admin guild id
# This guild will be test guild that using guild command (debug mode)
ADMIN_GUILD_ID = 123

# DB file path
# If no file there, create new file
DB_FILE = "statics/sky_whale.db"

# Embed color
# This bot's identity is "Sky Whale". So I choose sky-blue color
COLOR = 0x8AFDFD

# Default playlist image
URL = "https://cdn.discordapp.com/attachments/963347486720798770/963347758067093544/unknown.png"

# Num of youtube search result
# Max: 25 (if over, occur error)
NUM_OF_SEARCH = 10
