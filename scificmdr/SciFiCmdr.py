import PySimpleGUI as sg
from rapidfuzz.process import extract

__version__ = "0.0.1"


class CommandRegister:
    def __init__(self):
        self.commands = {}
        self.desc_text = {}

    def register(self, name, description=None):
        """
        Registers a command.
        The command is converted to lowercase before adding.
        All lookup is lowercase going forward.
        """
        name_lower = name.lower()
        if self.is_command(name_lower):
            raise KeyError(name_lower + " is already a registered command.")
        else:
            self.commands[name_lower] = description
            self.desc_text[name_lower] = (
                name_lower + " : " + description.lower()
            )

    def deregister(self, name):
        """
        Deregisters (removes) command
        """
        self.commands.pop(name.lower())
        self.desc_text.pop(name.lower())

    def is_command(self, name):
        return name.lower() in self.commands.keys()

    def match(self, input):
        results = extract(input, self.desc_text, score_cutoff=75)
        return results

    def display(self, name):
        return self.desc_text[name]

    def command_from_display(self, display_text):
        return display_text.split(" : ")[0]


COMMANDS = CommandRegister()


def register_command(name, description=None):
    COMMANDS.register(name, description)


def deregister_command(name):
    COMMANDS.deregister(name)


def is_command(name):
    return COMMANDS.is_command(name)


def choose_command(
    title="Choose command", allow_unlisted=True, commands=COMMANDS
):
    cmd = None

    layout = [
        [
            sg.Input(
                enable_events=True,
                focus=True,
                pad=(0, 0),
                font=("Helvetica", 24),
                k="query",
            )
        ],
        [
            sg.Listbox(
                [],
                size=(10, 5),
                select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
                expand_x=True,
                expand_y=True,
                no_scrollbar=True,
                font=("Helvetica", 16),
                k="options",
            )
        ],
    ]

    window = sg.Window(
        title,
        layout,
        default_element_size=(50, 1),
        no_titlebar=True,
        grab_anywhere=True,
        use_default_focus=False,
        keep_on_top=True,
        element_padding=(0, 0),
        margins=(0, 0),
        alpha_channel=0.8,
        finalize=True,
    )

    window.bind("<Return>", "-SUBMIT-")
    window.bind("<Escape>", "-EXIT-")

    # unbind all tab binding from tk root
    # see https://stackoverflow.com/a/58494895/9483968
    # and then bind the tab key for completion
    window.TKroot.unbind_all("<Tab>")
    window.TKroot.unbind_all("<<NextWindow>>")
    window.TKroot.unbind_all("<<PrevWindow>>")
    window.bind("<Tab>", "-COMPLETE_COMMAND-")
    window.bind("<Down>", "-DOWN_ARROW-")
    window.bind("<Up>", "-UP_ARROW-")

    window["query"].set_focus(force=True)

    while True:
        event, values = window.read()

        print(event)
        print(values)

        if event in ("-EXIT-", sg.WIN_CLOSED):
            break
        elif event == "query":
            matches = commands.match(values["query"])
            optls = []
            for m in matches:
                optls.append(commands.display(m[2]))

            # TODO: changing visiblity of the result listbox breaks its size,
            # so skipping that for now

            if len(optls) > 0:
                window["options"].update(values=optls, set_to_index=0)
            else:
                window["options"].update(values=optls)
        elif event == "-COMPLETE_COMMAND-":
            if len(values["options"]) > 0:
                window["query"].update(
                    commands.command_from_display(values["options"][0])
                )
        elif event == "-SUBMIT-":
            cmd = values["query"]
            break

    window.close()
    # sg.popup('You entered', text_input)
    return cmd


if __name__ == "__main__":
    register_command("apple", "is a red fruit")
    register_command("cherry", "a red fruit")
    register_command("banana", "is a yellow fruit")
    register_command("pineapple", "is a yellow and green fruit")
    register_command("brinjal", "is a purple vegetable")
    print(COMMANDS.match("red"))
    # exit(0)
    x = choose_command()
    print(x)
