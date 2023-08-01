class User:
    def __init__(self):
        self._current_user = -1
        self._current_wardrobe = ""

    @property
    def current_user(self):
        return self._current_user

    @current_user.setter
    def current_user(self, user_id):
        self._current_user = user_id

    @property
    def current_wardrobe(self):
        return self._current_wardrobe

    @current_wardrobe.setter
    def current_wardrobe(self, wardrobe):
        self._current_wardrobe = wardrobe
