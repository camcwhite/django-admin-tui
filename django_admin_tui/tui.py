from typing import Union

from django.apps import apps
from django.contrib.admin import site as admin_site
from py_cui import PyCUI, keys
from py_cui.widgets import Widget

TUI_DIMENSIONS = (9, 3)
MODEL_ADMINS = admin_site._registry 

def _require_selected_model(mtd):
    def _wrapper(self, *args, **kwargs):
        if not self.selected_model:
            self.move_focus(self.model_menu)
            return
        mtd(self, *args, **kwargs)
    return _wrapper

class ModelRowItem:
    def __init__(self, obj, row_text) -> None:
        self.obj = obj
        self.row_text = row_text

    def __str__(self) -> str:
        return self.row_text

# just a wrapper around py_cui.PyCUI
class Interface(PyCUI):
    NO_MODEL_CHOSEN = '<No model chosen>'

    def __init__(self):
        super().__init__(*TUI_DIMENSIONS)
        self.models = {}
        self.rows = []
        self.selected_model = None
        self.pk_name = None
        self.queryset = None
        self.set_title('Django Admin TUI')
        
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

        self.action_menu = self.add_scroll_menu('Actions', 1, 2, row_span=3, column_span=1)

        self.search_bar = self.add_text_box("Search (Ctrl+U to clear)", 1, 1, row_span=1, column_span=1)
        self.sort_btn = self.add_button("Sort", 2, 1, row_span=1, column_span=1)
        self.filter_btn = self.add_button("Filter", 3, 1, row_span=1, column_span=1)

        self.model_rows = self.add_checkbox_menu('Rows', 4, 1, row_span=5, column_span=2)

    def _add_keybindings(self):
        self.app_menu.add_key_command(keys.KEY_ENTER, self.select_app)
        self.model_menu.add_key_command(keys.KEY_ENTER, self.select_model)
        self.model_rows.add_key_command(keys.KEY_ENTER, self.select_model_object)
        self.model_rows.add_key_command(keys.KEY_SPACE, self.toggle_row)
        # remove mouse handler, it's broken
        self.model_rows._handle_mouse_press = lambda *_: None
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
        for obj in self.queryset:
            if search_text and not (search_text.lower() in str(obj.pk).lower() or search_text in str(obj).lower()):
                search_skipped = True
                continue
            self.model_rows.add_item(ModelRowItem(obj, f'{obj.pk} -- {str(obj)}'))

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

    def toggle_row(self):
        # how the library does it
        self.model_rows.toggle_item_checked(self.model_rows.get())
        self.update_actions_title()
        
    def update_actions_title(self):
        rows_checked = sum(1 for row_checked in self.model_rows._selected_item_dict.values() if row_checked)
        if self.selected_model:
            self.action_menu.set_title(f'Actions ({rows_checked} of {len(self.model_rows._view_items)} selected)')
        else:
            self.action_menu.set_title(f'Actions')

    def select_model_object(self):
        selected_obj = self.model_rows.get().obj

    @_require_selected_model
    def search(self):
        self.update_row_display(search_text=self.search_bar.get())

    def clear_search(self):
        self.search_bar.set_text('')

    @_require_selected_model
    def sort(self):
        self.show_text_box_popup("Search", print)

    @_require_selected_model
    def filter(self):
        self.show_text_box_popup("Search", print)

tui = Interface()

# class MenuItem