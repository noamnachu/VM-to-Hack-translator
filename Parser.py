"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """
    # Parser

    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient
    access to their components.
    In addition, it removes all white space and comments.

    ## VM Language Specification

    A .vm file is a stream of characters. If the file represents a
    valid program, it can be translated into a stream of valid assembly
    commands. VM commands may be separated by an arbitrary number of whitespace
    characters and comments, which are ignored. Comments begin with "//" and
    last until the line’s end.
    The different parts of each VM command may also be separated by an arbitrary
    number of non-newline whitespace characters.

    - Arithmetic commands:
      - add, sub, and, or, eq, gt, lt
      - neg, not, shiftleft, shiftright
    - Memory segment manipulation:
      - push <segment> <number>
      - pop <segment that is not constant> <number>
      - <segment> can be any of: argument, local, static, constant, this, that,
                                 pointer, temp
    - Branching (only relevant for project 8):
      - label <label-name>
      - if-goto <label-name>
      - goto <label-name>
      - <label-name> can be any combination of non-whitespace characters.
    - Functions (only relevant for project 8):
      - call <function-name> <n-args>
      - function <function-name> <n-vars>
      - return
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
            input_file (typing.TextIO): input file.
        """
        self.index = 0
        self.input_instructions = input_file.read().splitlines()
        self.clean_instructions = \
            self.remove_white_spaces(self.input_instructions)
        self.length = len(self.clean_instructions)

    def remove_white_spaces(self, input_instructions: typing.List[str]) \
            -> typing.List[str]:
        clean_instructions = []
        for line in input_instructions:
            comment_index = line.find('//')
            if comment_index != -1:
                line = line[:comment_index]
            # line = line.replace(" ", "")
            if line:
                clean_instructions.append(line)
        return clean_instructions

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return self.length > self.index

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        if self.has_more_commands():
            self.index += 1

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        line = self.clean_instructions[self.index]
        if line.startswith("push"):
            return "C_PUSH"
        elif line.startswith("pop"):
            return "C_POP"
        elif line.startswith("label"):
            return "C_LABEL"
        elif line.startswith("goto"):
            return "C_GOTO"
        elif line.startswith("if-goto"):
            return "C_IF"
        elif line.startswith("function"):
            return "C_FUNCTION"
        elif line.startswith("return"):
            return "C_RETURN"
        elif line.startswith("call"):
            return "C_CALL"
        else:
            return "C_ARITHMETIC"

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned.
            Should not be called if the current command is "C_RETURN".
        """
        if self.command_type() != "C_RETURN":
            line = self.clean_instructions[self.index]
            args = line.split()
            com_type = self.command_type()
            if com_type == "C_ARITHMETIC":
                return args[0]
            return args[1]

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP",
            "C_FUNCTION" or "C_CALL".
        """
        line = self.clean_instructions[self.index]
        args = line.split()
        com_type = self.command_type()
        if com_type == "C_PUSH" or com_type == "C_POP" or \
                com_type == "C_FUNCTION" or com_type == "C_CALL":
            return args[2]
