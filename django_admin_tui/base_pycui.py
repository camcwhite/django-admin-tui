from typing import List

import py_cui

from .tui_form import Form


# override and add some library methods
class BasePyCUI(py_cui.PyCUI):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.screens = {}
        

    # mostly copied from the library, just adding default text option
    def show_text_box_popup(self, title, command, text="", password=False):
        self._popup = py_cui.popups.TextBoxPopup(self, title, py_cui.WHITE_ON_BLACK, command, self._renderer, password, self._logger)
        self._logger.debug(f'Opened {str(type(self._popup))} popup with title {title}')
        self._popup.set_text(text)
        # shift cursor to end of text
        for _ in text:
            self._popup._move_right()

    def add_form(self, title: str, fields: List[dict], row: int, column: int, row_span: int=1, column_span: int=1, padx: int=1, pady: int=0, on_submit=None) -> Form:
        id = len(self.get_widgets().keys())
        if on_submit is None:
            def _on_submit():
                self.show_message_popup('Form submitted', 'Form submitted successfully.')

            on_submit = _on_submit

        if self._renderer is None:
            raise Exception(self.__class__)
        new_form = Form(id,
                        title,
                        fields,
                        self._grid,
                        self,
                        row,
                        column,
                        row_span,
                        column_span,
                        padx,
                        pady,
                        self._renderer,
                        self._logger,
                        on_submit)

        self.get_widgets()[id]  = new_form
        if self._selected_widget is None:
            self.set_selected_widget(id)
        self._logger.info(f'Adding widget {title} w/ ID {id} of type {str(type(new_form))}')
        return new_form

    def _initialize_widget_renderer(self) -> None:
        super()._initialize_widget_renderer()
        for screen in self.screens.values():
            screen._renderer = self._renderer

# also add the add_form to the WidgetSet class, which seems to duplicate PyCUI
py_cui.widget_set.WidgetSet.add_form = BasePyCUI.add_form