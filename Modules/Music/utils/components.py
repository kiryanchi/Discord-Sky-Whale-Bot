from discord_components import Button, ButtonStyle
from Modules.Music.components.queue import Queue


playlist_queue = Queue()


class Components:
    @classmethod
    def init(cls):
        components = [Button(style=ButtonStyle.green, label="여기에 앉으렴")]

        return components

    @classmethod
    def playlist(cls, app):
        async def callback(interaction):
            playlist = playlist_queue[f"{interaction.guild.id}"]
            custom_id = interaction.custom_id

            if custom_id == "pause":
                playlist.pause()
            elif custom_id == "resume":
                playlist.resume()
            elif custom_id == "shuffle":
                playlist.shuffle()
            elif custom_id == "help":
                playlist.help()
                return
            elif custom_id == "prev_page":
                playlist.prev_page()
            elif custom_id == "next_page":
                playlist.next_page()
            elif custom_id == "first_page":
                playlist.first_page()
            elif custom_id == "last_page":
                playlist.last_page()

            await interaction.send(
                interaction.custom_id, delete_after=5, ephemeral=False
            )

        components = [
            [
                app.components_manager.add_callback(
                    Button(style=ButtonStyle.red, label="||", custom_id="pause"),
                    callback,
                ),
                app.components_manager.add_callback(
                    Button(style=ButtonStyle.green, label="▷", custom_id="resume"),
                    callback,
                ),
                app.components_manager.add_callback(
                    Button(style=ButtonStyle.blue, label="↻", custom_id="shuffle"),
                    callback,
                ),
                app.components_manager.add_callback(
                    Button(style=ButtonStyle.grey, label="?", custom_id="help"),
                    callback,
                ),
            ],
            [
                app.components_manager.add_callback(
                    Button(style=ButtonStyle.grey, label="<", custom_id="prev_page"),
                    callback,
                ),
                app.components_manager.add_callback(
                    Button(style=ButtonStyle.grey, label=">", custom_id="next_page"),
                    callback,
                ),
                app.components_manager.add_callback(
                    Button(style=ButtonStyle.grey, label="<<", custom_id="first_page"),
                    callback,
                ),
                app.components_manager.add_callback(
                    Button(style=ButtonStyle.grey, label=">>", custom_id="last_page"),
                    callback,
                ),
            ],
        ]

        return components
