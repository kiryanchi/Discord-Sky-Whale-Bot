class Song:
    def __init__(self, id, title, url):
        self._id = id
        self._title = title
        self._url = url

    def __str__(self):
        return dict({"id": self._id, "title": self._title, "url": self._url})

    @property
    def id(self):
        return self._id

    @property
    def title(self):
        return self._title

    @property
    def url(self):
        return self._url
