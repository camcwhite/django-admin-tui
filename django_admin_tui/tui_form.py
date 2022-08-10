from typing import List

import py_cui
from py_cui.dialogs.form import Form as BaseForm
from py_cui.dialogs.form import FormFieldElement, FormImplementation
from py_cui.widgets import Widget


# the library is just missing this implementation, adapted from ScrollMenu 
class Form(BaseForm):
    def __init__(self, id, title: str, fields: List[dict], grid: 'py_cui.grid.Grid', screen, row: int, column: int, row_span: int, column_span: int, padx: int, pady: int, renderer: 'py_cui.renderer.Renderer', logger: 'py_cui.debug.PyCUILogger', on_submit=None):
        Widget.__init__(self, id, title, grid, row, column, row_span, column_span, padx, pady, logger)

        # create fields, as in FormPopup
        self._form_fields = []
        required_fields = []
        for i, field_info in enumerate(fields):
            init_text = ''
            if 'init_text' in field_info:
                init_text = field_info['init_text']
            required = field_info.get('required', False)
            self._form_fields.append(FormFieldElement(self, 
                                              i, 
                                              field_info['name'], 
                                              init_text, 
                                              field_info.get('password', False), 
                                              required, 
                                              renderer,
                                              logger))

            if required:
                required_fields.append(field_info['name'])

        if renderer is not None:
            self._assign_renderer(renderer)

        if self._form_fields:
            self._form_fields[0].set_selected(True)
        FormImplementation.__init__(self, self._form_fields, required_fields, logger)

        self.set_help_text('Focus mode on Form. Use TAB to navigate, ENTER to select a field, Esc to exit.')

        self.on_submit = on_submit 

        # store screen so we can make popups
        self.screen = screen
        self._popup = None

    def add_field(self, name, init_text=None, required=False, password=False):
        if init_text is None:
            init_text = ''
        id = len(self._form_fields)
        self._form_fields.append(FormFieldElement(self, 
                                            id, 
                                            name, 
                                            init_text, 
                                            password, 
                                            required, 
                                            self._renderer,
                                            self._logger))
        if required:
            self._required_fields.append(name)

    def clear_fields(self):
        self._form_fields = []
        self._selected_form_index = 0


    # no mouse events yet
    # def _handle_mouse_press(self, x: int, y: int, mouse_event: int):
    #     """Override of base class function, handles mouse press in menu

    #     Parameters
    #     ----------
    #     x, y : int
    #         Coordinates of mouse press
    #     """

    #     # For either click or double click we want to jump to the clicked-on item
    #     if mouse_event == py_cui.keys.LEFT_MOUSE_CLICK or mouse_event == py_cui.keys.LEFT_MOUSE_DBL_CLICK:
    #         current = self.get_selected_item_index()
    #         viewport_top = self._start_y + self._pady + 1

    #         if viewport_top <= y and viewport_top + len(self._view_items) - self._top_view >= y:
    #             elem_clicked = y - viewport_top + self._top_view
    #             self.set_selected_item_index(elem_clicked)
        
    #         if self.get_selected_item_index() != current and self._on_selection_change is not None:
    #             self._process_selection_change_event()

    #     # For scroll menu, handle custom mouse press after initial event, since we will likely want to
    #     # have access to the newly selected item
    #     Widget._handle_mouse_press(self, x, y, mouse_event)



    def _handle_key_press(self, key_pressed: int) -> None:
        """Override base class function.

        UP_ARROW scrolls up, DOWN_ARROW scrolls down.

        Parameters
        ----------
        key_pressed : int
            key code of key pressed
        """

        Widget._handle_key_press(self, key_pressed)
        
        if key_pressed == py_cui.keys.KEY_TAB:
            self._form_fields[self.get_selected_form_index()].set_selected(False)
            self.jump_to_next_field()
            self._form_fields[self.get_selected_form_index()].set_selected(True)
        elif key_pressed == py_cui.keys.KEY_ENTER:
            valid, err_msg = self.is_submission_valid()
            if not valid:
                self._popup = self.screen.show_message_popup("Error submitting form:", 
                                                            err_msg,
                                                            py_cui.YELLOW_ON_BLACK) 
            else:
                if self.on_submit:
                    self.on_submit()
        else:
            if self.get_selected_form_index() < len(self._form_fields):
                self._form_fields[self.get_selected_form_index()]._handle_key_press(key_pressed)

    def get_num_fields(self) -> int:
        """Getter for number of fields

        Returns
        -------
        num_fields : int
            Number of fields in form
        """

        return len(self._form_fields)

    def is_form_ready(self):
        return bool(self._form_fields)

    def _draw(self) -> None:
        """Overrides base class draw function
        """

        Widget._draw(self)
        self._renderer.set_color_mode(self._color)
        self._renderer.set_color_rules([])
        self._renderer.draw_border(self)

        for i, form_field in enumerate(self._form_fields):
            if i != self.get_selected_form_index():
                form_field._draw()

        try:
            self._form_fields[self.get_selected_form_index()]._draw()
        except IndexError:
            raise IndexError(f'len={len(self._form_fields)}, index={self.get_selected_form_index()}')

        # self._renderer.set_color_mode(self._color)
        # self._renderer.draw_border(self)
        # counter = self._pady + 1
        # line_counter = 0
        # for item in self._view_items:
        #     line = str(item)
        #     if line_counter < self._top_view:
        #         line_counter = line_counter + 1
        #     else:
        #         if counter >= self._height - self._pady - 1:
        #             break
        #         if line_counter == self._selected_item:
        #             self._renderer.draw_text(self, line, self._start_y + counter, selected=True)
        #         else:
        #             self._renderer.draw_text(self, line, self._start_y + counter)
        #         counter = counter + 1
        #         line_counter = line_counter + 1
        # self._renderer.unset_color_mode(self._color)
        # self._renderer.reset_cursor(self)

