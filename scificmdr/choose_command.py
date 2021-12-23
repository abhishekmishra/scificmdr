import PySimpleGUI as sg
from rapidfuzz.process import *

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
            self.desc_text[name_lower] = name_lower + ' ' + description.lower()

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

COMMANDS = CommandRegister()


def register_command(name, description=None):
    COMMANDS.register(name, description)


def deregister_command(name):
    COMMANDS.deregister(name)


def is_command(name):
    return COMMANDS.is_command(name)


def choose_command(title="Choose command", allow_unlisted=True, commands=COMMANDS):
    cmd = None

    layout = [[sg.Input(enable_events=True, focus=True, pad=(0, 0), k="command_query")]]

    window = sg.Window(
        title,
        layout,
        default_element_size=(120, 1),
        no_titlebar=True,
        grab_anywhere=True,
        use_default_focus=False,
        element_padding=(0, 0),
        margins=(0, 0),
        finalize=True,
    )
    window.bind("<Return>", "-SUBMIT-")
    window.bind("<Escape>", "-EXIT-")
    window["command_query"].set_focus(force=True)

    while True:
        event, values = window.read()

        print(event)
        print(values)

        if event in ("-EXIT-", sg.WIN_CLOSED):
            break
        elif event == "-SUBMIT-":
            cmd = values["command_query"]
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
    print(COMMANDS.match('red'))
    exit(0)
    x = choose_command()
    print(x)
