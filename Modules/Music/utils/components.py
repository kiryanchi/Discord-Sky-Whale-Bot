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
            print(f"{interaction.guild.id}")
            print(playlist_queue.queue)
            playlist = playlist_queue[interaction.guild.id]
            print(playlist)
            custom_id = interaction.custom_id

            if custom_id == "pause":
                playlist.pause()
            elif custom_id == "resume":
                playlist.resume()
            elif custom_id == "shuffle":
                await playlist.shuffle()
            elif custom_id == "help":
                playlist.help()
                return
            elif custom_id == "prev_page":
                await playlist.prev_page()
            elif custom_id == "next_page":
                await playlist.next_page()
            elif custom_id == "first_page":
                await playlist.first_page()
            elif custom_id == "last_page":
                await playlist.last_page()

            await interaction.send(
                interaction.custom_id, delete_after=1, ephemeral=False
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
