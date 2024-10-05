"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

C_ARITHMETIC_COMMAND = "C_ARITHMETIC"
C_PUSH_COMMAND = "C_PUSH"
C_POP_COMMAND = "C_POP"
C_LABEL_COMMAND = "C_LABEL"
C_IF_COMMAND = "C_IF"
C_GOTO_COMMAND = "C_GOTO"
C_CALL_COMMAND = "C_CALL",
C_FUNCTION_COMMAND = "C_FUNCTION"
C_RETURN_COMMAND = "C_RETURN"

PUSH_COMMAND = "push"
POP_COMMAND = "pop"
LABEL_COMMAND = "label"
IF_COMMAND = "if-goto"
GOTO_COMMAND = "goto"
CALL_COMMAND = "call"
FUNCTION_COMMAND = "function"
RETURN_COMMAND = "return"
ADD_COMMAND = "add"
SUB_COMMAND = "sub"
AND_COMMAND = "and"
OR_COMMAND = "or"
SHIFT_LEFT_COMMAND = "shiftleft"
SHIFT_RIGHT_COMMAND = "shiftright"
NEG_COMMAND = "neg"
EQ_COMMAND = "eq"
GT_COMMAND = "gt"
LT_COMMAND = "lt"
NOT_COMMAND = "not"
CONSTANT_SEGMENT = "constant"
STATIC_SEGMENT = "static"
POINTER_SEGMENT = "pointer"
TEMP_SEGMENT = "temp"
LOCAL_SEGMENT = "local"
ARGUMENT_SEGMENT = "argument"
THIS_SEGMENT = "this"
THAT_SEGMENT = "that"


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
    The different parts of each VM command may also be separated by an
    arbitrary number of non-newline whitespace characters.

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
        self.input_lines_init = input_file.read().splitlines()
        self.input_lines = []
        for line in self.input_lines_init:
            if line.isspace() or not line:
                continue
            if line.startswith("/"):
                continue
            if '/' in line:
                slashInd = line.find('/')
                line = line[:slashInd]
                self.input_lines.append(line)
                continue
            self.input_lines.append(line)

        self.num_lines = len(self.input_lines)
        self.cur_line = 0

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        if self.cur_line >= self.num_lines:
            return False
        return True

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current 
        command. Should be called only if has_more_commands() is true.
        Initially there is no current command.
        """
        self.cur_line = self.cur_line + 1

    def get_cur_command(self) -> str:
        """This function returns the current VM command (one of:add, sub,
        neg, eq, gt, lt, and, or, not, shiftleft, shiftright, push, pop, label,
        if-goto, goto, call, function, return).
        """
        return self.input_lines[self.cur_line].split()[0]

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        commands_dict = {ADD_COMMAND:C_ARITHMETIC_COMMAND,
                         SUB_COMMAND:C_ARITHMETIC_COMMAND,
                         NEG_COMMAND:C_ARITHMETIC_COMMAND,
                         EQ_COMMAND:C_ARITHMETIC_COMMAND,
                         GT_COMMAND:C_ARITHMETIC_COMMAND,
                         LT_COMMAND:C_ARITHMETIC_COMMAND,
                         AND_COMMAND:C_ARITHMETIC_COMMAND,
                         OR_COMMAND:C_ARITHMETIC_COMMAND,
                         NOT_COMMAND:C_ARITHMETIC_COMMAND,
                         SHIFT_LEFT_COMMAND:C_ARITHMETIC_COMMAND,
                         SHIFT_RIGHT_COMMAND:C_ARITHMETIC_COMMAND,
                         PUSH_COMMAND:C_PUSH_COMMAND,
                         POP_COMMAND:C_POP_COMMAND,
                         LABEL_COMMAND:C_LABEL_COMMAND,
                         IF_COMMAND:C_IF_COMMAND,
                         GOTO_COMMAND:C_GOTO_COMMAND,
                         CALL_COMMAND:C_CALL_COMMAND,
                         FUNCTION_COMMAND:C_FUNCTION_COMMAND,
                         RETURN_COMMAND:C_RETURN_COMMAND}

        return commands_dict[self.input_lines[self.cur_line].split()[0]]

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of 
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned. 
            Should not be called if the current command is "C_RETURN".
        """
        if self.command_type() == C_ARITHMETIC_COMMAND:
            return self.input_lines[self.cur_line]
        if self.command_type() == C_PUSH_COMMAND \
                or self.command_type() == C_POP_COMMAND\
                or self.command_type() == C_LABEL_COMMAND \
                or self.command_type() == C_IF_COMMAND \
                or self.command_type() == C_GOTO_COMMAND \
                or self.command_type() == C_CALL_COMMAND \
                or self.command_type() == C_FUNCTION_COMMAND:
            return self.input_lines[self.cur_line].split()[1]
        return ""

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP", 
            "C_FUNCTION" or "C_CALL".
        """
        if self.command_type() == C_PUSH_COMMAND \
                or self.command_type() == C_POP_COMMAND \
                or self.command_type() == C_CALL_COMMAND \
                or self.command_type() == C_FUNCTION_COMMAND:
            return int(self.input_lines[self.cur_line].split()[2])

        return 0
