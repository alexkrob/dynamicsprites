# This file is an abbreviated example of what you'd find in a typical `game/init.rpy` file. It contains the call to the
# subsystem to create the dynamic sprite manager, and an example of how you'd go about building up an expression
# library for one sprite.

init:
    # If a variable is defined in an init block, the dynamic sprite system can use it inside a python block. This is
    # especially useful for values defined in `gui.rpy` or `options.rpy`.
    define colors.marj = "#38a886"

    # By default, text_cps is set to 0 (all text is displayed instantly). To utilize the FlapMouth and Bounce
    # animations, this value must be higher than 0.
    $ preferences.text_cps = 40

    init python:
        # The first step of using the Dynamic Sprite Manager is to initialize it as a python object. Here, we've
        # abbreviated it as `dsm`, and will be using that name to call it throughout the project. However, we could
        # easily name it something else, as it's just a variable name. The argument to `DynamicSpriteManager` should be
        # the location of all the sprites in your project that you wish to have access to via the DSM.
        dsm = DynamicSpriteManager('dynamicsprites/images')
        # Typically you won't need more than one DSM per project. While it is possible to create any number of DSMs, all
        # referenced by different variable names, this will likely get confusing and lead to weird bugs.

        # In order to create a new sprite, we need to call the `add_sprite` method of the DSM. For more information on
        # what the arguments of this particular method need to be, see line 75 of `dynamicsprites.rpy`.
        marj_id = 'mj'
        marj_sprite, mj = dsm.add_sprite(marj_id, 'marj', 'Marjolaine', display_name_color = colors.marj)

        # The following steps can be done in any order.

        # Add default transforms for a sprite by naming them, and then defining a transform via keyword arguments.
        # See `example_script.rpy` for how to use them in a scripting setting.
        marj_sprite.add_transform('leftthird', Transform(xanchor=0.5, yanchor=1, xpos=0.30, ypos=0.16))
        marj_sprite.add_transform('center', Transform(xanchor=0.5, yanchor=1, xpos=0.55, ypos=0.16))

        # The Dynamic Sprite Manager allows you to add any number of layers to a sprite. Each layer is of type
        # `EmoteLayer`, and can contain either a string or a LayerAnimation.

        # For ease of use, it's wise to pre-define lengthy LayerAnimation statements that can be re-used by multiple
        # emotes. LayerAnimations take a ren'py Animation Transform as the first argument, and all the keyframes of
        # that animation as subsequent arguments. For example, `BlinkEyes` (`animation.rpy`, line 93) takes two
        # keyframes (an "eyes open" frame, and an "eyes closed" frame).
        marj_blinks = {}
        marj_blinks['default'] = LayerAnimation(BlinkEyes, 'open/default', 'closed/default')
        marj_blinks['wide'] = LayerAnimation(BlinkEyes, 'open/wide', 'closed/default')
        marj_blinks['wideglance'] = LayerAnimation(BlinkTransition, 'open/wide', 'open/sidelong', 'closed/flat')
        marj_blinks['sideeye'] = LayerAnimation(BlinkEyes, 'open/sidelong', 'closed/default')

        # More than just animation keyframes can be passed to LayerAnimations, however. `FlapMouth` (`animation.rpy`,
        # line 88) takes 4 arguments, and only two of them are keyframes that need evaluated by the DSM. As long as the
        # additional arguments are passed as keyword arguments, they'll be passed through to `FlapMouth`.
        marj_mouths = {}
        marj_mouths['default'] = LayerAnimation(FlapMouth, 'marj/neutral/mouth/closed/default', 'marj/neutral/mouth/open/default', cha=marj_id, dsm=dsm)
        marj_mouths['slant'] = LayerAnimation(FlapMouth, 'marj/neutral/mouth/closed/slant', 'marj/neutral/mouth/open/default', cha=marj_id, dsm=dsm)
        marj_mouths['pursed'] = LayerAnimation(FlapMouth, 'marj/neutral/mouth/closed/pursed', 'marj/neutral/mouth/open/default', cha=marj_id, dsm=dsm)

        # If a string argument is passed to an `EmoteLayer`, the DSM will perform a relative search in the corresponding
        # folder in the project directory. For example, in the following call to `add_emote`, an EmoteLayer('default')
        # is assigned to 'brows'. Because the base sprite is 'neutral', the DSM will look for an image at the following
        # location: "marj/neutral/brows/default.png" and set it to this layer of the sprite.
        marj_sprite.add_emote('relaxed', 'neutral', {
                              'brows': EmoteLayer('default'),

        # Here, you can see the dictionary we defined above becoming useful.
                              'eyes': EmoteLayer(animation=marj_blinks['default']),

        # However, take a look at the definition for `marj_mouths['default']` above (line 48). As you can see, keyframe
        # arguments are expanded out, and are no longer relative to the base sprite, but are absolute. This allows you
        # to re-use images that may not need any changes for use with different base sprites. For example, Marjolaine's
        # mouth doesn't need changed if her base sprite is swapped to `hat`, but her eyes and brows do. By making the
        # path to the desired mouth keyframes explicit, we override the DSM's local search, and re-use images for layers
        # without having to copy/paste them into a different folder.
                              'mouth': EmoteLayer(animation=marj_mouths['default'])})

        # Here we add several more emotes for Marjolaine. These all can be accessed in ren'py script by using the `show`
        # statement. For example, `show mj apologetic`.
        marj_sprite.add_emote('apologetic', 'neutral', {
                              'brows': EmoteLayer('concerned'),
                              'eyes': EmoteLayer(animation=marj_blinks['wideglance']),
                              'mouth': EmoteLayer(animation=marj_mouths['slant'])})
        marj_sprite.add_emote('daydreaming', 'neutral', {
                              'brows': EmoteLayer('hopeful'),
                              'eyes': EmoteLayer('closed/default'),
                              'mouth': EmoteLayer('open/drool')})
        marj_sprite.add_emote('determined', 'neutral', {
                              'brows': EmoteLayer('default'),
                              'eyes': EmoteLayer('closed/default'),
                              'mouth': EmoteLayer(animation=marj_mouths['default'])})
        marj_sprite.add_emote('plotting', 'neutral', {
                              'brows': EmoteLayer('raised'),
                              'eyes': EmoteLayer(animation=marj_blinks['sideeye']),
                              'mouth': EmoteLayer(animation=marj_mouths['default'])})

        # Here, we switch to a different base sprite (a version of Marjolaine with a hat on). Since we were smart about
        # how we defined our relative/absolute LayerAnimation keyframes, we can use the same LayerAnimations for both
        # versions of the sprite.
        marj_sprite.add_emote('hat relaxed', 'hat', {
                              'brows': EmoteLayer('default'),
                              'eyes': EmoteLayer(animation=marj_blinks['default']),
                              'mouth': EmoteLayer(animation=marj_mouths['default'])})
        marj_sprite.add_emote('hat pouty', 'hat', {
                              'brows': EmoteLayer('unsure'),
                              'eyes': EmoteLayer(animation=marj_blinks['wide']),
                              'mouth': EmoteLayer(animation=marj_mouths['pursed'])})
        marj_sprite.add_emote('hat exasperated', 'hat', {
                              'brows': EmoteLayer('furrowed'),
                              'eyes': EmoteLayer('closed/flat'),
                              'mouth': EmoteLayer(animation=marj_mouths['pursed'])})
        marj_sprite.add_emote('hat happy', 'hat', {
                              'brows': EmoteLayer('default'),
                              'eyes': EmoteLayer('closed/default'),
                              'mouth': EmoteLayer(animation=marj_mouths['default'])})

        # When all your sprites and emotes have been added, the final call to `compile_sprites()` will dynamically
        # gather all your Dynamic Sprites and make them available for use in scripting. Because the sprites are compiled
        # at runtime, our RAM usage is way more efficient than if we tried to specify every single combination of every
        # layer available. Call this last.
        dsm.compile_sprites()
