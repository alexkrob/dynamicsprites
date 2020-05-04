init:
    define colors.marj = "#38a886"
    # Dynamic sprite system initializations
    init python:
        dsm = DynamicSpriteManager('dynamicsprites/images')

        # Marjolaine Emotes
        marj_id = 'mj'

        marj_sprite, mj = dsm.add_sprite(marj_id, 'marj', 'Marjolaine', display_name_color = colors.marj, scale=0.96)
        marj_sprite.add_transform('leftthird', Transform(xanchor=0.5, yanchor=1, xpos=0.30, ypos=0.16))
        marj_sprite.add_transform('center', Transform(xanchor=0.5, yanchor=1, xpos=0.55, ypos=0.16))

        marj_blinks = {}
        marj_blinks['default'] = LayerAnimation(BlinkEyes, 'open/default', 'closed/default')
        marj_blinks['wide'] = LayerAnimation(BlinkEyes, 'open/wide', 'closed/default')
        marj_blinks['wideglance'] = LayerAnimation(BlinkTransition, 'open/wide', 'open/sidelong', 'closed/flat')
        marj_blinks['sideeye'] = LayerAnimation(BlinkEyes, 'open/sidelong', 'closed/default')

        marj_mouths = {}
        marj_mouths['default'] = LayerAnimation(FlapMouth, 'marj/neutral/mouth/closed/default', 'marj/neutral/mouth/open/default', cha=marj_id, dsm=dsm)
        marj_mouths['slant'] = LayerAnimation(FlapMouth, 'marj/neutral/mouth/closed/slant', 'marj/neutral/mouth/open/default', cha=marj_id, dsm=dsm)
        marj_mouths['pursed'] = LayerAnimation(FlapMouth, 'marj/neutral/mouth/closed/pursed', 'marj/neutral/mouth/open/default', cha=marj_id, dsm=dsm)

        marj_sprite.add_emote('relaxed', 'neutral', {
                              'brows': EmoteLayer('default'),
                              'eyes': EmoteLayer(animation=marj_blinks['default']),
                              'mouth': EmoteLayer(animation=marj_mouths['default'])})
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

        # Hat Emotes
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