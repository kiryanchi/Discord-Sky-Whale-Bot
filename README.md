# <center> Discord Music Bot

Discord Music Bot with Youtube

English is not my language.

한국인 가이드도 추가할 예정입니다.

---

## Library

- [**discord.py**](https://github.com/Rapptz/discord.py)
- [**youtube_dl**](https://github.com/ytdl-org/youtube-dl)
- [**discord components**](https://github.com/kiki7000/discord.py-components)
- [**youtube-search-python**](https://github.com/alexmercerind/youtube-search-python)

---

## Usage

### 1. Make `conf.json` by referring to `conf.example.json`  

```json
// JSON has no comment originally. Written for convenience.
// Essentially no difference between dev and prod
// Just because seperate bot for dev
// ex) prod: musicbot dev: muscbot-test
{
 "dev": {    // Setting for Develop
  "token": "...",   // Bot API Token
  "default_command_prefix": "...",  // Prefix
  "db": "..."   // Database
 },
 "prod": {   // Setting for Product
  "token": "...",
  "default_command_prefix": "...",
  "db": "..."
 }
}
```

### 2. Install Library for bot

```bash
# for Python3 (not Python2)
$ pip3 install -r req.txt
```

### 3. Run main.py

```bash
# for Product
$ python3 main.py

# for dev
$ python3 main.py dev
```

### 4. Go to text channel and enter start command

```bash
# You have to have a Administrator permission.
(prefix)init # aliases 초기화, 시작, start
```

### 5. Then Sky Whale will come to channel.

![init image](https://cdn.discordapp.com/attachments/963347486720798770/966971459610226688/Screen_Shot_2022-04-22_at_4.59.04_PM.png)

### 6. Click button `여기에 날아다니렴`

![player image](https://cdn.discordapp.com/attachments/963347486720798770/966971459811561512/Screen_Shot_2022-04-22_at_4.40.37_PM.png)

### **This channel will be music channel!**

---

## Feature

### 1. No command for music search

**Just work in music channel**

Chat music you want in music channel

or Paste Youtube link. (Not a playlist)

![search image](https://cdn.discordapp.com/attachments/963347486720798770/966978344467988510/unknown.png)

Select number you want to play

### 2. Button Interaction

button | button | button | button | button
---|:---:|:---:|:---:|---:
 Pause | Resume | Skip | Shuffle | Help
 First | Prev | Next | Last | Youtube

### 3. Music Queue

![queue image](https://cdn.discordapp.com/attachments/963347486720798770/966978269851287562/unknown.png)

if bot is playing music, next music is in queue.

Too long music title will be shorten. (blablah...)

---

## Will add feature

- [ ] log system
- [ ] timestamp
- [ ] user's playlist
- [ ] bot leave voice channel after 5 minutes
- [ ] when bot join a server, edit role color and seperate.