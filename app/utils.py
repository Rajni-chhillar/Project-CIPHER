def calculate_level(xp):
    if xp < 100:
        return 1
    elif xp < 300:
        return 2
    elif xp < 600:
        return 3
    elif xp < 1000:
        return 4
    else:
        return 5


def calculate_rank(level):
    ranks = {
        1:"Rookie Agent",
        2:"Investigator",
        3:"Detective",
        4:"Elite Agent",
        5:"Cipher Master"
    }
    return ranks.get(
        level,
        "Rookie Agent"
    )