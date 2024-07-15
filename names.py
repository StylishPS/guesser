import random as r

levels = [
    [
        {
            "name": "9blue",
            "image": "https://github.com/StylishPS/guesser_thumbnails/blob/main/easy/9blue.png?raw=true"
        },
        {
            "name": "ffffff",
            "image": "https://github.com/StylishPS/guesser_thumbnails/blob/main/easy/ffffff.png?raw=true"
        },
        {
            "name": "ok",
            "image": "https://github.com/StylishPS/guesser_thumbnails/blob/main/easy/ok.png?raw=true"
        }
    ],
        [{
            "name": "bloodbath",
            "image": "https://github.com/StylishPS/guesser_thumbnails/blob/main/easy/bloodbath.png?raw=true"
        },
        {
            "name": "auto play area",
            "image": "https://github.com/StylishPS/guesser_thumbnails/blob/main/easy/autoplayarea.png?raw=true"
        },
        {
            "name": "outerspace",
            "image": "https://github.com/StylishPS/guesser_thumbnails/blob/main/easy/outerspace.png?raw=true"
        }
    ],
    [
        {
            "name": "the nightmare",
            "image": "https://github.com/StylishPS/guesser_thumbnails/blob/main/easy/thenightmare.png?raw=true"
        },
        {
            "name": "heaven",
            "image": "https://github.com/StylishPS/guesser_thumbnails/blob/main/easy/heaven.png?raw=true"
        },
        {
            "name": "ovenbreak",
            "image": "https://github.com/StylishPS/guesser_thumbnails/blob/main/easy/ovenbreak.png?raw=true"
        }
    ]
]
names = len(levels)
name = '9blue'
for difficulty in levels:
    for level in difficulty:
        if level['name'] == 'name':
            if level in levels[0]:
                print('coco')