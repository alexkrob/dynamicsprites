screen image_browser:
    $ indent_size = 20
    if not inspector_dsm:
        text "No Images Loaded" color "0006" offset (10, 10) size text_size
    else:
        vbox:
            spacing 10
            for entry in inspector_image_browser_files:
                    hbox:
                        spacing 10
                        xoffset indent_size * entry.level
                        python:
                            if entry.isexpanded:
                                expanded_button_text = "▼"
                            else:
                                expanded_button_text = "►"
                        if entry.isdir:
                            textbutton expanded_button_text:
                                xysize(text_size, text_size)
                                background Solid("fff0")
                                text_size text_size
                                text_color "000f"
                                text_hover_color "0006"
                                action Function(update_expanded_list, entry)
                        else:
                            null width text_size

                        text entry.label color "000f" size text_size

screen sprite_inspector:
    key "K_ESCAPE" action Hide("sprite_inspector")

    zorder 200
    modal True
    frame:
        background Solid("fff8")
        xysize (1.0, 1.0)
        margin (0,0)
        padding (0,0)

        textbutton "x":
            background Solid("fff0")
            xysize (50, 50)
            anchor (1.0, 0.0)
            pos (1.0, 0.0)
            offset (-10, 10)

            action Hide("sprite_inspector")
            text_size 50
            text_color "000f"
            text_hover_color "0006"
            text_anchor (0.5, 0.5)
            text_pos(0.5, 0.5)

        frame id "inner_frame":
            background Solid("fff8")
            xysize (1.0, 1.0)
            margin (60, 60)

            hbox:
                spacing 10
                yfill True

                vbox:
                    spacing 10
                    text "Image Browser" color "000f" size title_size
                    frame:
                        background Solid("fff8")
                        xsize 0.5

                        vbox:
                            xfill True
                            spacing 10
                            text "Image Directory:" color "000f" size text_size
                            window:
                                xoffset 10
                                xpos 0.0
                                xanchor 0.0
                                xsize 0.69
                                ysize text_size + 10
                                padding (5, 5)
                                background Solid("0002")
                                input:
                                    color inspector_dsm_location_text_color
                                    size text_size
                                    copypaste True
                                    changed inspector_dsm_location_text_changed
                            textbutton "Index Images":
                                xoffset 10
                                if inspector_dsm_location_exists:
                                    background Solid("0006")
                                else:
                                    background Solid("0002")
                                hover_background Solid("0002")
                                if inspector_dsm_location_exists:
                                    text_color "000f"
                                else:
                                    text_color "0006"
                                text_size text_size
                                action create_or_update_inspector_dsm
                                sensitive inspector_dsm_location_exists

                    frame:
                        background Solid("fff8")
                        xsize 0.5

                        viewport:
                            xsize 0.5
                            mousewheel True
                            use image_browser

                vbox:
                    spacing 10
                    text "Layers" color "000f" size title_size
                    frame:
                        background Solid("fff8")
                        xysize (0.66, 1.0)

                vbox:
                    spacing 10
                    text "Preview" color "000f" size title_size
                    frame:
                        background Solid("fff8")
                        xysize (1.0, 1.0)


init 1000 python:
    from collections import OrderedDict

    inspector_dsm = None
    inspector_dsm_flattened_files = None
    inspector_dsm_expanded_directories = []
    inspector_dsm_location_text = ""
    inspector_dsm_location_text_color = "000f"
    inspector_dsm_location_exists = False
    inspector_valid_directories = list(dict.fromkeys([os.path.dirname(f) for f in renpy.list_files()]))
    inspector_valid_filetypes = ['.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp']

    text_size = 22
    title_size = 30


    class ListEntry:
        def __init__(self, level, isdir, label, isexpanded):
            self.level = level
            self.isdir = isdir
            self.label = label
            self.isexpanded = isexpanded


    def flatten_dict(d, level=0):
        flattened_list = []

        if isinstance(d, dict):
            for k, v in OrderedDict(sorted(sorted(d.items(), key=lambda k: k[0]),
                                                             key=lambda k: str(type(k[1])), reverse=True)).items():
                if isinstance(v, dict):
                    flattened_list.append(ListEntry(level, True, k, False))
                    flattened_list.extend(flatten_dict(v, level + 1))
                else:
                    if any([ext in v.lower() for ext in inspector_valid_filetypes]):
                        flattened_list.append(ListEntry(level, False, k, False))

        return flattened_list


    def inspector_dsm_location_text_changed(inputtext):
        global inspector_dsm_location_text_color
        global inspector_dsm_location_text
        global inspector_dsm_location_exists

        inspector_dsm_location_text = inputtext

        inspector_dsm_location_exists = inputtext in inspector_valid_directories and len(inputtext) > 0

        if inspector_dsm_location_exists:
            new_color = "000f"
        else:
            new_color = "#d60000"

        if new_color != inspector_dsm_location_text_color:
            inspector_dsm_location_text_color = new_color
            renpy.restart_interaction()


    def create_or_update_inspector_dsm():
        global inspector_dsm
        global inspector_dsm_flattened_files

        if inspector_dsm_location_exists:
            inspector_dsm = DynamicSpriteManager(inspector_dsm_location_text)
            inspector_dsm_flattened_files = flatten_dict(inspector_dsm.image_files)
            update_expanded_list()

        renpy.restart_interaction()


    def update_expanded_list(entry_to_expand=None):
        global inspector_image_browser_files
        global inspector_dsm_flattened_files

        inspector_image_browser_files = []

        if entry_to_expand:
            entry_to_expand.isexpanded = not entry_to_expand.isexpanded

        level_filter = 0

        for ent in inspector_dsm_flattened_files:
            level_filter = ent.level if ent.level < level_filter else level_filter

            if ent.level == level_filter:
                inspector_image_browser_files.append(ent)

            if ent.isexpanded and ent.level == level_filter:
                level_filter = ent.level + 1



    def show_sprite_inspector():
        if not renpy.config.developer:
            return
        renpy.show_screen('sprite_inspector')
        renpy.restart_interaction()

    config.underlay.append(renpy.Keymap(show_sprite_inspector = show_sprite_inspector,))


init 1100 python:
    config.locked = False
    config.keymap["show_sprite_inspector"] = ['S']
    config.locked = True