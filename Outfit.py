class Outfit:
    def __init__(self):
        self._user_head = "https://findathreadcontainer.blob.core.windows.net/imagestorage/head.jpg"
        self._user_top = "https://findathreadcontainer.blob.core.windows.net/imagestorage/Top.jpg"
        self._user_bottom = "https://findathreadcontainer.blob.core.windows.net/imagestorage/Bottom.jpg"
        self._user_shoes = "https://findathreadcontainer.blob.core.windows.net/imagestorage/shoes.jpg"

    @property
    def user_head(self):
        return self._user_head

    @user_head.setter
    def user_head(self, new_url):
        # Optional validation or processing before setting the new URL
        self._user_head = new_url

    @property
    def user_top(self):
        return self._user_top

    @user_top.setter
    def user_top(self, new_url):
        # Optional validation or processing before setting the new URL
        self._user_top = new_url

    @property
    def user_bottom(self):
        return self._user_bottom

    @user_bottom.setter
    def user_bottom(self, new_url):
        # Optional validation or processing before setting the new URL
        self._user_bottom = new_url

    @property
    def user_shoes(self):
        return self._user_shoes

    @user_shoes.setter
    def user_shoes(self, new_url):
        # Optional validation or processing before setting the new URL
        self._user_shoes = new_url


