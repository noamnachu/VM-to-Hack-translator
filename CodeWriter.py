"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        self.output_stream = output_stream
        self.file_name = ""
        self.current_function = ""
        self.arithmetic_counter = 0
        self.call_counter = 0


    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is
        started.

        Args:
            filename (str): The name of the VM file.
        """
        # Your code goes here!
        # This function is useful when translating code that handles the
        # static segment. For example, in order to prevent collisions between two
        # .vm files which push/pop to the static segment, one can use the current
        # file's name in the assembly variable's name and thus differentiate between
        # static variables belonging to different files.
        # To avoid problems with Linux/Windows/MacOS differences with regards
        # to filenames and paths, you are advised to parse the filename in
        # the function "translate_file" in Main.py using python's os library,
        # For example, using code similar to:
        # input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))
        self.file_name = filename

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to  be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """
        aritemetic_dictionary = {
            "add": "@SP\nA=M-1\nD=M\nA=A-1\nD=D+M\nM=D\n@SP\nM=M-1\n",
            "sub": "@SP\nA=M-1\nD=M\nA=A-1\nD=M-D\nM=D\n@SP\nM=M-1\n",
            "neg": "@SP\nA=M-1\nM=-M\n",
            "and": "@SP\nA=M-1\nD=M\nA=A-1\nM=D&M\n@SP\nM=M-1\n",
            "or": "@SP\nA=M-1\nD=M\nA=A-1\nM=D|M\n@SP\nM=M-1\n",
            "not": "@SP\nA=M-1\nM=!M\n",
            "eq": "@SP\nA=M-1\nA=A-1\nD=M\n@_JUMP1\nD;JGE\n@_JUMP2\n0;JMP\n"
                  "(_JUMP1)\n@SP\nA=M-1\nD=M\n@F_JUMP\nD;JGE\n@_FALSE\n0;JMP\n"
                  "(_JUMP2)\n@SP\nA=M-1\nD=M\n@F_JUMP\nD;JLT\n@_FALSE\n0;JMP\n"
                  "(F_JUMP)\n@SP\nA=M-1\nD=M\nA=A-1\nD=M-D\n@_TRUE\nD;JEQ\n"
                  "D=0\n@CONTINUE_\n0;JMP\n(_TRUE)\nD=-1\n@CONTINUE_\n0;JMP\n"
                  "(_FALSE)\nD=0\n@CONTINUE_\n0;JMP\n(CONTINUE_)\n@SP\nA=M-1\n"
                  "A=A-1\nM=D\n@SP\nM=M-1\n",
            "gt": "@SP\nA=M-1\nA=A-1\nD=M\n@_JUMP1\nD;JGE\n@_JUMP2\n0;JMP\n"
                  "(_JUMP1)\n@SP\nA=M-1\nD=M\n@F_JUMP\nD;JGE\n@_TRUE\n0;JMP\n"
                  "(_JUMP2)\n@SP\nA=M-1\nD=M\n@F_JUMP\nD;JLT\n@_FALSE\n0;JMP\n"
                  "(F_JUMP)\n@SP\nA=M-1\nD=M\nA=A-1\nD=M-D\n@_TRUE\nD;JGT\n"
                  "D=0\n@CONTINUE_\n0;JMP\n(_TRUE)\nD=-1\n@CONTINUE_\n0;JMP\n"
                  "(_FALSE)\nD=0\n@CONTINUE_\n0;JMP\n(CONTINUE_)\n@SP\nA=M-1\n"
                  "A=A-1\nM=D\n@SP\nM=M-1\n",
            "lt": "@SP\nA=M-1\nA=A-1\nD=M\n@_JUMP1\nD;JGE\n@_JUMP2\n0;JMP\n"
                  "(_JUMP1)\n@SP\nA=M-1\nD=M\n@F_JUMP\nD;JGE\n@_FALSE\n0;JMP\n"
                  "(_JUMP2)\n@SP\nA=M-1\nD=M\n@F_JUMP\nD;JLT\n@_TRUE\n0;JMP\n"
                  "(F_JUMP)\n@SP\nA=M-1\nD=M\nA=A-1\nD=M-D\n@_TRUE\nD;JLT\n"
                  "D=0\n@CONTINUE_\n0;JMP\n(_TRUE)\nD=-1\n@CONTINUE_\n0;JMP\n"
                  "(_FALSE)\nD=0\n@CONTINUE_\n0;JMP\n(CONTINUE_)\n@SP\nA=M-1\n"
                  "A=A-1\nM=D\n@SP\nM=M-1\n",
            "shiftleft": "@SP\nA=M-1\nM=M<<\n",
            "shiftright": "@SP\nA=M-1\nM=M>>\n"
        }
        output = aritemetic_dictionary[command].replace("_", f"{self.current_function}.{str(self.arithmetic_counter)}")
        self.arithmetic_counter += 1
        self.output_stream.write(output)

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        # Your code goes here!
        # Note: each reference to "static i" appearing in the file Xxx.vm should
        # be translated to the assembly symbol "Xxx.i". In the subsequent
        # assembly process, the Hack assembler will allocate these symbolic
        # variables to the RAM, starting at address 16.

        # PUSH CONST
        if command == "C_PUSH":
            if segment == "constant":
                self.output_stream.write("@" + str(index) + "\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
            elif segment == "local":
                self.output_stream.write("@LCL\nD=M\n@" + str(index) +
                                         "\nD=D+A\nA=D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
            elif segment == "argument":
                self.output_stream.write("@ARG\nD=M\n@" + str(index) +
                                         "\nD=D+A\nA=D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
            elif segment == "this":
                self.output_stream.write("@THIS\nD=M\n@" + str(index) +
                                         "\nD=D+A\nA=D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
            elif segment == "that":
                self.output_stream.write("@THAT\nD=M\n@" + str(index) +
                                         "\nD=D+A\nA=D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
            elif segment == "temp":
                self.output_stream.write("@5\nD=A\n@" + str(index) +
                                         "\nA=D+A\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
            elif segment == "pointer":
                if index == "0":
                    self.output_stream.write("@THIS\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
                elif index == "1":
                    self.output_stream.write("@THAT\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
            elif segment == "static":
                self.output_stream.write("@" + self.file_name + "."
                                         + str(index) + "\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")

        elif command == "C_POP":
            if segment == "local":
                self.output_stream.write("@LCL\nD=M\n@" + str(index) +
                                         "\nD=D+A\n@13\nM=D\n@SP\nA=M-1\nD=M\n@13\nA=M\nM=D\n@SP\nM=M-1\n")
            elif segment == "argument":
                self.output_stream.write("@ARG\nD=M\n@" + str(index) +
                                         "\nD=D+A\n@13\nM=D\n@SP\nA=M-1\nD=M\n@13\nA=M\nM=D\n@SP\nM=M-1\n")
            elif segment == "this":
                self.output_stream.write("@THIS\nD=M\n@" + str(index) +
                                         "\nD=D+A\n@13\nM=D\n@SP\nA=M-1\nD=M\n@13\nA=M\nM=D\n@SP\nM=M-1\n")
            elif segment == "that":
                self.output_stream.write("@THAT\nD=M\n@" + str(index) +
                                         "\nD=D+A\n@13\nM=D\n@SP\nA=M-1\nD=M\n@13\nA=M\nM=D\n@SP\nM=M-1\n")
            elif segment == "temp":
                self.output_stream.write("@5\nD=A\n@" + str(index) +
                                         "\nD=D+A\n@13\nM=D\n@SP\nA=M-1\nD=M\n@13\nA=M\nM=D\n@SP\nM=M-1\n")
            elif segment == "pointer":
                if index == "0":
                    self.output_stream.write("@SP\nA=M-1\nD=M\n@THIS\nM=D\n"
                                             "@SP\nM=M-1\n")
                elif index == "1":
                    self.output_stream.write("@SP\nA=M-1\nD=M\n@THAT\nM=D\n"
                                             "@SP\nM=M-1\n")
            elif segment == "static":
                self.output_stream.write("@SP\nA=M-1\nD=M\n"
                                         "@" + self.file_name + "." + str(index) + "\nM=D\n@SP\nM=M-1\n")

    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command.
        Let "Xxx.foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "Xxx.foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        self.output_stream.write(f"({self.current_function}${label})\n")

    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        self.output_stream.write(
            f"@{self.current_function}${label}\n0;JMP\n")

    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command.

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!

        # push the condition value from stack is needed??

        self.output_stream.write(f"@SP\nAM=M-1\nD=M\n")
        self.output_stream.write(f"@{self.current_function}${label}\n")
        self.output_stream.write("D;JNE\n")

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
        self.current_function = function_name
        self.output_stream.write(f"({function_name})\n")
        for i in range(n_vars):
            self.output_stream.write("@SP\nA=M\nM=0\n@SP\nM=M+1\n")

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
        # (return_address)      // injects the return address label into the code

        self.output_stream.write(f"@{self.current_function}$ret.{str(self.call_counter)}\n")
        self.output_stream.write("D=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
                                 "@LCL\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
                                 "@ARG\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
                                 "@THIS\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
                                 "@THAT\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
                                 "@SP\nD=M\n@" + str(n_args) + "\nD=D-A\n@5\nD=D-A\n@ARG\nM=D\n"
                                                               "@SP\nD=M\n@LCL\nM=D\n@" + function_name +
                                 "\n0;JMP\n" + "("+self.current_function+"$ret." + str(self.call_counter) + ")\n")
        self.call_counter += 1

    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "return" is:
        # frame = LCL                   // frame is a temporary variable
        # return_address = *(frame-5)   // puts the return address in a temp var
        # *ARG = pop()                  // repositions the return value for the caller
        # SP = ARG + 1                  // repositions SP for the caller
        # THAT = *(frame-1)             // restores THAT for the caller
        # THIS = *(frame-2)             // restores THIS for the caller
        # ARG = *(frame-3)              // restores ARG for the caller
        # LCL = *(frame-4)              // restores LCL for the caller
        # goto return_address           // go to the return address
        self.output_stream.write("@LCL\nD=M\n@R13\nM=D\n"                
                                 "@R13\nD=M\n@5\nA=D-A\nD=M\n@R14\nM=D\n"
                                 "@SP\nA=M-1\nD=M\n@ARG\nA=M\nM=D\n"
                                 "@ARG\nD=M+1\n@SP\nM=D\n"
                                 "@R13\nD=M\n@1\nD=D-A\nA=D\nD=M\n@THAT\nM=D\n"
                                 "@R13\nD=M\n@2\nD=D-A\nA=D\nD=M\n@THIS\nM=D\n"
                                 "@R13\nD=M\n@3\nD=D-A\nA=D\nD=M\n@ARG\nM=D\n"
                                 "@R13\nD=M\n@4\nD=D-A\nA=D\nD=M\n@LCL\nM=D\n"
                                 "@R14\nA=M\n0;JMP\n")

    def bootstrap(self):
        self.output_stream.write("@256\nD=A\n@SP\nM=D\n")
        self.write_call("Sys.init", 0)
