def unlock_badges(user):
    badges = 0

    if user.missions_completed >= 1:
        badges += 1
    if user.missions_completed >= 5:
        badges += 1
    if user.level >= 3:
        badges += 1
    if user.level >= 5:
        badges += 1
    user.badges = badges