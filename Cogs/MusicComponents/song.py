class Song:
    def __init__(self, info):
        self.__info = info
        self.__title = info["title"]
        self.__link = info["link"]
        self.__thumbnail = info["thumbnails"][0]["url"]

    @property
    def title(self):
        return self.__title

    @property
    def link(self):
        return self.__link

    @property
    def thumbnail(self):
        return self.__thumbnail

    def __str__(self):
        return self.__info
