import PySimpleGUI as sg


class CommandRegister:
    def __init__(self):
        self.commands = {}

    def register(self, name, description=None):
        """
        Registers a command
        """
        if self.is_command(name):
            raise KeyError(name + " is already a registered command.")
        else:
            self.commands[name] = description

    def deregister(self, name):
        """
        Deregisters (removes) command
        """
        self.commands.pop(name)

    def is_command(self, name):
        return name in self.commands.keys()


COMMANDS = CommandRegister()


def choose_command(title="Choose command", allow_unlisted=True):
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
    x = choose_command()
    print(x)
