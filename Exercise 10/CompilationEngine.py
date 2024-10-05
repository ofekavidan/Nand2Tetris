"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
from JackTokenizer import JackTokenizer

KEYWORD_CONSTANT_SET = {"true", "false", "null", "this"}
UNARY_OP_SET = {"~", "-", "#", "^"}
OP_SET = {"+", "-", "*", "/", "&", "|", "<", ">", "="}
SPECIAL_SYMBOLS = {"<": "&lt;", ">": "&gt;", "&": "&amp;"}
VAR_DEC_SET = {"static", "field"}
SUBROUTINE_SET = {"method", "function", "constructor"}
STATEMENTS_SET = {"do", "let", "while", "return", "if"}


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
        self.tokenizer = input_stream
        self.output_file = output_stream
        self.compile_class()

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.output_file.write("<class>\n")
        # prints class
        self.write_cur_token_and_advance()
        # prints the name of the class
        self.write_cur_token_and_advance()
        # prints {
        self.write_cur_token_and_advance()
        # check if there is field or static
        while self.tokenizer.get_cur_token() in VAR_DEC_SET:
            self.compile_class_var_dec()

        # check if the cur token is method,function,constructor
        while self.tokenizer.get_cur_token() in SUBROUTINE_SET:
            self.compile_subroutine()
        # prints }
        self.write_cur_token_and_advance()
        self.output_file.write("</class>\n")

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        self.output_file.write("<classVarDec>\n")
        while self.tokenizer.get_cur_token() != ";":
            self.write_cur_token_and_advance()
        self.write_cur_token_and_advance()
        self.output_file.write("</classVarDec>\n")

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        self.output_file.write("<subroutineDec>\n")

        while self.tokenizer.get_cur_token() != "(":
            self.write_cur_token_and_advance()

        # prints (
        self.write_cur_token_and_advance()

        self.compile_parameter_list()
        # prints )
        self.write_cur_token_and_advance()

        self.output_file.write("<subroutineBody>\n")
        # prints {
        self.write_cur_token_and_advance()

        while self.tokenizer.get_cur_token() != "}":
            if self.tokenizer.get_cur_token() == "var":
                self.compile_var_dec()
            else:
                self.compile_statements()

        # prints }
        self.write_cur_token_and_advance()

        self.output_file.write("</subroutineBody>\n")
        self.output_file.write("</subroutineDec>\n")

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        self.output_file.write("<parameterList>\n")
        while self.tokenizer.get_cur_token() != ")":
            self.write_cur_token_and_advance()

        self.output_file.write("</parameterList>\n")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.output_file.write("<varDec>\n")
        while self.tokenizer.get_cur_token() != ";":
            self.write_cur_token_and_advance()
        # prints ;
        self.write_cur_token_and_advance()
        self.output_file.write("</varDec>\n")

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        self.output_file.write("<statements>\n")
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
            if self.tokenizer.has_more_tokens():
                self.tokenizer.advance()

        self.output_file.write("</statements>\n")

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.output_file.write("<doStatement>\n")
        while self.tokenizer.get_cur_token() != "(":
            self.write_cur_token_and_advance()

        # prints (
        self.output_file.write("<symbol> " + self.tokenizer.get_cur_token() +
                               " </symbol>\n")
        if self.tokenizer.has_more_tokens():
            self.tokenizer.advance()

        self.compile_expression_list()
        # prints )
        self.write_cur_token_and_advance()
        # prints ;
        self.write_cur_token_and_advance()

        self.output_file.write("</doStatement>\n")

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.output_file.write("<letStatement>\n")

        self.output_file.write("<keyword> " + self.tokenizer.get_cur_token()
                               + " </keyword>\n")
        if self.tokenizer.has_more_tokens():
            self.tokenizer.advance()

        self.output_file.write("<identifier> " + self.tokenizer.get_cur_token()
                               + " </identifier>\n")
        if self.tokenizer.has_more_tokens():
            self.tokenizer.advance()

        while self.tokenizer.get_cur_token() != "=":
            if self.tokenizer.get_cur_token() == "[":
                # prints [
                self.write_cur_token_and_advance()

                self.compile_expression()
                # self.tokenizer.advance()
                # prints ]
                self.write_cur_token_and_advance()
                continue

            self.write_cur_token_and_advance()

        # prints =
        self.write_cur_token_and_advance()

        self.compile_expression()

        # prints ;
        self.write_cur_token_and_advance()
        self.output_file.write("</letStatement>\n")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.output_file.write("<whileStatement>\n")
        # prints while
        self.write_cur_token_and_advance()

        # prints (
        self.write_cur_token_and_advance()

        self.compile_expression()

        # prints )
        self.write_cur_token_and_advance()

        # prints {
        self.write_cur_token_and_advance()

        self.compile_statements()

        # prints }
        self.write_cur_token_and_advance()

        self.output_file.write("</whileStatement>\n")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.output_file.write("<returnStatement>\n")
        # prints return
        self.write_cur_token_and_advance()

        if self.tokenizer.get_cur_token() != ";":
            self.compile_expression()

        # prints ;
        self.write_cur_token_and_advance()
        self.output_file.write("</returnStatement>\n")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.output_file.write("<ifStatement>\n")
        # prints if
        self.write_cur_token_and_advance()

        # prints (
        self.write_cur_token_and_advance()

        self.compile_expression()

        # prints )
        self.write_cur_token_and_advance()

        # prints {
        self.write_cur_token_and_advance()

        self.compile_statements()

        # prints }
        self.write_cur_token_and_advance()

        if self.tokenizer.get_cur_token() == "else":
            # prints else
            self.write_cur_token_and_advance()
            # prints {
            self.write_cur_token_and_advance()
            self.compile_statements()
            # prints }
            self.write_cur_token_and_advance()

        self.output_file.write("</ifStatement>\n")

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        self.output_file.write("<expressionList>\n")
        while self.tokenizer.get_cur_token() != ")":
            if self.tokenizer.get_cur_token() == ",":
                # prints ,
                self.write_cur_token_and_advance()
            else:
                self.compile_expression()
        self.output_file.write("</expressionList>\n")

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.output_file.write("<expression>\n")
        self.compile_term()
        while self.tokenizer.get_cur_token() in OP_SET:
            # prints the op
            self.write_cur_token_and_advance()

            self.compile_term()
        self.output_file.write("</expression>\n")

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
        self.output_file.write("<term>\n")

        if self.tokenizer.token_type() == "INT_CONST":
            self.write_cur_token_and_advance()

        elif self.tokenizer.token_type() == "STRING_CONST":
            self.write_cur_token_and_advance()

        elif self.tokenizer.get_cur_token() in KEYWORD_CONSTANT_SET:
            self.write_cur_token_and_advance()

        elif self.tokenizer.get_cur_token() in UNARY_OP_SET:
            self.write_cur_token_and_advance()

            self.compile_term()
        elif self.tokenizer.get_cur_token() == "(":
            # prints (
            self.write_cur_token_and_advance()
            self.compile_expression()
            # prints )
            self.write_cur_token_and_advance()

        elif self.tokenizer.token_type() == "IDENTIFIER":
            self.write_cur_token_and_advance()
            next_token = self.tokenizer.get_cur_token()

            if next_token == "[":
                self.write_cur_token_and_advance()
                self.compile_expression()
                # prints ]
                self.write_cur_token_and_advance()

            elif next_token == "(":
                self.write_cur_token_and_advance()
                self.compile_expression_list()
                self.write_cur_token_and_advance()

            elif next_token == ".":
                self.write_cur_token_and_advance()

                # prints subroutineName
                self.write_cur_token_and_advance()

                # prints (
                self.write_cur_token_and_advance()

                self.compile_expression_list()
                # prints )
                self.write_cur_token_and_advance()

        self.output_file.write("</term>\n")

    def write_cur_token_and_advance(self):
        """"this method writes the current token in the format <token_type>
        token </token_type> and advance the tokenizer."""

        if self.tokenizer.token_type() == "INT_CONST":
            self.output_file.write(f'<integerConstant> '
                                   f'{self.tokenizer.get_cur_token()}'
                                   f' </integerConstant>\n')
            if self.tokenizer.has_more_tokens():
                self.tokenizer.advance()
            return

        if self.tokenizer.token_type() == "STRING_CONST":
            self.output_file.write(
                "<stringConstant> " + self.tokenizer.string_val() +
                " </stringConstant>\n")
            if self.tokenizer.has_more_tokens():
                self.tokenizer.advance()
            return

        cur_token = self.tokenizer.get_cur_token()
        if self.tokenizer.get_cur_token() in SPECIAL_SYMBOLS:
            cur_token = SPECIAL_SYMBOLS[self.tokenizer.get_cur_token()]

        self.output_file.write(f'<{self.tokenizer.token_type().lower()}> '
                               f'{cur_token} <'
                               f'/{self.tokenizer.token_type().lower()}>\n')
        if self.tokenizer.has_more_tokens():
            self.tokenizer.advance()
