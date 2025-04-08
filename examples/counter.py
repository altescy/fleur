import fleur


@fleur.component
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


@fleur.component
def App():
    return fleur.tags.div(
        {"class": "flex flex-col items-center justify-center h-screen"},
        Counter(),
        fleur.tags.p(
            {"class": "text-gray-500 text-sm"},
            "Click the buttons to increment or decrement the count.",
        ),
    )


print(fleur.render(App))
