import py_cui
from django.contrib.admin import site as admin_site
from py_cui import PyCUI, keys
from py_cui.widgets import Widget

from . import edit_model

TUI_DIMENSIONS = (9, 3)
MODEL_ADMINS = admin_site._registry 

def _require_selected_model(mtd):
    def _wrapper(self, *args, **kwargs):
        if not self.selected_model:
            self.move_focus(self.model_menu)
            return
        mtd(self, *args, **kwargs)
    return _wrapper

class MenuItem:
    def __init__(self, obj, row_text) -> None:
        self.obj = obj
        self.row_text = row_text

    def __str__(self) -> str:
        return self.row_text

# just a wrapper around py_cui.PyCUI
class Interface(PyCUI):
    TITLE = 'Django Admin TUI'
    NO_MODEL_CHOSEN = '<No model chosen>'

    def __init__(self):
        super().__init__(*TUI_DIMENSIONS)
        self.models = {}
        self.rows = []
        self.selected_model = None
        self.pk_name = None
        self.queryset = None
        self.search_text = None
        self.set_title(self.TITLE)

    # mostly copied from the library, just adding default text option
    def show_text_box_popup(self, title, command, text="", password=False):
        self._popup = py_cui.popups.TextBoxPopup(self, title, py_cui.WHITE_ON_BLACK, command, self._renderer, password, self._logger)
        self._logger.debug(f'Opened {str(type(self._popup))} popup with title {title}')
        self._popup.set_text(text)
        # shift cursor to end of text
        for _ in text:
            self._popup._move_right()

        
    # called after django has started
    def initialize(self):
        self._create_ui() 
        self._add_keybindings()
        self._populate_apps()
        # TODO: remove
        self.select_app('testapp')
        self.move_focus(self.model_menu)

    def _create_ui(self):
        self.app_menu = self.add_scroll_menu('Choose an app', 0, 0, row_span=3, column_span=1)
        self.model_menu = self.add_scroll_menu('Choose a model', 3, 0, row_span=6, column_span=1)
        
        self.model_label = self.add_label(self.NO_MODEL_CHOSEN, 0, 1, row_span=1, column_span=2)

        self.action_menu = self.add_scroll_menu('Actions', 1, 2, row_span=2, column_span=1)
        self.create_btn = self.add_button("Add", 3, 2, row_span=1, column_span=1)

        self.search_bar = self.add_text_box("Search (Ctrl+U to clear)", 1, 1, row_span=1, column_span=1)
        self.sort_btn = self.add_button("Sort", 2, 1, row_span=1, column_span=1)
        self.filter_btn = self.add_button("Filter", 3, 1, row_span=1, column_span=1)

        self.model_rows = self.add_checkbox_menu('Rows', 4, 1, row_span=5, column_span=2, checked_char='*')

    def _add_keybindings(self):
        self.app_menu.add_key_command(keys.KEY_ENTER, self.select_app)
        self.model_menu.add_key_command(keys.KEY_ENTER, self.select_model)

        self.model_rows.add_key_command(keys.KEY_ENTER, self.select_model_object)
        self.model_rows.add_key_command(keys.KEY_SPACE, self.toggle_row)
        # remove mouse handler, it's broken
        self.model_rows._handle_mouse_press = lambda *_: None
        
        self.create_btn.command = self.add_instance

        self.search_bar.add_key_command(keys.KEY_ENTER, self.search)
        self.search_bar.add_key_command(keys.KEY_TAB, self.search)
        self.search_bar.add_key_command(keys.KEY_CTRL_U, self.clear_search)
        self.sort_btn.command = self.sort
        self.filter_btn.command = self.filter

    def _populate_apps(self):
        app_labels = sorted(set(model._meta.app_label for model in MODEL_ADMINS.keys()))
        self.app_menu.add_item_list(app_labels)

    def _fill_rows(self):
        if not self.selected_model:
            self.move_focus(self.model_menu)
            return

        if MODEL_ADMINS[self.selected_model].list_select_related:
            objects = self.selected_model.objects.all().select_related(*MODEL_ADMINS[self.selected_model].list_select_related)
        else:
            objects = self.selected_model.objects.all()

        # need a unique string for each row
        self.pk_name = self.selected_model._meta.pk.name
        self.model_rows.set_title(f'[selected] - {self.pk_name} -- {self.selected_model.__name__}')
        self.queryset = objects

        self.update_row_display()

        
    def update_row_display(self, search_text=None):
        self.model_rows.clear()
        search_skipped = False
        if search_text is None and self.search_text:
            search_text = self.search_text
        elif self.search_text is None and search_text:
            self.search_text = search_text

        for obj in self.queryset:
            if search_text and not (search_text.lower() in str(obj.pk).lower() or search_text in str(obj).lower()):
                search_skipped = True
                continue
            self.model_rows.add_item(MenuItem(obj, f'{obj.pk} -- {str(obj)}'))

        if not self.model_rows._view_items and search_skipped:
            self.show_warning_popup('No results', "Search returned no matching rows.")
            self.move_focus(self.search_bar)

    def select_app(self, app=None):
        selected_app_label = self.app_menu.get() if app is None else app
        if self.app_menu.get() != selected_app_label:
            self.app_menu.set_selected_item_index(self.app_menu._view_items.index(selected_app_label))
        self.models = {model.__name__: model for model in MODEL_ADMINS.keys() if model._meta.app_label == selected_app_label} 
        self.model_menu.clear()
        self.model_menu.add_item_list(sorted(self.models.keys()))
        self.move_focus(self.model_menu)

    def select_model(self):
        selected_model_name = self.model_menu.get()
        selected_model = self.models.get(selected_model_name, None)
        if not selected_model:
            self.move_focus(self.app_menu)
            return

        self.selected_model = selected_model
        self.model_label.set_title(selected_model.__name__)
        self._fill_rows()
        self.update_actions_title()
        self.move_focus(self.model_rows)

    def toggle_row(self, skip_update=False):
        # how the library does it
        self.model_rows.toggle_item_checked(self.model_rows.get())
        if not skip_update:
            self.update_actions_title()

    def clear_model_rows(self):
        for item in self.model_rows._selected_item_dict:
            self.model_rows.mark_item_as_not_checked(item)
        
    def update_actions_title(self):
        rows_checked = sum(1 for row_checked in self.model_rows._selected_item_dict.values() if row_checked)
        if self.selected_model:
            self.action_menu.set_title(f'Actions ({rows_checked} of {len(self.model_rows._view_items)} selected)')
        else:
            self.action_menu.set_title(f'Actions')

    def select_model_object(self):
        selected_obj = self.model_rows.get().obj
        self.show_message_popup('woah', str(selected_obj))

        EDIT_FIELD = "Edit field"
        DROP_IN = "Drop in terminal"
        def handle(option):
            def handle(item):
                edit_model.handle_string_field(selected_obj, item.obj, self.pk_name, self)

            if option == EDIT_FIELD:
                # TODO: maybe use _get_fields() since this is terminal
                fields = [MenuItem(field, field.name) for field in selected_obj._meta.get_fields()]
                self.show_menu_popup(EDIT_FIELD, fields, command=handle)

            self.toggle_row(skip_update=False)

        self.show_menu_popup("Edit model", (EDIT_FIELD, DROP_IN), command=handle)
        # # self.clear_model_rows()
        # self.update_row_display()

    @_require_selected_model
    def search(self):
        self.update_row_display(search_text=self.search_bar.get())

    def clear_search(self):
        self.search_bar.set_text('')

    @_require_selected_model
    def sort(self):
        pass 

    @_require_selected_model
    def filter(self):
        self.show_text_box_popup("Search", print)

    @_require_selected_model
    def add_instance(self):
        self.show_form_popup()

tui = Interface()

# class MenuItem