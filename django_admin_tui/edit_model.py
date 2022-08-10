from django.db.models.fields import NOT_PROVIDED

from django_admin_tui.helpers import MenuItem, get_model_name


class _NotSet:
    pass

def _get_title_prefix(instance, field):
    return f"Editing {str(instance)}" if instance else f"Create new {get_model_name(field.model)}"

def _get_init_value(instance, field, default=""):
    return getattr(instance, field.name,  default) if instance else str(field.default) if getattr(field, 'default', NOT_PROVIDED) != NOT_PROVIDED else default

def handle_choice_field(field_menu_item, pk_name, interface, instance=None):
    field = field_menu_item.obj
    menu_items = [MenuItem(val, f'{desc} ({str(val)})') for val, desc in field.choices]

    def try_update(choice_item):
        def update(do_update):
            if not do_update:
                return 

            if instance:
                try:
                    setattr(instance, field.name, choice_item.obj)
                    instance.save(update_fields=[field.name])
                except Exception as e:
                    interface.show_error_popup('There was an error updating the model:', str(e))
            else:
                interface.set_new_model_field(field, choice_item.obj, field_menu_item)

        if instance:
            interface.show_yes_no_popup(f'"{field.name}" <= "{choice_item.obj}"?', update)
        else:
            # when creating, don't confirm
            update(True)

    # init_value
    _ = _get_init_value(instance, field, default=_NotSet)

    interface.show_menu_popup(f'{_get_title_prefix(instance, field)}: {field.name} (choices)', menu_items=menu_items, command=try_update)
    
# show a text edit popup
def handle_string_field(field_menu_item, pk_name, interface, instance=None):
    field = field_menu_item.obj
    def try_update(text):
        def update(do_update):
            if not do_update:
                return 

            if instance:
                try:
                    setattr(instance, field.name, text)
                    instance.save(update_fields=[field.name])
                except Exception as e:
                    interface.show_error_popup('There was an error updating the model:', str(e))
            else:
                interface.set_new_model_field(field, text, field_menu_item)

        if instance:
            interface.show_yes_no_popup(f'Update "{field.name}" on {str(instance)} ({pk_name}={getattr(instance, pk_name)})\nto "{text}"?', update)
        else:
            # when creating, don't confirm
            update(True)
            
    title_prefix = _get_title_prefix(instance, field)
    init_text = _get_init_value(instance, field)
    interface.show_text_box_popup(f"{title_prefix}: {field.name}", command=try_update, text=init_text)
