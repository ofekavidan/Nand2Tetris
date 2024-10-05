"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """Encapsulates access to the input code. Reads an assembly program
    by reading each command line-by-line, parses the current command,
    and provides convenient access to the commands components (fields
    and symbols). In addition, removes all white space and comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        self.input_lines_init = input_file.read().splitlines()
        self.input_lines = []
        for line in self.input_lines_init:
            line = line.replace(" ", "")
            line = line.replace('\t', "")
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

    def get_cur_line_number(self) -> int:
        """
        returns the number of the current line.
        """
        return self.cur_line

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
        """
        self.cur_line = self.cur_line + 1

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal
            number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a
            symbol.
        """

        if '@' in self.input_lines[self.cur_line]:
            return "A_COMMAND"
        elif self.input_lines[self.cur_line][0] == "(":
            return "L_COMMAND"
        return "C_COMMAND"

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        commandType = self.command_type()
        if commandType == "A_COMMAND":
            return self.input_lines[self.cur_line][1:]
        if commandType == "L_COMMAND":
            length = len(self.input_lines[self.cur_line])
            return self.input_lines[self.cur_line][1:length - 1]
        return "null"

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        commandType = self.command_type()
        if commandType == "C_COMMAND" and '=' in self.input_lines[
            self.cur_line]:
            equalInd = self.input_lines[self.cur_line].find('=')
            return self.input_lines[self.cur_line][:equalInd]
        return "null"

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        commandType = self.command_type()
        if commandType == "C_COMMAND" and '=' in self.input_lines[
            self.cur_line]:
            equalInd = self.input_lines[self.cur_line].find('=')
            comp = self.input_lines[self.cur_line][equalInd + 1:]
            if ';' in comp:
                semicolonInd = comp.find(';')
                return comp[:semicolonInd]

            return self.input_lines[self.cur_line][equalInd + 1:]
        elif commandType == "C_COMMAND" and ';' in self.input_lines[
            self.cur_line]:
            semicolonInd = self.input_lines[self.cur_line].find(';')
            return self.input_lines[self.cur_line][:semicolonInd]
        elif commandType == "C_COMMAND":
            return self.input_lines[self.cur_line]

        return "null"

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        commandType = self.command_type()
        if commandType == "C_COMMAND" and ';' in self.input_lines[
            self.cur_line]:
            semicolonInd = self.input_lines[self.cur_line].find(';')
            return self.input_lines[self.cur_line][semicolonInd + 1:]
        return "null"
