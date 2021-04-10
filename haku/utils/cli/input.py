from typing import Callable, Optional

from haku.utils.cli import Console
from haku.utils.cli.renderable import Group, Text


class Choice:
    """Input choice renderable"""

    def __init__(
        self,
        console: Console,
        get_input: Callable[[str], str] = input,
        exit_on: Optional[str] = None,
        prompt: Text = Text(">"),
        error_prompt: Text = Text("|"),
        error_message: Text = Text("Input error, choose one from"),
    ):
        self.console = console
        self.get_input = get_input
        self.prompt = prompt
        self.options = {}
        self.exit_on = exit_on
        self.error_prompt = error_prompt
        self.error_message = error_message

        if self.exit_on is not None:
            self.options[self.exit_on] = lambda _: None

    def __setitem__(self, option: str, action: Callable[[str], Optional[str]]):
        self.options[option] = action

    def __getitem__(self, option: str) -> Callable[[str], Optional[str]]:
        return self.options[option]

    def build_help(self) -> Group:
        """Build help from the existing options"""

        tokens = Group(*map(Text, self.options), separator=" | ")
        return Group(Text("["), tokens, Text("]"), separator=" ")

    def input(self, width: Optional[int] = None) -> str:
        """Get user input"""

        width = width or self.console.columns
        prompt = Group(self.prompt, Text(" "))
        return self.get_input(prompt.render(width))

    def ask(self, exit_on: Optional[str] = None):
        """Ask the question and execute the callback linked to the uset choice"""

        exit_on = exit_on or self.exit_on
        if exit_on is not None:
            exc = Exception("`exit_on` must be an existing option")
            assert exit_on in self.options, exc

        width = self.console.columns
        choice = self.input(width)

        while choice not in self.options:
            error = Group(
                self.error_prompt,
                self.error_message,
                self.build_help(),
                separator=" ",
            )

            self.console.print(error)
            choice = self.input(width)

        content = self.options[choice](width)
        if content is not None:
            self.console.print(content)

        if exit_on is not None and choice != exit_on:
            self.ask(exit_on)

    def __call__(self, width: int):
        self.ask()
