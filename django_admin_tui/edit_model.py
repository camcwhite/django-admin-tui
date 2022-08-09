

# show a text edit popup
def handle_string_field(instance, field, pk_name, interface):
    def try_update(text):
        def update(do_update):
            if not do_update:
                return 

            try:
                setattr(instance, field.name, text)
                instance.save(update_fields=[field.name])
            except Exception as e:
                interface.show_error_popup('There was an error updating the model:', str(e))

        interface.show_yes_no_popup(f'Update "{field.name}" on {str(instance)} ({pk_name}={getattr(instance, pk_name)})?', update)
            
    interface.show_text_box_popup(f"Editing {str(instance)}: {field.name}", command=try_update, text=getattr(instance, field.name,  ""))
