import fleur


def Counter():
    count = fleur.state(0)

    def increment():
        count.value += 1

    def decrement():
        count.value -= 1

    return fleur.tags.div(
        {"class": "flex items-center justify-center gap-2 shadow rounded p-4 w-fit"},
        "Count: ",
        count,
        "  ",
        fleur.tags.button({"onclick": increment}, "+"),
        fleur.tags.button({"onclick": decrement}, "-"),
    )


print(fleur.render(Counter))
