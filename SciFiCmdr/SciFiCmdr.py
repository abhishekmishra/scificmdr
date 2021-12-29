import PySimpleGUI as sg
from rapidfuzz.process import extract
import logging

__version__ = "0.0.1"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class CommandRegister:
    def __init__(self):
        self.commands = {}
        self.commandfns = {}
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
            self.commandfns[name_lower] = []
            self.desc_text[name_lower] = (
                name_lower + " : " + description.lower()
                if description is not None
                else name_lower
            )

    def register_handler(self, name, fn):
        if fn and self.is_command(name):
            self.commandfns[name.lower()].append(fn)

    def get_handlers(self, name):
        return self.commandfns[name.lower()]

    def deregister(self, name):
        """
        Deregisters (removes) command
        """
        name_lower = name.lower()
        self.commands.pop(name_lower)
        self.desc_text.pop(name_lower)
        self.commandfns.pop(name_lower)

    def is_command(self, name):
        return name.lower() in self.commands.keys()

    def match(self, input):
        results = extract(input, self.desc_text, score_cutoff=75)
        return results

    def display(self, name):
        return self.desc_text[name.lower()]

    def command_from_display(self, display_text):
        return display_text.split(" : ")[0]


COMMANDS = CommandRegister()


def register_command(name, description=None):
    COMMANDS.register(name, description)


def register_handler(name, fn):
    COMMANDS.register_handler(name, fn)


def get_handlers(name):
    return COMMANDS.get_handlers(name)


def deregister_command(name):
    COMMANDS.deregister(name)


def is_command(name):
    return COMMANDS.is_command(name)


def run_command(command_name, **kwargs):
    """
    Run command given by command_name(str) with arguments window, event,
    and values from the pysimplegui window

    Parameters:
        command_name (str): name of the command to run.
            program will look for method '%command_name%'
            in global scope to run.

        kwargs: the arguments to the command.
            these will be passed as-is to the command function if found.

    Returns:
        Return value of executed command function.

    Throws:
        NameError if cmd_%command_name% not found.
    """
    logger.debug(
        "running command {} with args {}".format(command_name, kwargs)
    )

    if is_command(command_name) is not None:
        cmd_handlers = get_handlers(command_name)
        ret = None
        for cmdfn in cmd_handlers:
            ret = cmdfn(**kwargs)
        return ret
    else:
        NameError(command_name + " is not a command")


# see https://stackoverflow.com/a/54030205/9483968
def cmdhandler(command=None):
    """
    Returns the decorator which will return the command function as-is
    but will register the command if required and then register
    the function as the command handler as well.

    Parameters:
        command (str): name of the command for which this function is
            a handler. If the name is not provided, the function name
            becomes the command name. This is to avoid repetition when
            command name and handler are same.

    Returns:
        the decorator
    """

    def wrap(f):
        cmdname = command
        if cmdname is None:
            cmdname = f.__name__
        if not is_command(cmdname):
            register_command(cmdname)
            logger.info("Registered command {}".format(cmdname))
        register_handler(cmdname, f)
        logger.info("Registered handler {} for {}".format(f, cmdname))
        return f

    return wrap


def commander(title="SciFiCmdr", allow_unlisted=True, commands=COMMANDS):
    cmd = None

    theme_bgcolour = sg.theme_background_color()
    print(theme_bgcolour)

    layout = [
        [
            sg.Input(
                enable_events=True,
                focus=True,
                pad=(0, 0),
                font=("Helvetica", 24),
                size=(50, 5),
                k="query",
            )
        ],
        [
            sg.Listbox(
                [],
                font=("Helvetica", 24),
                size=(50, 5),
                select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
                auto_size_text=False,
                expand_x=True,
                expand_y=True,
                no_scrollbar=True,
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
        transparent_color=theme_bgcolour,
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
    window["options"].update(visible=False)

    # don't know which of these works to bring to front
    # and have focus when started with desktop keyboard
    # shortcut.
    window.bring_to_front()
    window.force_focus()
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
                window["options"].update(visible=True)
            else:
                window["options"].update(values=optls)
                window["options"].update(visible=False)
        elif event == "-COMPLETE_COMMAND-":
            if len(values["options"]) > 0:
                window["query"].update(
                    commands.command_from_display(values["options"][0])
                )
        elif event == "-DOWN_ARROW-":
            focused = window.find_element_with_focus()
            indexes = window["options"].get_indexes()
            opt_vals = window["options"].get_list_values()
            if not focused or focused.Key != "options":
                if len(opt_vals) > 0:
                    window["options"].set_focus(True)
                    window["options"].set_value(values=[opt_vals[0]])
                else:
                    window["query"].set_focus(True)
            elif focused.Key == "options":
                idx = None
                if len(indexes) > 0:
                    idx = indexes[0]
                if idx is not None:
                    # if reached last element cycle to the query
                    # else select the next option
                    if idx >= (len(opt_vals) - 1):
                        window["query"].set_focus(True)
                    else:
                        window["options"].set_value(values=[opt_vals[idx + 1]])
                else:
                    # select first element (this should not happen
                    # where options was focused but no index was selected)
                    # except when there were no options
                    if len(opt_vals) > 0:
                        window["options"].set_value(values=[opt_vals[0]])
                    else:
                        window["query"].set_focus(True)
        elif event == "-UP_ARROW-":
            focused = window.find_element_with_focus()
            indexes = window["options"].get_indexes()
            opt_vals = window["options"].get_list_values()
            if not focused or focused.Key != "options":
                if len(opt_vals) > 0:
                    window["options"].set_focus(True)
                    window["options"].set_value(values=[opt_vals[-1]])
                else:
                    window["query"].set_focus(True)
            elif focused.Key == "options":
                idx = None
                if len(indexes) > 0:
                    idx = indexes[0]
                if idx is not None:
                    # if reached first element cycle to the query
                    # else select the next option
                    if idx <= 0:
                        window["query"].set_focus(True)
                    else:
                        window["options"].set_value(values=[opt_vals[idx - 1]])
                else:
                    # select first element (this should not happen
                    # where options was focused but no index was selected)
                    # except when there were no options
                    if len(opt_vals) > 0:
                        window["options"].set_value(values=[opt_vals[-1]])
                    else:
                        window["query"].set_focus(True)
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
    x = commander()
    print(x)
