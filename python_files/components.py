import flet as ft

class ConfirmButton(ft.ElevatedButton):
    def __init__(self, text, callback, colors, width=95, expand=False):
        super().__init__()
        self.text = text
        self.color = "white"
        self.width = width
        self.expand = expand
        self.bgcolor = {
            ft.ControlState.DEFAULT: colors.primary,
            ft.ControlState.HOVERED: colors.primary_2
        }
        self.style = ft.ButtonStyle(
            alignment=ft.alignment.center,
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.Padding(6, 14, 6, 16)
        )
        self.on_click = callback



class CancelButton(ft.OutlinedButton):
    def __init__(self, text, callback, colors, width=95, expand=False):
        super().__init__()
        self.content = ft.Text(text, color=colors.primary)
        self.width = width
        self.expand = expand
        self.style = ft.ButtonStyle(
            alignment=ft.alignment.center,
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.Padding(6, 14, 6, 16),
            side=ft.BorderSide(width=1.5, color=colors.primary)
        )
        self.on_click = callback


class NumberStepper(ft.Row):
    def __init__(self, colors, font_sizes, value=0, step=1):
        super().__init__()
        self.value = value
        self.step = step

        self.video_num_field = NumbersOnlyField(font_sizes=font_sizes, colors=colors, value=self.value)

        # Arrow buttons (comfortable size)
        up_button = ft.IconButton(
            icon=ft.Icons.KEYBOARD_ARROW_UP,
            icon_size=14,
            padding=0,
            width=18,
            height=15,
            on_click=self.increment,
            icon_color=colors.primary
        )
        down_button = ft.IconButton(
            icon=ft.Icons.KEYBOARD_ARROW_DOWN,
            icon_size=14,
            padding=0,
            width=18,
            height=15,
            on_click=self.decrement,
            icon_color=colors.primary
        )

        buttons = ft.Column([up_button, down_button], spacing=0, tight=True)

        # Row = field + arrows
        self.controls = [self.video_num_field, buttons]
        self.spacing = 0

    def increment(self, e):
        self.value = int(self.video_num_field.value or 0) + self.step
        self.video_num_field.value = f"{self.value:02}"   # keep 2-digit format
        self.update()

    def decrement(self, e):
        if self.value == 0:
            return
        self.value = int(self.video_num_field.value or 0) - self.step
        self.video_num_field.value = f"{self.value:02}"
        self.update()

class NumbersOnlyField(ft.TextField):
    def __init__(self, font_sizes, colors, value=0, max_value=None):
        super().__init__()
        self.value=f"{value:02}"
        self.max_value = max_value
        self.content_padding=ft.Padding(0, 8, 0, 8)
        self.text_style=ft.TextStyle(weight=ft.FontWeight.W_500, size=font_sizes.medium)
        self.keyboard_type=ft.KeyboardType.NUMBER
        self.input_filter=ft.NumbersOnlyInputFilter()
        self.width = 30
        self.text_align = ft.TextAlign.CENTER
        self.border_color = "transparent"
        self.cursor_color = colors.primary

        self.on_change = self.validate_value

    def validate_value(self, e):
        # To make sure program doesnt crash if invalid input in number field
        try:
            val = int(self.value or 0)
        except ValueError:
            val = 0

        if self.max_value is not None:
            if val > self.max_value:
                val = self.max_value
            elif val < 0:
                val = 0
        
        self.value = f"{val:02}"
        self.update()
        

class PlaylistEntry(ft.Container):
    def __init__(self, name, vid_num, hours, minutes, seconds, colors, font_sizes, parent_list:ft.ListView, page, delete_callback):
        super().__init__()
        self.colors = colors
        self.font_sizes = font_sizes
        self.parent_list = parent_list
        self.page = page
        self.delete_callback = delete_callback

        self.bgcolor = colors.secondary_2
        self.padding = 8
        self.height = 50
        self.border_radius = 12
        self.expand = True        

        self.name_field = ft.TextField(
            value=name,
            content_padding=ft.Padding(0, 8, 0, 8),
            text_style=ft.TextStyle(weight=ft.FontWeight.W_500, size=font_sizes.medium),
            border_color="transparent",
            cursor_color=colors.primary,
            expand=1
        )
        
        self.video_number_stepper = NumberStepper(colors=colors, font_sizes=font_sizes, value=vid_num)

        self.hours_field = NumbersOnlyField(font_sizes=font_sizes, colors=colors, value=hours)
        self.minutes_field = NumbersOnlyField(font_sizes=font_sizes, colors=colors, value=minutes, max_value=59)
        self.seconds_field = NumbersOnlyField(font_sizes=font_sizes, colors=colors, value=seconds, max_value=59)

        self.timestamp_container = ft.Container(
            content=ft.Row([self.hours_field, ft.Text(":", weight=ft.FontWeight.W_500), self.minutes_field, ft.Text(":", weight=ft.FontWeight.W_500), self.seconds_field]),
            expand=1,
        )

        common_button_style = dict(
            icon_color=colors.primary,
            padding=5,
            width=36,
            height=36,
        )

        self.reset_button = ft.IconButton(
            ft.Icons.RESTORE,
            on_click=self.reset_timestamp,
            tooltip="Reset timestamp",
            **common_button_style
        )

        self.delete_button = ft.IconButton(
            ft.Icons.DELETE,
            on_click=self.open_delete_dialog,
            tooltip="Delete playlist",
            **common_button_style
        )

        self.delete_playlist_dialog = ft.AlertDialog(
            title=ft.Text("Confirm delete", weight=ft.FontWeight.W_500),
            content=ft.Text("Are you sure you want to delete this playlist?", size=font_sizes.medium),
            bgcolor=colors.secondary_2,
            actions=[
                CancelButton(text="Cancel", callback=self.close_delete_dialog, colors=colors),
                ConfirmButton(text="Delete", callback=self.delete_playlist, colors=colors)
            ]
        )

        self.content = ft.Row(
            controls=[self.name_field, self.video_number_stepper, self.timestamp_container, self.reset_button, self.delete_button],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
    
    def open_delete_dialog(self, e=None):
        self.page.open(self.delete_playlist_dialog)
        self.page.on_keyboard_event = self.handle_key
        self.page.update()

    def close_delete_dialog(self, e=None):
        self.page.close(self.delete_playlist_dialog)
        self.page.update()

    def delete_playlist(self, e=None):
        self.parent_list.controls.remove(self)
        self.page.close(self.delete_playlist_dialog)
        self.delete_callback()
        self.page.update()

    def reset_timestamp(self, e=None):
        self.hours_field.value = f"{0:02}"
        self.minutes_field.value = f"{0:02}"
        self.seconds_field.value = f"{0:02}"
        self.update()
    
    def handle_key(self, e:ft.KeyboardEvent):
        if e.key == "Enter":
            if self.delete_playlist_dialog.open:
                self.delete_playlist()
        elif e.key == "Escape":
            if self.delete_playlist_dialog.open:
                self.close_delete_dialog()    