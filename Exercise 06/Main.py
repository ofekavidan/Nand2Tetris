"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code


def assemble_file(input_file: typing.TextIO,
                  output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    parser = Parser(input_file)
    symbolTable = SymbolTable()

    """" First-pass:
     For each label declaration of the form
     Add the pair <symbol, address to the symbol table,
     where address is the number of the instruction
     following the (symbol) label declaration
    """
    labels_count = 0
    while parser.has_more_commands():
        if parser.command_type() == "L_COMMAND":
            symbolTable.add_entry(parser.symbol(),
                                  parser.get_cur_line_number() - labels_count)
            labels_count += 1

        parser.advance()

    """ Second-pass:
    Set countSymbols to 16;
    Scan the entire program (again):
    For each instruction:
    If the instruction is @symbol,look up symbol in the symbol table;
    If <symbol, value> is found, use value to complete the
    instruction's translation; 
    Else:
    Add <symbol, n> to the symbol table.
    Use countSymbols to complete the instruction's translation.
    countSymbols++
    If the instruction is a C-instruction, translate each field
    Assemble the translated fields into a 16-bit instruction,
    and write it to the output file.
    """
    input_file.seek(0)
    secParser = Parser(input_file)
    countSymbols = 16  # n
    while secParser.has_more_commands():
        if secParser.command_type() == "A_COMMAND":
            cur_symbol = secParser.symbol()
            if cur_symbol.isnumeric():
                cur_value = int(cur_symbol)
            elif symbolTable.contains(cur_symbol):
                cur_value = symbolTable.get_address(cur_symbol)

            else:
                symbolTable.add_entry(secParser.symbol(), countSymbols)
                countSymbols += 1
                cur_value = symbolTable.get_address(cur_symbol)

            final_val = '0' + f'{cur_value:015b}'
            output_file.write(final_val + "\n")
            secParser.advance()
            continue

        elif secParser.command_type() == "C_COMMAND":
            dest_field = secParser.dest()
            comp_field = secParser.comp()
            jump_field = secParser.jump()

            code_dest = Code.dest(dest_field)
            code_comp = Code.comp(comp_field)
            code_jump = Code.jump(jump_field)
            if '<' in comp_field or '>' in comp_field:
                final_val = "101" + code_comp + code_dest + code_jump
            else:
                final_val = "111" + code_comp + code_dest + code_jump
            output_file.write(final_val + '\n')
            secParser.advance()
            continue

        elif secParser.command_type() == "L_COMMAND":
            secParser.advance()
            continue


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
