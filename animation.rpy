init:
    transform blinkeyes(eyes_default, eyes_blink):
        eyes_default
        choice:
            3.5
        choice:
            2.5
        choice:
            1.5
        eyes_blink
        .15
        repeat

    transform blinktransition(eyes_default, eyes_alt, eyes_closed):
        block:
            choice:
                eyes_default
            choice:
                eyes_alt

        block:
            choice:
                3.5
            choice:
                2.5
            choice:
                1.5

        eyes_closed
        .15
        repeat

    transform flapmouth(mouth_default, mouth_speaking):
        mouth_default
        .2
        mouth_speaking
        .2
        repeat

    transform bounce:
        easein 0.125 yoffset -20
        easeout 0.125 yoffset 0

    transform alertblink(layer):
        layer
        alpha 1
        .5
        xoffset -25 yoffset -25
        .5
        alpha 0
        .5
        xoffset 0 yoffset 0
        repeat


init python:
    from datetime import datetime
    def set_speaking(name, dsm, event, **kwargs):
        if event == 'begin':
            if name in dsm.bounce_on_speak:
                renpy.show(name, at_list=[bounce])
        elif event == 'show':
            print(str(datetime.utcnow()) + ': Speech beginning, name: ' + name)
            dsm.speaking_characters.append(name)
        elif event == 'slow_done' or event == 'end':
            print(str(datetime.utcnow()) + ': Speech ending, name: ' + name)
            if name in dsm.speaking_characters:
                dsm.speaking_characters.remove(name)


    speaker = renpy.curry(set_speaking)


    def is_speaking(name, dsm, speaking_mouth, default_mouth, st, at):
        if name in dsm.speaking_characters:
            return speaking_mouth, .1
        else:
            return default_mouth, None


    while_speaking = renpy.curry(is_speaking)


    def SpeakingAnimation(name, dsm, speaking_d, done_d=Null()):
        return DynamicDisplayable(while_speaking(name, dsm, speaking_d, done_d))


    def FlapMouth(mouth_default, mouth_speaking, cha, dsm):
        mouth_animated = flapmouth(mouth_default, mouth_speaking)
        return SpeakingAnimation(cha, dsm, mouth_animated, mouth_default)


    def BlinkEyes(eyes_default, eyes_blink):
        return blinkeyes(eyes_default, eyes_blink)


    def BlinkTransition(eyes_default, eyes_alt, eyes_closed):
        return blinktransition(eyes_default, eyes_alt, eyes_closed)


    def AlertBlink(layer):
        return alertblink(layer)