################################
# CONSTANTS
################################

DIGITS = "0123456789"  # Digits present in the input

################################
# ERRORS
################################


# This class will return the error messages for the exceptions occured during execution
class Error:
    def __init__(self, pos_start, pos_end, err_name, err_details):
        self.err_name = err_name  # Name of the error
        self.err_details = err_details  # Details of the error
        self.pos_start = pos_start  # Start positionn of the occurance of the error
        self.pos_end = pos_end  # Ending of error

    def as_string(self):
        result = f"{self.err_name}: {self.err_details}"  # Create the returning result with the combination of error name and the details
        result += f" in file {self.pos_start.file_name}, in line {self.pos_start.line + 1}"  # Additionaly add the file name and line number of occureance of the error
        return result


# Implementation of the Illegal Character Error
# If the character from the text is identified as not proper one then this error returns the output
class IllegalCharErr(Error):
    def __init__(self, pos_start, pos_end, err_details):
        super().__init__(
            pos_start, pos_end, "Avaidh Pratik", err_details
        )  # Illegal Character error


################################
# POSITION
################################

# To keep the track of line and character / col number of current index


class Position:
    def __init__(self, index, line, col, file_name, file_text):
        self.index = (
            index  # To keep track of the index (No of the character in the sequence)
        )
        self.line = line  # To keep the track of the line
        self.col = col  # To keep the track of the column
        self.file_name = file_name
        self.file_text = file_text

    # Advance method to go to next char and keep the track
    def advance(self, current_char):
        self.index += 1  # Increase index and column count for each next character
        self.col += 1
        if current_char == "\n":
            # If the next character is \n (the implementation of next line) then reset column count and add 1 in line count
            self.line += 1
            self.col = 0
        return self

    def copy(self):
        return Position(self.index, self.line, self.col, self.file_name, self.file_text)


################################
# TOKENS
################################


# TT stands for Token Type

TT_INT = "SANKHYA"  # Integer
TT_FLOAT = "DASHANK"  # Float
TT_PLUS = "ADHIK"  # Addition
TT_MINUS = "KAMI"  # Subtraction # Additionly VAJA can be added here
TT_MUL = "GUNAKAR"  # Multiplication
TT_DIV = "BHAG"  # Division
TT_MOD = "BAKI"  # Modulus
TT_LPREN = "DAVA"  # Left parenthesis
TT_RPREN = "UJAVA"  # Right parenthesis


class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.value:
            return f"{self.type}:{self.value}"
        return f"{self.type}"


##################################
# LEXER
##################################

# a class responsible for breaking down the source code into a stream of tokens


class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text  # Extract the text
        self.pos = Position(-1, 0, -1, fn, text)  # Initial position of cursor
        self.current_char = None  # Set empty first char
        self.advance()  # Calling the advance function

    def advance(self):
        self.pos.advance(self.current_char)
        # Advace function is used to change cursor forward by one character

        self.current_char = (
            self.text[self.pos.index] if self.pos.index < len(self.text) else None
        )  # Avoid going beyond the text size

    def make_tokens(self):
        tokens = []  # Initially token list is empty
        # Manage all the tokens below and if present in the text then add them to the list above named tokens
        while self.current_char != None:
            if self.current_char in " \t":
                # If there is space or tab skip that thing
                self.advance()
            elif self.current_char in DIGITS:
                # If there is digit proceed accordingly
                tokens.append(self.make_number())
            elif self.current_char == "+":
                # Implementation of addition
                tokens.append(Token(TT_PLUS))
                self.advance()
            elif self.current_char == "-":
                # Implementation of subtraction
                tokens.append(Token(TT_MINUS))
                self.advance()
            elif self.current_char == "*":
                # Implementation of multiplication
                tokens.append(Token(TT_MUL))
                self.advance()
            elif self.current_char == "/":
                # Implementation of division
                tokens.append(Token(TT_DIV))
                self.advance()
            elif self.current_char == "%":
                # Implementation of modulus
                tokens.append(Token(TT_MOD))
                self.advance()
            elif self.current_char == "(":
                # Implementation of opening parenthesis
                tokens.append(Token(TT_LPREN))
                self.advance()
            elif self.current_char == ")":
                # Implementation of closing parenthesis
                tokens.append(Token(TT_RPREN))
                self.advance()
            else:
                # If nothing from above characters then return Illegal Character Exception
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharErr(pos_start, self.pos, "'" + char + "'")
        return tokens, None

    def make_number(self):
        # Function to return if the number from input is Float (Dashank) of Integer (Sankhya/Purnank)
        num_str = ""
        dot_count = 0   # Dot count if 0 then Sankhya if 1 then Dashank else invalid one

        while self.current_char != None and self.current_char in DIGITS + ".":
            if self.current_char == ".": 
                # If the current number is . then do
                if dot_count == 1:
                    # If the . cound is already one then break as more than one dot count is illegal
                    break
                dot_count += 1 # Else if 0 then make it one as it may be Dashank
                num_str += "." # Append that dot to the number string
            else:
                num_str += self.current_char # If there is no dot then simply append that digit to the number string
            self.advance()

        if dot_count == 0:
            # If dot count is one then return Int i.e. Sankhya
            return Token(TT_INT, int(num_str))
        else:
            # If dot count is one then Dashank
            return Token(TT_FLOAT, float(num_str))


################################
# RUN
################################


def run(fn, text):
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    return tokens, error
