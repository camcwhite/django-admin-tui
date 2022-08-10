from py_cui.keys import KEY_ENTER, KEY_S_UPPER
from py_cui.popups import MenuPopup as BaseMenuPopup


class MenuPopup(BaseMenuPopup):
    def _handle_key_press(self, key_pressed: int) -> None:
        # changed events
        if key_pressed == KEY_ENTER:
            if getattr(self, 'skip_close_on_enter', False):
                # from the base implementation 
                ret_val = self.get()
                if self._command is not None:
                    if ret_val is not None or self._run_command_if_none:
                        self._command(ret_val)
                else:
                    self._root.show_warning_popup('No Command Specified', 'The menu popup had no specified command')

                return
            

        super()._handle_key_press(key_pressed)

        # added buttons

        if key_pressed == KEY_S_UPPER:
            if hasattr(self, 'save_command'):
                self.save_command()