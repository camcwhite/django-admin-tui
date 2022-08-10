from py_cui.popups import MessagePopup as BaseMessagePopup


class MessagePopup(BaseMessagePopup):
    def _handle_key_press(self, key_pressed: int) -> None:
        super()._handle_key_press(key_pressed)

        if key_pressed in self._close_keys and hasattr(self, 'on_close'):
            getattr(self, 'on_close')()