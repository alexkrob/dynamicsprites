screen image_browser:
    if not inspector_dsm:
        text "No Images Loaded" color "0006" offset (10, 10) size text_size
    else:
        text "Images loaded!" color "000f" offset (10, 10) size text_size

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
    inspector_dsm = None
    inspector_dsm_location_text = ""
    inspector_dsm_location_text_color = "000f"
    inspector_dsm_location_exists = False
    inspector_valid_directories = list(dict.fromkeys([os.path.dirname(f) for f in renpy.list_files()]))

    text_size = 22
    title_size = 30


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

        if inspector_dsm_location_exists:
            inspector_dsm = DynamicSpriteManager(inspector_dsm_location_text)

        renpy.restart_interaction()


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