import flet as ft
from types import SimpleNamespace
import os
import sys
import json
from components import PlaylistEntry, CancelButton, ConfirmButton

def main(page: ft.Page):
    def load_playlists():
        if os.path.exists(PLAYLISTS_FILE):
            with open(PLAYLISTS_FILE, 'r') as f:
                try:
                    playlists = json.load(f)
                    for playlist in playlists:
                        add_playlist_to_ui(
                            name=playlist["name"],
                            vid_num=playlist["vid_num"],
                            hours=playlist["hours"],
                            minutes=playlist["minutes"],
                            seconds=playlist["seconds"]
                        )
                    page.update()
                except:
                    pass

    def save_playlists():
        data = []
        for playlist in playlists_list.controls:
            entry = {
                "name": playlist.name_field.value,
                "vid_num": int(playlist.video_number_stepper.video_num_field.value),
                "hours": int(playlist.hours_field.value),
                "minutes": int(playlist.minutes_field.value),
                "seconds": int(playlist.seconds_field.value)
            }
            data.append(entry)
        try:
            with open(PLAYLISTS_FILE, "w") as f:
                json.dump(data, f, indent=4)
        except:
            pass

    def handle_key(e: ft.KeyboardEvent):
        if e.key == "Escape":
            if add_playlist_dialog.open:
                close_playlist_dialog()

    def open_playlist_dialog(e=None):
        page.open(add_playlist_dialog)
        page.update()

    def close_playlist_dialog(e=None):
        page.close(add_playlist_dialog)
        add_playlist_field.value = ""
        add_playlist_field.error_text = None
        page.update()

    def add_playlist(e):
        playlist_name = add_playlist_field.value
        if not playlist_name.strip():
            add_playlist_field.error_text = "Cannot be empty"
            page.update()
            return
        add_playlist_to_ui(playlist_name)
        save_playlists()
        close_playlist_dialog()

    def add_playlist_to_ui(name, vid_num=0, hours=0, minutes=0, seconds=0):
        playlist_container = PlaylistEntry(name, vid_num, hours, minutes, seconds, colors, font_sizes, playlists_list, page, delete_callback=save_playlists)
        playlists_list.controls.append(playlist_container)

    def open_resize_dialog(e):
        page.open(resize_dialog)
        page.update()

    def close_resize_dialog(e=None):
        page.close(resize_dialog)
        width_field.value = ""
        width_field.error_text = None
        height_field.value = ""
        height_field.error_text = None
        page.update()

    def get_current_size(e):
        width_field.value = int(page.window.width)
        height_field.value = int(page.window.height)
        page.update()

    def get_default_size(e):
        width_field.value = default_width
        height_field.value = default_height
        page.update()
    
    def get_dimensions():
        width = None
        height = None
        if os.path.exists(DIMENSIONS_FILE):
            try:
                with open(DIMENSIONS_FILE, 'r') as f:
                    dimensions = json.load(f)
                    width = dimensions['width']
                    height = dimensions['height']
            except:
                pass
        if not width or not height:
            return default_width, default_height
        else:
            return width, height
        
    def save_dimensions(e):
        error = False
        if not str(width_field.value).strip():
            width_field.error_text = " "
            error = True
        if not str(height_field.value).strip():
            height_field.error_text = " "
            error = True
        if error:
            page.update()
            return

        try:
            with open(DIMENSIONS_FILE, 'w') as f:
                dimensions = {"width": width_field.value, "height": height_field.value}
                json.dump(dimensions, f, indent=4)
        except Exception:
            pass
        page.window.width = width_field.value
        page.window.height = height_field.value
        page.window.center()
        close_resize_dialog()

    def handle_window_close(e):
        if e.data == "close":
            page.window.visible = False
            save_playlists()
            page.window.destroy()

    # Making sure data directory exists
    if getattr(sys, 'frozen', False):
        BASE_DIR = os.path.dirname(sys.executable)
    else:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    DATA_DIR = os.path.join(BASE_DIR, "data")
    os.makedirs(DATA_DIR, exist_ok=True)

    PLAYLISTS_FILE = os.path.join(DATA_DIR, "playlists.json")
    DIMENSIONS_FILE = os.path.join(DATA_DIR, "dimensions.json")

    # colors and text
    colors = SimpleNamespace(
        primary="#00ae77",
        primary_2="#01bd82",
        secondary="#16181a",
        secondary_2="#1f2123",
        secondary_3="#26292B"
    )

    font_sizes = SimpleNamespace(
        large=20,
        medium=15
    )

    default_width = 585
    default_height = 565

    # page settings
    page.title = "NextUp"
    page.window.width, page.window.height = get_dimensions()
    page.window.center()
    page.bgcolor = colors.secondary
    page.on_keyboard_event = handle_key
    page.window.prevent_close = True
    page.window.on_event = handle_window_close

    # Main setup
    
    heading = ft.Text("All Playlists", size=font_sizes.large, weight=ft.FontWeight.W_600)

    resize_button = ft.IconButton(icon=ft.Icons.LAPTOP_WINDOWS, icon_color=colors.primary, tooltip="Resize window", on_click=open_resize_dialog)
    width_field = ft.TextField(
        hint_text="Width",
        autofocus=True,
        bgcolor=colors.secondary_3,
        border_color="transparent",
        cursor_color=colors.primary,
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=ft.NumbersOnlyInputFilter()
    )
    height_field = ft.TextField(
        hint_text="Height",
        autofocus=True,
        bgcolor=colors.secondary_3,
        border_color="transparent",
        cursor_color=colors.primary,
        keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=ft.NumbersOnlyInputFilter()
    )
    resize_dialog_fields = ft.Row([ft.Container(width_field, expand=True), ft.Container(height_field, expand=True)])
    use_current_button = ft.Container(
        content=ft.TextButton(
            "Use current",
            style=ft.ButtonStyle(color="#aaaaaa", text_style=ft.TextStyle(size=12), padding=ft.Padding(2, 0, 2, 0), overlay_color="transparent"),
            on_click=get_current_size,
        ),
        height=22
    )
    reset_to_default_button = ft.Container(
        content=ft.TextButton(
            "Reset to default",
            style=ft.ButtonStyle(color="#aaaaaa", text_style=ft.TextStyle(size=12), padding=ft.Padding(2, 0, 2, 0), overlay_color="transparent"),
            on_click=get_default_size,
        ),
        height=22
    )
    resize_dialog_column = ft.Column(
        [resize_dialog_fields, use_current_button, reset_to_default_button],
        spacing=0,
        tight=True
    )
    resize_dialog = ft.AlertDialog(
        title=ft.Text("Resize Window", weight=ft.FontWeight.W_500),
        bgcolor=colors.secondary_2,
        
        content=resize_dialog_column,
        actions=[
        ft.Row(
            [
                CancelButton(text="Cancel", callback=close_resize_dialog, colors=colors, expand=True, width=None),
                ConfirmButton(text="Save", callback=save_dimensions, colors=colors, expand=True, width=None)
            ],
            spacing=10,
        )]
    )

    add_playlist_field = ft.TextField(
        hint_text="Playlist name",
        autofocus=True,
        bgcolor=colors.secondary_3,
        border_color="transparent",
        cursor_color=colors.primary,
        on_submit=add_playlist
    )
    add_playlist_dialog = ft.AlertDialog(
        title=ft.Text("Add new playlist", weight=ft.FontWeight.W_500),
        content=add_playlist_field,
        bgcolor=colors.secondary_2,
        # Putting buttons inside a row so they're able to expand
        actions=[
            ft.Row(
                controls=[
                    CancelButton(text="Cancel", callback=close_playlist_dialog, colors=colors, expand=True, width=None, ),
                    ConfirmButton(text="Add", callback=add_playlist, colors=colors, expand=True, width=None)
                ],
                spacing=10
            )
        ]
    )
    add_button = ft.IconButton(icon=ft.Icons.ADD, icon_color=colors.primary, tooltip="Add playlist" ,on_click=open_playlist_dialog)

    top_row = ft.Row(
        controls=[resize_button, heading, add_button],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    top_container = ft.Container(
        content=top_row
    )

    playlists_list = ft.ListView(
        expand=True,
        spacing=10
    )

    layout = ft.Column(
        [top_container, playlists_list],
        spacing=15,
        expand=True
    )

    page.add(layout)

    load_playlists()

ft.app(target=main)