def get_answer(text):
    if len(text) % 2 == 0:
        return "{} - yes".format(text)
    return "{} - no".format(text)