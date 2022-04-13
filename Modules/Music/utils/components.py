from discord_components import Button, ButtonStyle


class Components:
    @classmethod
    def init(cls):
        components = [Button(style=ButtonStyle.green, label="여기에 앉으렴")]

        return components

    @classmethod
    def playlist(cls):
        components = [
            [
                Button(style=ButtonStyle.red, label="||"),
                Button(style=ButtonStyle.green, label="▷"),
                Button(style=ButtonStyle.blue, label="↻"),
                Button(style=ButtonStyle.grey, label="?"),
            ],
            [
                Button(style=ButtonStyle.grey, label="<"),
                Button(style=ButtonStyle.grey, label=">"),
                Button(style=ButtonStyle.grey, label="<<"),
                Button(style=ButtonStyle.grey, label=">>"),
            ],
        ]

        return components
