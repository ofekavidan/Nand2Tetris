import re

"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

KEYWORD_SET = {"class", "constructor", "function",
               "method", "field", "static", "var", "int",
               "char", "boolean", "void", "true", "false", "null",
               "this", "let", "do", "if", "else", "while", "return"}

SYMBOL_SET = {"{", "}", "(", ")", "[", "]", ".",
              ",", ";", "+", "-", "*", "/", "&", "|", "<",
              ">", "=", "~", "#", "^"}

ESCAPE_SET = {"\\", "\n", "\r", "\t", "\b", "\f"}


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    
    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters, 
    and comments, which are ignored. There are three possible comment formats: 
    /* comment until closing */ , /** API comment until closing */ , and 
    // comment until the line’s end.

    - ‘xxx’: quotes are used for tokens that appear verbatim (‘terminals’).
    - xxx: regular typeface is used for names of language constructs 
           (‘non-terminals’).
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' | 
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate 
    file. A compilation unit is a single class. A class is a sequence of tokens 
    structured according to the following context free syntax:
    
    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) 
    - subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement | 
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' 
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions
    
    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName | 
            varName '['expression']' | subroutineCall | '(' expression ')' | 
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className | 
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'
    
    Note that ^, # correspond to shiftleft and shiftright, respectively.
    """

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        self.input_lines_init = input_stream.read().splitlines()
        self.tokens_arr = []
        self.is_in_comment = False
        for line in self.input_lines_init:
            line = self.delete_comments(line)  # delete comments
            self.fill_tokens_arr(self.tokens_arr, line)  # tokenize
        self.num_tokens = len(self.tokens_arr)
        self.cur_token = 0

    def fill_tokens_arr(self, tokens_arr: list, line: str) -> None:
        """ split the line to tokens, and add to the given tokens_arr """
        word = re.compile('(?!\w)|'.join(KEYWORD_SET) + '(?!\w)' + '|' +
                          '[' + re.escape('|'.join(SYMBOL_SET)) + ']' + '|' +
                          r'\d+' + '|' +
                          r'"[^"\n]*"' + '|' +
                          r'[\w]+')
        tokens_arr += word.findall(line)

    def delete_comments(self, line: str) -> str:
        """ delete the comments from a given line """
        # if line is empty
        if line.isspace() or not line:
            return line
        # if we closing an API comment
        if self.is_in_comment and "*/" in line:
            end_ind = line.find("*/")
            line = line[end_ind + 2:]
            self.is_in_comment = False
        # if we in comment
        if self.is_in_comment:
            return ""
        # clean line from unwanted escape chars
        for e in ESCAPE_SET:
            if (e in line and line[:line.find(e)].count('"') == 2) or \
                    (e in line and '"' not in line) or \
                    (e in line and line.find('"') > line.find(e)):
                line = line.replace(e, " ")
        # if we start an API comment
        while ("/*" in line and '"' not in line) or \
                ("/*" in line and line.find('"') > line.find("/*")):
            start_ind = line.find("/*")
            end_ind = -1
            self.is_in_comment = True
            if "*/" in line:
                end_ind = line.find("*/")
                self.is_in_comment = False
            if end_ind == -1:
                str_replace = line[start_ind:]
            else:
                str_replace = line[start_ind:end_ind + 2]
            line = line.replace(str_replace, "")
        # if we start a regular comment
        while (("//" in line and line[:line.find("//")].count('"') == 2)
               or "//" in line and '"' not in line) or \
                ("//" in line and line.find('"') > line.find("//")):
            start_ind = line.find("//")
            line = line[:start_ind]
            return line

        return line

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        if self.cur_token >= self.num_tokens:
            return False
        return True

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        self.cur_token += 1

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        if self.tokens_arr[self.cur_token] in KEYWORD_SET:
            return "KEYWORD"

        if self.tokens_arr[self.cur_token] in SYMBOL_SET:
            return "SYMBOL"

        if self.tokens_arr[self.cur_token].isnumeric() and \
                0 <= int(self.tokens_arr[self.cur_token]) <= 32767:
            return "INT_CONST"

        if self.tokens_arr[self.cur_token].startswith('"') and \
                self.tokens_arr[self.cur_token].endswith('"') and \
                '"' not in self.tokens_arr[self.cur_token][1:-1] and \
                '\n' not in self.tokens_arr[self.cur_token][1:-1]:
            return "STRING_CONST"

        return "IDENTIFIER"

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        if self.tokens_arr[self.cur_token] in KEYWORD_SET:
            return self.tokens_arr[self.cur_token].upper()
        return ""

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        if self.tokens_arr[self.cur_token] in SYMBOL_SET:
            return self.tokens_arr[self.cur_token]
        return ""

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        return self.tokens_arr[self.cur_token]

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        if self.tokens_arr[self.cur_token].isnumeric() and \
                0 <= int(self.tokens_arr[self.cur_token]) <= 32767:
            return int(self.tokens_arr[self.cur_token])
        return 0

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
        """
        if self.tokens_arr[self.cur_token].startswith('"') and \
                self.tokens_arr[self.cur_token].endswith('"') and \
                '"' not in self.tokens_arr[self.cur_token][1:-1] and \
                '\n' not in self.tokens_arr[self.cur_token][1:-1]:
            return self.tokens_arr[self.cur_token][1:-1]
        return ""

    def get_cur_token(self):
        """ returns the current token """
        return self.tokens_arr[self.cur_token]
