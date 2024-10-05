"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter

KEYWORD_CONSTANT_SET = {"true", "false", "null", "this"}
KEYWORD_CONSTANT_DICT = {"true": ("constant", 1), "false": ("constant", 0),
                         "null": ("constant", 0), "this": ("pointer", 0)}

UNARY_OP_DICT = {"~": "not", "-": "neg", "#": "shiftright", "^": "shiftleft"}

OP_DICT = {"+": "add", "-": "sub", "*": "Math.multiply", "/": "Math.divide",
           "&": "and", "|": "or", "<": "lt", ">": "gt",
           "=": "eq"}
VAR_DEC_SET = {"static", "field"}
SUBROUTINE_SET = {"method", "function", "constructor"}
STATEMENTS_SET = {"do", "let", "while", "return", "if"}
# from lecture11 page 8:
KIND_DICT = {"var": "local", "argument": "argument", "field": "this",
             "static": "static"}


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.class_name = ""  # initial boot of class name
        self.tokenizer = input_stream  # initial boot of tokenizer
        self.output_file = output_stream  # initial boot of output file
        self.symbol_table = SymbolTable()  # initial boot of symbol table
        self.vmWriter = VMWriter(self.output_file)  # initial boot vm writer
        self.label_counter = 0  # initial boot of label counter
        self.compile_class()  # start the process of the translation

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.has_more_token_and_advance()  # advance from class
        # save the name of the class
        self.class_name = self.tokenizer.get_cur_token()
        self.has_more_token_and_advance()  # advance from class name
        self.has_more_token_and_advance()  # advance from {

        # check if there is field or static
        while self.tokenizer.get_cur_token() in VAR_DEC_SET:
            self.compile_class_var_dec()

        # check if the cur token is method,function,constructor
        while self.tokenizer.get_cur_token() in SUBROUTINE_SET:
            self.compile_subroutine()

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        cur_kind = self.tokenizer.get_cur_token()
        self.has_more_token_and_advance()  # advance from kind
        cur_type = self.tokenizer.get_cur_token()

        while self.tokenizer.get_cur_token() != ";":
            self.has_more_token_and_advance()  # advance from type or ,
            cur_name = self.tokenizer.get_cur_token()
            # add the var to the symbol table
            self.symbol_table.define(cur_name, cur_type, cur_kind)
            self.has_more_token_and_advance()  # advance from name
        self.has_more_token_and_advance()  # advance from ;

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        # first create a clean symbol table
        self.symbol_table.start_subroutine()

        # indicator to FUNCTION, METHOD or CONSTRUCTOR !
        cur_subroutine_type = self.tokenizer.get_cur_token()

        if cur_subroutine_type == "method":
            # add the method to the symbol table
            self.symbol_table.define("this", self.class_name, "argument")

        self.has_more_token_and_advance()  # advance from subroutine type
        self.has_more_token_and_advance()  # advance from return value

        cur_func_name = self.tokenizer.get_cur_token()
        self.has_more_token_and_advance()  # advance from function name
        self.has_more_token_and_advance()  # advance from (

        self.compile_parameter_list()

        self.has_more_token_and_advance()  # advance from ) to {
        self.has_more_token_and_advance()  # advance from { to subroutine body

        num_of_vars = 0
        # now handle the function's body
        while self.tokenizer.get_cur_token() == "var":
            num_of_vars += self.compile_var_dec()

        # now divide to cases and handle the subroutine type
        # helped by Ella-Falik summary

        # in case of a method
        if cur_subroutine_type == "method":
            self.output_file.write(f'function {self.class_name}.'
                                   f'{cur_func_name} {num_of_vars}\n')
            self.output_file.write("push argument 0\n")
            self.output_file.write("pop pointer 0\n")

        # in case of a function
        if cur_subroutine_type == "function":
            self.output_file.write(f'function {self.class_name}.'
                                   f'{cur_func_name} {num_of_vars}\n')

        # in case of a constructor
        if cur_subroutine_type == "constructor":
            self.output_file.write(f'function {self.class_name}.'
                                   f'{cur_func_name} {num_of_vars}\n')
            num_of_fields = self.symbol_table.var_count("FIELD")
            self.output_file.write(f'push constant {num_of_fields}\n')
            self.output_file.write("call Memory.alloc 1\n")
            self.output_file.write("pop pointer 0\n")

        # handle the subroutine body
        while self.tokenizer.get_cur_token() != "}":
            if self.tokenizer.get_cur_token() == "function" or \
                    self.tokenizer.get_cur_token() == "method" or \
                    self.tokenizer.get_cur_token() == "constructor":
                return
            if self.tokenizer.get_cur_token() != "var":
                self.compile_statements()
            self.has_more_token_and_advance()

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        # as long as the parameter list goes on...
        while self.tokenizer.get_cur_token() != ")":
            cur_type = self.tokenizer.get_cur_token()
            self.has_more_token_and_advance()  # advance from type
            self.symbol_table.define(self.tokenizer.get_cur_token(),
                                     cur_type, "argument")
            self.has_more_token_and_advance()  # advance from name
            if self.tokenizer.get_cur_token() != ")":
                self.has_more_token_and_advance()  # advance from ,

    def compile_var_dec(self) -> int:
        """Compiles a var declaration."""
        self.has_more_token_and_advance()  # advance from var
        num_vars = 0  # counts the number of vars
        # as long as the var declaration goes on...
        while self.tokenizer.get_cur_token() != ";":
            cur_type = self.tokenizer.get_cur_token()
            self.has_more_token_and_advance()  # advance from type
            cur_name = self.tokenizer.get_cur_token()
            # add the var to the symbol table
            self.symbol_table.define(cur_name, cur_type, "VAR")
            num_vars += 1
            self.has_more_token_and_advance()  # advance from var name

            # as long as the var declaration goes on...
            while self.tokenizer.get_cur_token() == ",":
                self.has_more_token_and_advance()  # advance from ,
                cur_name = self.tokenizer.get_cur_token()
                # add the var to the symbol table
                self.symbol_table.define(cur_name, cur_type, "VAR")
                num_vars += 1
                self.has_more_token_and_advance()  # advance from var name
        self.has_more_token_and_advance()  # advance from ;
        return num_vars

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        while self.tokenizer.get_cur_token() in STATEMENTS_SET:
            if self.tokenizer.get_cur_token() == "do":
                self.compile_do()
            elif self.tokenizer.get_cur_token() == "let":
                self.compile_let()
            elif self.tokenizer.get_cur_token() == "while":
                self.compile_while()
            elif self.tokenizer.get_cur_token() == "return":
                self.compile_return()
            elif self.tokenizer.get_cur_token() == "if":
                self.compile_if()

        if self.tokenizer.get_cur_token() != "}":
            self.has_more_token_and_advance()  # advance from ;

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.has_more_token_and_advance()  # advance from do

        cur_identifier = self.tokenizer.get_cur_token()  # i.e Output
        self.has_more_token_and_advance()  # advance from the identifier,
        # i.e Output

        # initial boot of argument counter:
        num_args = 0

        # if the subroutine continues after the dot, for instance
        # Output.printInt
        if self.tokenizer.get_cur_token() == ".":
            # for instance: Output.
            if cur_identifier in self.symbol_table.symbol_table_dict_class:
                self.vmWriter.write_push(
                    KIND_DICT[self.symbol_table.kind_of(cur_identifier)],
                    self.symbol_table.index_of(cur_identifier))
                cur_identifier = self.symbol_table.symbol_table_dict_class[
                    cur_identifier][0]
                num_args += 1
            if cur_identifier in self.symbol_table.symbol_table_dict_subroutine:
                self.vmWriter.write_push(KIND_DICT[self.symbol_table.kind_of(
                    cur_identifier)], self.symbol_table.index_of(
                    cur_identifier))

                cur_identifier = \
                    self.symbol_table.symbol_table_dict_subroutine[
                        cur_identifier][0]
                num_args += 1

            cur_identifier += self.tokenizer.get_cur_token()
            self.has_more_token_and_advance()  # advance from dot
            # for instance: Output.printInt
            cur_identifier += self.tokenizer.get_cur_token()
            self.has_more_token_and_advance()  # advance second-part of the
            # subroutine
            self.has_more_token_and_advance()  # advance from (
            num_args += self.compile_expression_list()
            self.has_more_token_and_advance()  # advance from )

            # from video 11.7 19:43
            self.output_file.write(f'call {cur_identifier} {num_args}\n')
            self.vmWriter.write_pop("TEMP", 0)
            self.has_more_token_and_advance()
        else:
            self.has_more_token_and_advance()  # advance from (
            self.vmWriter.write_push("POINTER", 0)
            num_args += 1
            num_args += self.compile_expression_list()
            self.has_more_token_and_advance()  # advance from )
            cur_identifier = self.class_name + "." + cur_identifier
            self.output_file.write(f'call {cur_identifier} {num_args}\n')
            self.vmWriter.write_pop("TEMP", 0)

            self.has_more_token_and_advance()  # advance from ;

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.has_more_token_and_advance()  # advance from let
        cur_name = self.tokenizer.get_cur_token()  # let x = .. then cur_name=x
        self.has_more_token_and_advance()  # advance from cur_name
        array_flag = False  # initial boot

        if self.tokenizer.get_cur_token() == "[":
            array_flag = True
            cur_name_kind = self.symbol_table.kind_of(cur_name)
            cur_name_ind = self.symbol_table.index_of(cur_name)
            self.vmWriter.write_push(KIND_DICT[cur_name_kind], cur_name_ind)

            self.has_more_token_and_advance()  # advance from [
            self.compile_expression()
            self.output_file.write("add\n")  # ella-falik summary
            self.has_more_token_and_advance()

        self.has_more_token_and_advance()  # advance from =
        self.compile_expression()

        if not array_flag:
            self.vmWriter.write_pop(
                KIND_DICT[self.symbol_table.kind_of(cur_name)],
                self.symbol_table.index_of(cur_name))
            self.has_more_token_and_advance()  # advance from ;
        else:  # cur token is =
            self.vmWriter.write_pop("temp", 0)  # ella-falik summary
            self.vmWriter.write_pop("pointer", 1)
            self.vmWriter.write_push("temp", 0)
            self.vmWriter.write_pop("that", 0)
            self.has_more_token_and_advance()  # advance from ;

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.has_more_token_and_advance()  # advance from while
        self.label_counter += 1
        cur_index = self.label_counter

        self.vmWriter.write_label("WHILE_FIRST" + str(cur_index))
        self.has_more_token_and_advance()  # advance from (
        self.compile_expression()
        self.output_file.write("not\n")
        self.vmWriter.write_if("WHILE_SECOND" + str(cur_index))
        self.has_more_token_and_advance()  # advance from )

        self.has_more_token_and_advance()  # advance from {
        self.compile_statements()
        self.vmWriter.write_goto("WHILE_FIRST" + str(cur_index))
        self.vmWriter.write_label("WHILE_SECOND" + str(cur_index))

        self.has_more_token_and_advance()  # advance from }

    def compile_return(self) -> None:
        """Compiles a return statement."""

        self.has_more_token_and_advance()  # advance from return
        if self.tokenizer.get_cur_token() != ";":
            self.compile_expression()

        else:
            self.vmWriter.write_push("CONSTANT", 0)
        self.vmWriter.write_return()

        self.has_more_token_and_advance()  # advance from ;

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.has_more_token_and_advance()  # advance from if
        self.has_more_token_and_advance()  # advance from (

        self.label_counter += 1
        cur_index = self.label_counter

        self.compile_expression()
        self.output_file.write("not\n")
        self.vmWriter.write_if("IF_FIRST" + str(cur_index))

        self.has_more_token_and_advance()  # advance from )

        self.has_more_token_and_advance()  # advance from {

        self.compile_statements()

        self.vmWriter.write_goto("IF_SECOND" + str(cur_index))

        self.has_more_token_and_advance()  # advance from }
        if self.tokenizer.get_cur_token() == "else":
            self.vmWriter.write_label("IF_FIRST" + str(cur_index))
            self.has_more_token_and_advance()  # advance from else
            self.has_more_token_and_advance()  # advance from {
            self.compile_statements()
            self.vmWriter.write_label("IF_SECOND" + str(cur_index))
            self.has_more_token_and_advance()  # advance from }
        else:
            self.vmWriter.write_label("IF_FIRST" + str(cur_index))
            self.vmWriter.write_label("IF_SECOND" + str(cur_index))

    def compile_expression_list(self) -> int:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        args_counter = 0

        if self.tokenizer.get_cur_token() != ")":
            self.compile_expression()
            args_counter += 1
            while self.tokenizer.get_cur_token() == ",":
                self.has_more_token_and_advance()  # advance from ,
                self.compile_expression()
                args_counter += 1
        return args_counter

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.compile_term()
        while self.tokenizer.get_cur_token() in OP_DICT:
            cur_operator = self.tokenizer.get_cur_token()
            self.has_more_token_and_advance()  # advance from operator name
            self.compile_term()

            # prints the op
            if cur_operator == "*" or cur_operator == "/":
                self.vmWriter.write_call(OP_DICT[cur_operator], 2)
            else:
                self.output_file.write(OP_DICT[cur_operator] + "\n")

    def compile_string(self) -> None:
        """
        This function handles the situation of pushing a String into the stack
        the function does it by pushing every single character of the string,
        using ASCII table (and ord built-in function of python)
        Returns: None
        """
        # first, get the length of the given string
        # then, push it into the stack (why? Targil!)
        self.vmWriter.write_push("constant",
                                 len(self.tokenizer.get_cur_token()) - 2)
        # from Ella-Falik summary, page 73
        self.vmWriter.write_call("String.new", 1)
        # iterate the string (character by character)
        for char in self.tokenizer.string_val():
            # from Ella-Falik summary, page 73
            self.vmWriter.write_push("constant", ord(char))
            # from lecture 11
            self.vmWriter.write_call("String.appendChar", 2)
        self.has_more_token_and_advance()

    def compile_term(self) -> None:
        """Compiles a term.
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "."
        suffices to distinguish between the three possibilities. Any other
        token is not part of this term and should not be advanced over.
        """
        if self.tokenizer.token_type() == "INT_CONST":
            self.vmWriter.write_push("CONSTANT",
                                     self.tokenizer.get_cur_token())
            self.has_more_token_and_advance()  # advance from the number

        elif self.tokenizer.token_type() == "STRING_CONST":
            self.compile_string()

        elif self.tokenizer.get_cur_token() in KEYWORD_CONSTANT_SET:
            self.vmWriter.write_push(KEYWORD_CONSTANT_DICT[
                                         self.tokenizer.get_cur_token()][0],
                                     KEYWORD_CONSTANT_DICT[
                                         self.tokenizer.get_cur_token()][1])
            if self.tokenizer.get_cur_token() == "true":
                self.output_file.write("neg\n")

            self.has_more_token_and_advance()  # advance from the keyword const

        elif self.tokenizer.get_cur_token() in UNARY_OP_DICT:
            cur_op = self.tokenizer.get_cur_token()
            self.has_more_token_and_advance()  # advance from the op
            self.compile_term()
            self.output_file.write(UNARY_OP_DICT[cur_op] + "\n")

        elif self.tokenizer.get_cur_token() == "(":

            self.has_more_token_and_advance()  # advance from (
            self.compile_expression()

            self.has_more_token_and_advance()  # advance from )

        elif self.tokenizer.token_type() == "IDENTIFIER":
            cur_identifier = self.tokenizer.get_cur_token()
            self.has_more_token_and_advance()  # advance from the identifier
            next_token = self.tokenizer.get_cur_token()

            if next_token == "[":
                cur_name_kind = self.symbol_table.kind_of(cur_identifier)
                cur_name_ind = self.symbol_table.index_of(cur_identifier)
                self.vmWriter.write_push(KIND_DICT[cur_name_kind],
                                         cur_name_ind)
                self.has_more_token_and_advance()  # advance from [
                self.compile_expression()

                self.has_more_token_and_advance()  # advance from ]
                self.output_file.write("add\n")
                self.vmWriter.write_pop("pointer", 1)
                self.vmWriter.write_push("that", 0)

            elif next_token == "(":
                # ask on shaat kabala
                self.has_more_token_and_advance()
                self.compile_expression_list()
                self.has_more_token_and_advance()

            elif next_token == ".":
                num_args = 0  # counter for the number of arguments of the term
                # for instance: Output.
                if cur_identifier in \
                        self.symbol_table.symbol_table_dict_subroutine:
                    cur_kind = \
                        KIND_DICT[
                            self.symbol_table.symbol_table_dict_subroutine[
                                cur_identifier][1]]
                    cur_ind = self.symbol_table.symbol_table_dict_subroutine[
                        cur_identifier][2]
                    self.output_file.write("push " + str(cur_kind) + " " +
                                           str(cur_ind) + "\n")
                    cur_identifier = self.symbol_table.type_of(cur_identifier)
                    num_args += 1

                elif cur_identifier in \
                        self.symbol_table.symbol_table_dict_class:
                    cur_kind = \
                        KIND_DICT[
                            self.symbol_table.symbol_table_dict_class[
                                cur_identifier][1]]
                    cur_ind = self.symbol_table.symbol_table_dict_class[
                        cur_identifier][2]
                    self.output_file.write("push " + str(cur_kind) + " " +
                                           str(cur_ind) + "\n")
                    cur_identifier = self.symbol_table.type_of(cur_identifier)
                    num_args += 1

                cur_identifier += self.tokenizer.get_cur_token()

                self.has_more_token_and_advance()  # advance from dot
                # for instance: Output.printInt
                cur_identifier += self.tokenizer.get_cur_token()
                self.has_more_token_and_advance()  # advance second-part of
                # the subroutine
                self.has_more_token_and_advance()
                num_args += self.compile_expression_list()

                # from video 11.7 19:43
                self.output_file.write(f'call {cur_identifier} {num_args}\n')
                self.has_more_token_and_advance()
            else:
                if cur_identifier in \
                        self.symbol_table.symbol_table_dict_subroutine:
                    cur_kind = \
                        KIND_DICT[
                            self.symbol_table.symbol_table_dict_subroutine[
                                cur_identifier][1]]
                    cur_ind = self.symbol_table.symbol_table_dict_subroutine[
                        cur_identifier][2]
                    self.output_file.write("push " + str(cur_kind) + " " +
                                           str(cur_ind) + "\n")
                elif cur_identifier in \
                        self.symbol_table.symbol_table_dict_class:
                    cur_kind = \
                        KIND_DICT[
                            self.symbol_table.symbol_table_dict_class[
                                cur_identifier][1]]
                    cur_ind = self.symbol_table.symbol_table_dict_class[
                        cur_identifier][2]
                    self.output_file.write("push " + str(cur_kind) + " " +
                                           str(cur_ind) + "\n")

    def has_more_token_and_advance(self) -> None:
        """ this function checks if the tokenizer has more tokens and can
            advance """
        if self.tokenizer.has_more_tokens():
            self.tokenizer.advance()
