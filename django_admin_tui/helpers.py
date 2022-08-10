class MenuItem:
    def __init__(self, obj, row_text) -> None:
        self.obj = obj
        self.row_text = row_text

    def __str__(self) -> str:
        return self.row_text

class FieldMenuItem(MenuItem):
    def __init__(self, obj, row_text, init_value) -> None:
        super().__init__(obj, row_text)
        self.init_value = init_value

def get_model_name(model_class):
    return model_class._meta.object_name
