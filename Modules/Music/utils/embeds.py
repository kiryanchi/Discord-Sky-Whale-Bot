import discord


class Embed:
    COLOR = 0x8AFDFD
    URL = "https://cdn.discordapp.com/attachments/963347486720798770/963347758067093544/unknown.png"
    CURRENT_SONG_NAME: str = "현재 재생중인 노래"
    NEXT_SONGS_NAME: str = "대기중인 노래"

    @classmethod
    def init(cls):
        embed = (
            discord.Embed(title="하늘 고래가 이 곳을 떠다니고 싶어합니다.", color=cls.COLOR)
            .set_image(url=cls.URL)
            .set_footer(text="수락을 누르면 이 채널을 음악 채널로 사용합니다.")
        )
        return embed

    @classmethod
    def playlist(cls, playlist):
        # TODO: 아직 미완성

        embed = (
            discord.Embed(title="\u2000" * 5 + "Sky Whale", color=cls.COLOR)
            .set_thumbnail(url=cls.URL)
            .set_footer(text="노래를 검색해서 추가하세요.")
        )

        # 현재 재생중 갱신
        if not (song := playlist.get_current_song()):
            embed.add_field(
                name=cls.CURRENT_SONG_NAME, value="하늘 고래가 쉬고있어요", inline=False
            )
        else:
            embed.add_field(name=cls.CURRENT_SONG_NAME, value=f"{song.title}")

        # 대기중인 노래 갱신
        if not (next_songs := playlist.get_next_songs()):
            embed.add_field(name=cls.NEXT_SONGS_NAME, value="다음 곡이 없어요")
        else:
            next_songs = "\n".join(next_songs)
            embed.add_field(name=cls.NEXT_SONGS_NAME, value=f"{next_songs}")

        return embed

    @classmethod
    def search(cls, content, info):
        embed = discord.Embed(title=f"{content} 검색 결과", color=cls.COLOR).set_thumbnail(
            url=cls.URL
        )

        for i in range(len(info)):
            embed.add_field(
                name=f"{i+1:2d}번\t({info[i]['duration']}) {info[i]['channel']['name']}",
                value=f"제목: {info[i]['title']}",
                inline=False,
            )

        return embed
