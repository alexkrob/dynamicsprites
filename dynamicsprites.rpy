init python:
    config.reject_backslash = False

    class ImageNotFoundException(Exception):
        def __init__(self, expected_location):
            Exception.__init__(self, 'Image was expected at {0}, but was not found.'.format(expected_location))

    class DynamicSpriteManager:
        """DynamicSpriteManager is a high-level system for easily defining and compiling the ren'py native LayeredImage.

        DynamicSpriteManager is the top-level entity in the dynamic sprite system. Given a directory of images, it will
        automatically scan and categorize those images for use in a mix-and-match style sprite declaration language. It
        expects files to be laid out roughly in the following format:

        <Sprite Name>
        |
        -- <Pose Name>
          |
          -- base.png (sprite base, this will be placed on the bottommost layer unless specified otherwise)
            |
            -- <Layer Name> (a layer can be named anything, but is usually something like "eyes" or "mouth")
              |
              -- Art for this particular layer, categorized and/or named however you like

        As long as this rough format is followed, the DSM will categorize and reference the images properly.

        To start using the DSM, initialize it in a python block using:
        >>> dsm = DynamicSpriteManager(['path/to/your/sprite/folder/here'])

        To create a new sprite:
        >>> my_sprite = dsm.add_sprite([character_name], [name_of_character_images_folder])
        character_name should be the name you've assigned to the ren'py Character "image" argument.

        To add an emote to your new sprite:
        >>> my_sprite.add_emote([emote_name], [name_of_pose], [emote_layer_1], [emote_layer_2], ..., [last_emote_layer])
        add_emote supports infinitely many emote layers, as long as they're named differently. Emote layers can be
        either static images or animations. For more information, see EmoteLayer.

        At the end of your python block, once you've finished adding all your emotes and sprites to the DSM:
        >>> dsm.compile_sprites()

        Sprites are compiled statically after they've all been defined, so the system doesn't index image files that
        aren't used in the script, which keeps RAM usage low.

        Attributes:
            sprites                         (Dict[str, DynamicSprite]): A dictionary of sprites this DSM keeps track of,
                                                                        keyed by the sprite name.
            image_files (Dict[str, Union[Dict[str, Union[...]], str]]): A recursive dictionary of images in the
                                                                        specified directory.
            speaking_characters                            (List[str]): A list of character names that have active
                                                                        dialogue. This can be accessed via callbacks
                                                                        to control animation when a character has
                                                                        text scrolling or voice playing.
            bounce_on_speak                                (List[str]): A list of character names containing all
                                                                        characters that should animate a little bounce
                                                                        when they start a new line of dialogue.
        """
        def __init__(self, image_directory):
            """
            Args:
                image_directory (Union[bytes, str]): The filepath, relative to ren'py's game/ directory, in which to
                                                     locate sprite images.
            """
            self.sprites = {}
            self.image_files = {}
            self.speaking_characters = []
            self.bounce_on_speak = []
            for image_file in [f for f in renpy.list_files() if image_directory in f]:
                # Index the whole directory, but don't create renpy images for everything, as we may not use it all
                dict_path = os.path.relpath(os.path.normpath(image_file), image_directory).split(os.sep)[:-1]
                filename = os.path.relpath(os.path.normpath(image_file), image_directory).split(os.sep)[-1]
                img_dict = add_recursive_dict(self.image_files, dict_path)
                img_dict[os.path.splitext(filename)[0]] = image_file

        def add_sprite(self, character_tag, character_sprite_directory_name, display_name,
                       layer_order=None, scale=1, offsets=(0, 0), display_name_color=gui.text_color,
                       display_dialogue_color=gui.text_color, **kwargs):
            """Adds a sprite to the DSM's manifest.

            Args:
                character_tag                   (str): The character tag used in ren'py scripts to indicate this
                                                       character is speaking.
                character_sprite_directory_name (str): The top-level directory containing all of this sprite's images.
                scale                         (float): The scale factor to apply to all emotes belonging to this sprite.
                offsets             (Tuple[int, int]): The x and y offsets, in pixels, to apply to all emotes belonging
                                                       to this sprite.
            """
            self.sprites[character_tag] = DynamicSprite(character_sprite_directory_name, layer_order, scale, offsets)
            self.enable_bounce(character_tag)
            return self.sprites[character_tag], Character(display_name, callback=speaker(character_tag, self),
                                                          who_color=display_name_color, image=character_tag,
                                                          what_color=display_dialogue_color, **kwargs)

        def enable_bounce(self, character_tag):
            """Enables the bounce on speak animation per-character.

            This method should be used instead of accessing the list directly, as it ensures no duplicates are
            created.
            """
            if character_tag not in self.bounce_on_speak:
                self.bounce_on_speak.append(character_tag)

        def disable_bounce(self, character_tag):
            if character_tag in self.bounce_on_speak:
                self.bounce_on_speak.remove(character_tag)

        def __getattr__(self, character_tag):
            """Allows the user to access sprite and emote attributes in ren'py script, courtesy of attributes.

            If, for example, you had a sprite named "aa" and the xoffset for the "shrug" emote was different than the
            xoffset for the "handsonhips" emote, you could access both attributes in native ren'py script without
            invoking python, like so:

            >>> dsm.aa.shrug.offsets.x
            >>> dsm.aa.handsonhips.offsets.x

            These will work in place of any other variable inside ren'py script.
            """
            return self.sprites[character_tag]

        def compile_sprites(self):
            """Compiles and assembles LayeredImage entities for use by the ren'py engine.

            Call this function after you've defined all your sprites and emotes, as it will load them dynamically into
            the ren'py engine for use in scripting.
            """
            for sprite_name in self.sprites.keys():
                emotes = self.sprites[sprite_name].emotes
                for emote_name in emotes.keys():
                    zoom = 1
                    emote = emotes[emote_name]
                    layer_attributes = []
                    # Do all the layers in emote.layer_order first, then pick up any stragglers.
                    for layer in emote.layer_order + [k for k in emote.layers.keys() if k not in emote.layer_order]:
                        if layer == '_base_':
                            if 'base' in self.image_files[self.sprites[sprite_name].dir_name][emote.pose]:
                                img = self.image_files[self.sprites[sprite_name].dir_name][emote.pose]['base']
                            else:
                                # Realistically if there's only one image in the pose directory, let's not complain and
                                # just assume it's the base image.
                                potential_images = [f for f in self.image_files[sprite_name][emote.pose].values() \
                                                    if type(f) != dict]
                                if len(potential_images) == 1:
                                    img = potential_images[0]
                                else:
                                    # However, if there's more than one, that's a no-no because we have no idea which
                                    # image to use as the base.
                                    raise ImageNotFoundException('/'.join([sprite_name, emote.pose, 'base']))
                            # Scale the base image to ensure that at its native size it'll at least fit on the screen.
                            base_image = Image(img)
                            base_image_size = renpy.image_size(base_image)
                            if base_image_size[1] > config.screen_height:
                                zoom = float(config.screen_height) / base_image_size[1]
                            layer_attributes.append(Attribute(sprite_name + '_base', emote.pose, img, True))
                        else:
                            if layer not in emote.layers:
                                # This continue is triggered when we have a default layer that isn't defined in the
                                # emote layers. This is fine for sprites that maybe don't have all their parts on
                                # different layers, or don't have eyes, etc.
                                continue
                            layer_img = emote.layers[layer].layer_image_name
                            layer_ani = emote.layers[layer].animation
                            if layer_img != '':
                                # Layer is a static image, just grab it from the image dictionary and slap it in there.
                                img, layer_name = self.get_image([self.sprites[sprite_name].dir_name,
                                                                  emote.pose, layer], layer_img)
                                layer_attributes.append(Attribute(sprite_name + '_' + layer,
                                                                  emote.pose, img, layer_name == 'default'))
                            elif layer_ani is not None:
                                # Layer is an animation, so we have to do some work in order to get it ready.
                                imgs = []
                                # We want the image name to be unique amongst animations, so we'll rely on using
                                # every variable that makes an animation unique in the name. It's not like the user
                                # will ever have to reference this animation anyhow, and if they do, we can expose it
                                # in the DSM easier than making them remember a complicated name.
                                img_name = sprite_name + '_' + emote.pose + '_' + layer + '_'
                                # Get and append all the animation states, which will be passed as arguments to the
                                # Transform.
                                for animation_state in layer_ani.states:
                                    img, layer_name = self.get_image([self.sprites[sprite_name].dir_name,
                                                                      emote.pose, layer], animation_state)
                                    imgs.append(img)
                                    img_name += animation_state + '_'

                                img_name += 'animation'
                                # Passing any additional arguments that aren't animation states to the Transform must
                                # be done as keyword arguments, because python 2.7 doesn't support using defaults after
                                # unpacking lists. Any Transforms used by the DSM need to have any additional args
                                # referenced by keyword, for this reason.
                                img = renpy.image(img_name, layer_ani.transform(*(imgs), **(layer_ani.args)))
                                layer_attributes.append(Attribute(sprite_name + '_' + layer,
                                                                  emote.pose,
                                                                  img_name,
                                                                  layer_ani.states[0].split('/')[-1] == 'default'))

                    # Since overall zoom doesn't matter if the image is flipped, we can bake it into the final dynamic
                    # sprite. Offsets, however, have to be on a case-by-case basis, in case sprites are flipped around.
                    composite = LayeredImage(layer_attributes,
                                             at=Transform(zoom=zoom * self.sprites[sprite_name].scale * emote.scale))
                    emote.imgref = renpy.image(sprite_name + ' ' + emote_name, composite)

        def get_image(self, layers_hint, image_name):
            """Gets an image from the sprite image directory based on a layer hint and the name of the image.

            Args:
                layers_hint (List[str]): A list of layers to use as a hint for determining what file image_name is
                                         referring to.
                image_name        (str): The name of an image, represented as a file path from the current layer,
                                         usually something like 'open/smiling' if the layer were for a mouth.

            Returns:
                (str): The system filepath if the image to be consumed by the ren'py image system.
                (str): The final layer on which this image exists. Important for keeping unique names in the ren'py
                       image system.
            """
            img = self.image_files
            layers_from_name = image_name.split('/')
            i = 0
            while i < len(layers_from_name) and layers_from_name[i] not in layers_hint:
                i += 1

            if i == len(layers_from_name):
                finalized_layers = layers_hint + layers_from_name
            else:
                finalized_layers = layers_hint[:layers_hint.index(layers_from_name[i])] + layers_from_name[i:]

            for layer in finalized_layers:
                if layer in img:
                    img = img[layer]
                    lyr = layer
                else:
                    raise ImageNotFoundException('/'.join(finalized_layers))

            return img, lyr


    class DynamicSprite:
        """Represents a Sprite entity in the DSM. This is 1:1 akin to a ren'py Character entity.

        Realistically this class should probably never been initialized on its own. Instead, use the add_sprite method
        in the DynamicSpriteManager class.

        Attributes:
            dir_name            (str): The top-level directory containing all of this sprite's images.
            emotes (Dict[str, Emote]): All the emotes, keyed by their names, belonging to this sprite.
            scale             (float): The scale factor to apply to all emotes belonging to this sprite.
            offsets (Tuple[int, int]): The x and y offsets, in pixels, to apply to all emotes belonging to this sprite.
        """
        def __init__(self, character_sprite_directory_name, layer_order=None, scale=1, offsets=(0, 0)):
            self.dir_name = character_sprite_directory_name
            self.layer_order = layer_order
            self.emotes = {}
            self.transforms = SpriteTransforms()
            self.scale = scale
            self.offsets = SpriteOffset(*offsets)

        def __getattr__(self, emote_name):
            """Works in tandem with the DSM to give the user access to sprite and emote attributes in ren'py script.

            See the DynamicSpriteManager.__getattr__ documentation for more information on how this works.
            """
            return self.emotes[emote_name]

        def add_emote(self, emote_name, pose, layers, layer_order=None, scale=1, offsets=(0, 0)):
            """Adds an emote to this DynamicSprite.

            Args:
                emote_name               (str): The name of the emote to be used in ren'py script.
                pose                     (str): The name of the base pose folder in the images directory to use.
                layers (Dict[str, EmoteLayer]): A dictionary of EmoteLayers, with the layer names as keys. These layers
                                                should correspond 1:1 with directories inside the base pose folder.
                layer_order        (List[str]): The order in which layers should be assembled, bottom-to-top. Entries in
                                                this list should be the same as the keys in layers. Can be
                                                left blank, will default to [_base_, 'mouth', 'eyes', 'brows', 'extra'].
                scale                  (float): The scale of this emote, which will be multiplied by the total scale for
                                                the entire sprite.
                offsets      (Tuple[int, int]): The offsets of this emote, which will be added to the total offsets for
                                                the entire sprite.
            """
            if layer_order is None:
                layer_order = self.layer_order

            self.emotes[emote_name] = Emote(pose, layers, layer_order, scale,
                                            [self.offsets.x + offsets[0], self.offsets.y + offsets[1]])
            return self.emotes[emote_name]

        def add_transform(self, transform_name, transform):
            self.transforms.transforms[transform_name] = transform


    class Emote:
        """Defines one base pose and x number of images/animations layered onto it. 1:1 with a ren'py LayeredImage.

        Realistically this class should probably never been initialized on its own. Instead, use the add_emote method
        in the DynamicSprite class.

        Attributes:
            pose                     (str): The name of the base pose folder in the images directory to use.
            layers (Dict[str, EmoteLayer]): A dictionary of EmoteLayers, with the layer names as keys. These layers
                                            should correspond 1:1 with directories inside the base pose folder.
            layer_order        (List[str]): The order in which layers should be assembled, bottom-to-top. Entries in
                                            this list should be the same as the keys in layers. Can be
                                            left blank, will default to [_base_, 'mouth', 'eyes', 'brows', 'extra'].
            scale                  (float): The scale of this emote, which will be multiplied by the total scale for
                                            the entire sprite.
            offsets      (Tuple[int, int]): The offsets of this emote, which will be added to the total offsets for
                                            the entire sprite.
            imgref           (renpy.Image): The renpy.Image object this Emote was built into. Is None until the DSM
                                            runs compile_sprites().
        """
        def __init__(self, pose, layers, layer_order=None, scale=1, offsets=(0, 0)):
            if layer_order is None:
                layer_order = ['_base_', 'mouth', 'eyes', 'brows', 'extra']
            self.pose = pose
            self.layers = layers
            self.layer_order = layer_order
            self.scale = scale
            self.offsets = SpriteOffset(*offsets)
            self.imgref = None


    class EmoteLayer:
        """Represents one layer of an Emote. Could be a base image, a layer image, or a layer animation.

        To populate an EmoteLayer, you'll need to use images inside the sprite folder. Typically, an EmoteLayer is
        populated by an image from the [sprite]/[pose]/[layer] folder. However, the DSM is flexible. Say you had an
        image in [sprite]/[pose]/mouth/closed/image.png you wanted to use. Simply use 'closed/image' as the layer
        image name, and the DSM will know that's the image you want to use.if

        Similarly, if you wanted to use an image from another layer (or even a base pose), that's allowed too! Using
        'otherpose/mouth/closed/image' will tell the DSM you want to use /mouth/closed/image.png from another pose for
        this layer only.

        Attributes:
            layer_image_name     (str): The name of a static image to use on this layer.
            animation (LayerAnimation): An animation to run on this layer instead of a static image. Only used if
                                        layer_image_name == ''.
        """
        def __init__(self, layer_image_name='', animation=None):
            self.layer_image_name = layer_image_name
            self.animation = animation


    class LayerAnimation:
        """Holds a reference to a ren'py Transform, all of its animation states, and any additional args to pass to it.

        These are usually defined case-by-case, depending on the Transform. Experimentation is key here. Some examples
        are defined above/below, but the sky is the limit, honestly.

        Attributes:
            transform (Transform): The ren'py Transform to apply on this layer.
            states    (List[str]): A list of images to use as animation states in the Transform.
            args (Dict[str, Any]): Any additional keyword arguments to supply to the Transform.
        """
        def __init__(self, transform, *anim_states, **anim_args):
            self.transform = transform
            self.args = anim_args
            self.states = anim_states


    class SpriteOffset:
        """Defines an offset, in pixels, for a sprite, in both horizontal and vertical directions.

        Attributes:
            x (int): The x offset to apply. Positive is right.
            y (int): The y offset to apply. Positive is up.
        """
        def __init__(self, x, y):
            self.x = x
            self.y = y

    class SpriteTransforms:
        def __init__(self):
            self.transforms = {}

        def __getattr__(self, attr):
            return self.transforms[attr]


    def add_recursive_dict(d, keys):
        """Takes a dictionary that already exists, d, and adds key-value pairs recursively for each key in keys.

        Returns:
            (Dict[Any, Any]): An empty dict, nested properly in a much larger dictionary of dictionaries.
        """
        key = keys[0]
        if key not in d:
            d[key] = {}

        if len(keys) > 1:
            return add_recursive_dict(d[key], keys[1:])
        else:
            return d[key]