label start:
    show mj relaxed at dsm.mj.transforms.center with dissolve

    "This is an example of how to use the Dynamic Sprite Manager in a script."

    mj "Characters, by default, bounce when they begin a new line of dialogue. {w}Note that they don't bounce when the wait or pause tags are used in the middle of a say statement."

    mj "However, on a new line, they do!"

    mj "Mouths are set to only move when a character is speaking."

    "However, eyes blink regardless of what's happening at the moment onscreen."

    show mj:
        parallel:
            ease 1.5 xpos dsm.mj.transforms.leftthird.xpos
        parallel:
            0.75
            ease 0.5 xzoom -1

    with move

    "It's also possible to break out individual components of DSM transforms, for use in animation."

    show mj plotting at dsm.mj.transforms.leftthird:
        xzoom -1

    mj "It's a sneaky way to ensure consistent animation that scales with screen resolution!"

    show mj relaxed

    show mj hat relaxed with dissolve

    mj "It's also easy to switch base sprites on the fly, without having to define new characters!"

    "This is just a small subset of what you can do with the Dynamic Sprite System."

    "For more, press Shift+S to open the inspector, which will allow you to mix and match sprite layers based on what the DSM has indexed."

    mj hat happy "Enjoy!"
