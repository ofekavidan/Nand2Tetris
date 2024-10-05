"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

""" constatnts: """
SP = 0
LCL = 1
ARG = 2
POINTER = 3
THIS = 3
THAT = 4
TEMP = 5
STATIC = 16

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
PUSH_COMMAND = "C_PUSH"
POP_COMMAND = "C_POP"
CONSTANT_SEGMENT = "constant"
STATIC_SEGMENT = "static"
POINTER_SEGMENT = "pointer"
TEMP_SEGMENT = "temp"
LOCAL_SEGMENT = "local"
ARGUMENT_SEGMENT = "argument"
THIS_SEGMENT = "this"
THAT_SEGMENT = "that"


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.output_stream = output_stream
        self.counter_labels = 1
        self.public_file_name = ""

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        self.public_file_name = filename

    def write_arithmetic_add_sub(self, command):
        """ This method is called when we want to add or sub numbers from
        the stack. it translates the command: add/sub o asm.
        """
        sign_dict = {ADD_COMMAND: "+", SUB_COMMAND: "-"}

        self.output_stream.write("@SP\n")
        self.output_stream.write("M = M - 1\n")
        self.output_stream.write("A = M\n")
        self.output_stream.write("D = M\n")
        self.output_stream.write("@SP\n")
        self.output_stream.write("M = M - 1\n")
        self.output_stream.write("A = M\n")
        self.output_stream.write(f'M= M {sign_dict[command]}D\n')
        self.output_stream.write("@SP\n")
        self.output_stream.write("M = M + 1\n")

    def write_gt_labels(self):
        """ This method is called from the write_gt method. It writes all the
         labels of gt.
         """
        self.output_stream.write(f'(ifsamesign{self.counter_labels})\n')
        self.output_stream.write("@SP\n")
        self.output_stream.write("M = M - 1\n")  # hold &y
        self.output_stream.write("A = M\n")  # @M ===> @Y
        self.output_stream.write("D = M\n")  # D = Y
        self.output_stream.write("@SP\n")
        self.output_stream.write("M = M - 1\n")
        self.output_stream.write("A = M\n")  # @X
        self.output_stream.write("D = D - M\n")  # D = Y - X
        self.output_stream.write(f'@IFGT{self.counter_labels}\n')
        self.output_stream.write("D;JLT\n")
        self.output_stream.write(f'@IFNOTGT{self.counter_labels}\n')
        self.output_stream.write("0;JMP\n")

        self.output_stream.write(f'(IFGT{self.counter_labels})\n')
        self.output_stream.write("@SP\n")
        self.output_stream.write("A = M\n")  # goto X
        self.output_stream.write("M = -1\n")  # x =-1
        self.output_stream.write("@SP\n")
        self.output_stream.write("M = M + 1\n")
        self.output_stream.write(f'@GTEND{self.counter_labels}\n')
        self.output_stream.write("0;JMP\n")

        self.output_stream.write(f'(IFNOTGT{self.counter_labels})\n')
        self.output_stream.write("@SP\n")

        self.output_stream.write("A = M\n")  # goto x
        self.output_stream.write("M = 0\n")  # x=0
        self.output_stream.write("@SP\n")
        self.output_stream.write("M = M + 1\n")

        self.output_stream.write(f'(GTEND{self.counter_labels})\n')
        self.counter_labels += 1

    def write_gt_y_pos(self):
        """this method is called from the write_gt method. it handles the
        case where y is positive."""
        # y >= 0
        self.output_stream.write(f'(ifypos{self.counter_labels})\n')
        self.output_stream.write("@SP\n")
        self.output_stream.write("M = M - 1\n")
        self.output_stream.write("A = M\n")  # @X
        self.output_stream.write("D = M\n")  # D = X
        # now check x
        # if x < 0, so they don't have the same sign
        self.output_stream.write(f'@IFNOTGT{self.counter_labels}\n')
        self.output_stream.write("D;JLT\n")

        self.output_stream.write("@SP\n")
        self.output_stream.write("M = M + 1\n")
        self.output_stream.write("M = M + 1\n")
        self.output_stream.write(f'@ifsamesign{self.counter_labels}\n')
        # x >= 0
        self.output_stream.write("D;JGE\n")

    def write_gt_y_neg(self):
        """ this method is called from the write_gt method. it handles the
        case where y is negative.
        """
        # y < 0
        # now check if x is pos (y < 0 and x >= 0, so true)
        self.output_stream.write(f'(ifyneg{self.counter_labels})\n')
        self.output_stream.write("@SP\n")
        self.output_stream.write("M = M - 1\n")  # hold &x
        self.output_stream.write("A = M\n")  # @X
        self.output_stream.write("D = M\n")  # D = X
        self.output_stream.write(f'@IFGT{self.counter_labels}\n')
        self.output_stream.write("D;JGE\n")  # y < 0 and x >= 0, so true

        self.output_stream.write("@SP\n")
        self.output_stream.write("M = M + 1\n")
        self.output_stream.write("M = M + 1\n")
        # y < 0 and x < 0
        self.output_stream.write(f'@ifsamesign{self.counter_labels}\n')
        self.output_stream.write("0;JMP\n")

    def write_gt(self):
        """ This method is called when we got the command gt."""
        self.output_stream.write("@SP\n")
        self.output_stream.write("M = M - 1\n")  # hold &y
        self.output_stream.write("A = M\n")  # @M ===> @Y
        self.output_stream.write("D = M\n")  # D = Y

        self.output_stream.write(f'@ifyneg{self.counter_labels}\n')
        self.output_stream.write("D;JLT\n")
        self.output_stream.write(f'@ifypos{self.counter_labels}\n')  # y>=0
        self.output_stream.write("D;JGE\n")

        self.write_gt_y_neg()
        self.write_gt_y_pos()
        self.write_gt_labels()

    def swap_x_y(self):
        """ this method swaps x and y in the stack."""
        self.output_stream.write("@SP\n")
        self.output_stream.write("M=M-1\n")
        self.output_stream.write("M=M-1\n")
        self.output_stream.write("A=M\n")
        self.output_stream.write("D=M\n")  # D=X
        self.output_stream.write("@SP\n")
        self.output_stream.write("M=M+1\n")
        self.output_stream.write("M=M+1\n")
        self.output_stream.write("A=M\n")
        self.output_stream.write("M=D\n")  # SP=X

        self.output_stream.write("@SP\n")
        self.output_stream.write("M=M-1\n")
        self.output_stream.write("A=M\n")
        self.output_stream.write("D=M\n")  # D=Y

        self.output_stream.write("@SP\n")
        self.output_stream.write("M=M-1\n")
        self.output_stream.write("A=M\n")
        self.output_stream.write("M=D\n")  # Y IN X

        self.output_stream.write("@SP\n")
        self.output_stream.write("M=M+1\n")
        self.output_stream.write("M=M+1\n")
        self.output_stream.write("A=M\n")
        self.output_stream.write("D=M\n")  # D=X

        self.output_stream.write("@SP\n")
        self.output_stream.write("M=M-1\n")
        self.output_stream.write("A=M\n")
        self.output_stream.write("M=D\n")  # X IN Y
        self.output_stream.write("@SP\n")
        self.output_stream.write("M=M+1\n")

    def write_eq(self):
        """ this method translates the command eq to asm."""
        self.output_stream.write("@SP\n")
        self.output_stream.write("M = M - 1\n")  # hold &y
        self.output_stream.write("A = M\n")  # @M ===> @Y
        self.output_stream.write("D = M\n")  # D = Y
        self.output_stream.write("@SP\n")
        self.output_stream.write("M = M - 1\n")

        self.output_stream.write("A = M\n")  # @X
        self.output_stream.write("D = D - M\n")  # D = Y - X
        self.output_stream.write(f'@IFEQ{self.counter_labels}\n')
        self.output_stream.write("D;JEQ\n")
        self.output_stream.write(f'@IFNOTEQ{self.counter_labels}\n')
        self.output_stream.write("0;JMP\n")

        self.output_stream.write(f'(IFEQ{self.counter_labels})\n')
        self.output_stream.write("@SP\n")
        self.output_stream.write("A = M\n")  # goto x
        self.output_stream.write("M = -1\n")  # x=-1
        self.output_stream.write("@SP\n")
        self.output_stream.write("M = M + 1\n")
        self.output_stream.write(f'@EQEND{self.counter_labels}\n')
        self.output_stream.write("0;JMP\n")

        self.output_stream.write(f'(IFNOTEQ{self.counter_labels})\n')
        self.output_stream.write("@SP\n")
        self.output_stream.write("A = M\n")  # goto x
        self.output_stream.write("M = 0\n")  # x=0
        self.output_stream.write("@SP\n")
        self.output_stream.write("M = M + 1\n")

        self.output_stream.write(f'(EQEND{self.counter_labels})\n')

        self.counter_labels += 1

    def write_and_or(self, command):
        """ This method translates the command and/or to asm """
        command_dict = {AND_COMMAND: "&", OR_COMMAND: "|"}

        self.output_stream.write("@SP\n")
        self.output_stream.write("AM=M-1\n")
        self.output_stream.write("D=M\n")
        self.output_stream.write("A=A-1\n")
        self.output_stream.write(f'M=M{command_dict[command]}D\n')

    def write_shifts(self, command):
        """ this method translates the command shiftleft, shiftright to asm"""
        command_dict = {SHIFT_LEFT_COMMAND: "<<", SHIFT_RIGHT_COMMAND: ">>"}
        self.output_stream.write("@SP\n")
        self.output_stream.write("AM=M-1\n")
        self.output_stream.write(f'M = M{command_dict[command]}\n')

    def write_neg(self):
        """ this method translates the command neg to asm"""
        self.output_stream.write("@SP\n")
        self.output_stream.write("A = M - 1\n")
        self.output_stream.write("M = - M\n")

    def write_not(self):
        """ this method translates the command not to asm """
        self.output_stream.write("@SP\n")
        self.output_stream.write("A = M - 1\n")  # hold &y
        self.output_stream.write("M = !M\n")  # @M ===> @Y

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given 
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """

        if command == ADD_COMMAND or command == SUB_COMMAND:
            self.write_arithmetic_add_sub(command)

        elif command == NEG_COMMAND:
            self.write_neg()

        elif command == EQ_COMMAND:
            self.write_eq()

        elif command == GT_COMMAND:
            self.write_gt()

        elif command == LT_COMMAND:
            self.swap_x_y()
            self.write_gt()

        elif command == AND_COMMAND or command == OR_COMMAND:
            self.write_and_or(command)

        elif command == SHIFT_LEFT_COMMAND or command == SHIFT_RIGHT_COMMAND:
            self.write_shifts(command)

        elif command == NOT_COMMAND:
            self.write_not()

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given 
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        if command == PUSH_COMMAND:
            if segment == CONSTANT_SEGMENT:
                self.write_push_constant(index)

            if segment == STATIC_SEGMENT or segment == POINTER_SEGMENT or \
                    segment == TEMP_SEGMENT:
                self.write_push_static_pointer_temp(segment, index)

            if segment == LOCAL_SEGMENT or segment == ARGUMENT_SEGMENT or \
                    segment == THIS_SEGMENT or segment == THAT_SEGMENT:
                self.write_push_local_arg_this_that(segment, index)

        if command == POP_COMMAND:
            if segment == STATIC_SEGMENT or segment == POINTER_SEGMENT or \
                    segment == TEMP_SEGMENT:
                self.write_pop_static_pointer_temp(segment, index)

            if segment == LOCAL_SEGMENT or segment == ARGUMENT_SEGMENT or \
                    segment == THIS_SEGMENT or segment == THAT_SEGMENT:
                self.write_pop_local_arg_this_that(segment, index)

    def write_push_constant(self, index):
        """ This method is called when we want to push constant to the
        stack. It translate the command: push constant index to asm.
        """
        self.output_stream.write(f'@{index}\n')
        self.output_stream.write("D=A\n")
        self.output_stream.write("@SP\n")
        self.output_stream.write("A=M\n")
        self.output_stream.write("M=D\n")
        self.output_stream.write("@SP\n")
        self.output_stream.write("M=M+1\n")

    def write_push_static_pointer_temp(self, segment, index):
        """This method is called when we want to push a static, pointer or
        temp to the stack. it translates the command: push static/pointer/temp
        index to asm.
        """
        segment_dict = {STATIC_SEGMENT: f'@{self.public_file_name}.{index}\n',
                        POINTER_SEGMENT: f'@{POINTER + index}\n',
                        TEMP_SEGMENT: f'@{TEMP + index}\n'}

        self.output_stream.write(segment_dict[segment])
        self.output_stream.write("D = M\n")
        self.output_stream.write("@SP\n")
        self.output_stream.write("A=M\n")
        self.output_stream.write("M=D\n")
        self.output_stream.write("@SP\n")
        self.output_stream.write("M=M+1\n")

    def write_push_local_arg_this_that(self, segment, index):
        """This method is called when we want to push a local,arg,this or that
        to the stack. it translates the command push local/arf/this/that
        index to asm.
        """
        segment_dict = {LOCAL_SEGMENT: f'@{LCL}\n',
                        ARGUMENT_SEGMENT: f'@{ARG}\n',
                        THIS_SEGMENT: f'@{THIS}\n',
                        THAT_SEGMENT: f'@{THAT}\n'}

        self.output_stream.write(segment_dict[segment])
        self.output_stream.write("D = M\n")
        self.output_stream.write(f'@{index}\n')
        self.output_stream.write("A= D + A\n")
        self.output_stream.write("D = M\n")
        self.output_stream.write("@SP\n")
        self.output_stream.write("A = M\n")
        self.output_stream.write("M = D\n")
        self.output_stream.write("@SP\n")
        self.output_stream.write("M = M + 1\n")

    def write_pop_static_pointer_temp(self, segment, index):
        """This method is called when we want to pop a static or a pointer or
        temp from the stack. it translates the command pop
        static/pointer/temp index to asm.
        """
        segment_dict = {STATIC_SEGMENT: f'@{self.public_file_name}.{index}\n',
                        POINTER_SEGMENT: f'@{POINTER + index}\n',
                        TEMP_SEGMENT: f'@{TEMP + index}\n'}
        self.output_stream.write("@SP\n")
        self.output_stream.write("M = M - 1\n")
        self.output_stream.write("A = M\n")
        self.output_stream.write("D = M\n")
        self.output_stream.write(segment_dict[segment])
        self.output_stream.write("M=D\n")

    def write_pop_local_arg_this_that(self, segment, index):
        """ This method is called when we want to pop a local,arg,this or that
          from the stack. It translates the command pop
          local/arg/this/that index to asm.
          """
        segment_dict = {LOCAL_SEGMENT: f'@{LCL}\n',
                        ARGUMENT_SEGMENT: f'@{ARG}\n',
                        THIS_SEGMENT: f'@{THIS}\n',
                        THAT_SEGMENT: f'@{THAT}\n'}

        self.output_stream.write(segment_dict[segment])
        self.output_stream.write("D = M\n")
        self.output_stream.write(f'@{index}\n')
        self.output_stream.write("D = D + A\n")
        self.output_stream.write("@SP\n")
        self.output_stream.write("AM = M - 1\n")
        self.output_stream.write("D =D+ M\n")
        self.output_stream.write("M =D- M\n")
        self.output_stream.write("D =D- M\n")
        self.output_stream.write("A = M\n")
        self.output_stream.write("M = D\n")

    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command. 
        Let "Xxx.foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "Xxx.foo" generates and injects the
        symbol "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass

    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass

    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command. 

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass

    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that affects the function command. 
        The handling of each "function Xxx.foo" command within the file Xxx.vm
        generates and injects a symbol "Xxx.foo" into the assembly code stream,
        that labels the entry-point to the function's code.
        In the subsequent assembly process, the assembler translates this 
        symbol into the physical address where the function code starts.

        Args:
            function_name (str): the name of the function.
            n_vars (int): the number of local variables of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "function function_name n_vars" is:
        # (function_name)       // injects a function entry label into the code
        # repeat n_vars times:  // n_vars = number of local variables
        #   push constant 0     // initializes the local variables to 0
        pass

    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command. 
        Let "Xxx.foo" be a function within the file Xxx.vm.
        The handling of each "call" command within Xxx.foo's code generates and
        injects a symbol "Xxx.foo$ret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "Xxx.foo").
        This symbol is used to mark the return address within the caller's 
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.

        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "call function_name n_args" is:
        # push return_address   // generates a label and pushes it to the stack
        # push LCL              // saves LCL of the caller
        # push ARG              // saves ARG of the caller
        # push THIS             // saves THIS of the caller
        # push THAT             // saves THAT of the caller
        # ARG = SP-5-n_args     // repositions ARG
        # LCL = SP              // repositions LCL
        # goto function_name    // transfers control to the callee
        # (return_address)      // injects the return address label into the
        # code
        pass

    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "return" is:
        # frame = LCL                   // frame is a temporary variable
        # return_address = *(frame-5)   // puts the return address in a temp
        # var
        # *ARG = pop()                  // repositions the return value for the
        # caller
        # SP = ARG + 1                  // repositions SP for the caller
        # THAT = *(frame-1)             // restores THAT for the caller
        # THIS = *(frame-2)             // restores THIS for the caller
        # ARG = *(frame-3)              // restores ARG for the caller
        # LCL = *(frame-4)              // restores LCL for the caller
        # goto return_address           // go to the return address
        pass
