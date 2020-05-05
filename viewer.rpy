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
                                    color "000f"
                                    size text_size
                                    value inspector_dsm_location
                                    copypaste True
                            textbutton "Index Images":
                                xoffset 10
                                background Solid("0006")
                                hover_background Solid("0002")
                                text_color "000f"
                                text_size text_size
                                action create_or_update_inspector_dsm

                    frame:
                        background Solid("fff8")
                        xsize 0.5

                        viewport id "filebrowser":
                            background Solid("0002")
                            margin(10, 10)
                            xsize 0.5


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
    inspector_dsm_location = VariableInputValue("inspector_dsm_location_text", default=True, returnable=False)
    inspector_valid_directories = list(dict.fromkeys([os.path.dirname(f) for f in renpy.list_files()]))

    text_size = 22
    title_size = 30


    def create_or_update_inspector_dsm():
        global inspector_dsm
        location_exists = inspector_dsm_location_text in inspector_valid_directories \
                          and len(inspector_dsm_location_text) > 0

        if location_exists:
            inspector_dsm = DynamicSpriteManager(inspector_dsm_location_text)


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