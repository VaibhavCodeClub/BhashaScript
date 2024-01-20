#######################################
#######################################
# IMPORTS
#######################################
#######################################

# Import to add arrow where error is occured
import math
import os
from strings_with_arrows import *

# import to get all the alphabets to recognise identifiers
import string

#######################################
#######################################
# CONSTANTS
#######################################
#######################################

# Digits present in the input
DIGITS = "0123456789"
# all the alphabets are imported
LETTERS = string.ascii_letters
# combined alphabets and digits
LETTERS_DIGITS = LETTERS + DIGITS

#######################################
#######################################
# ERRORS
#######################################
#######################################


# This class will return the error messages for the exceptions occured during executione
class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        # Start positionn of the occurance of the error
        self.pos_start = pos_start
        # Ending of error
        self.pos_end = pos_end
        # Name of the error
        self.error_name = error_name
        # Details of the error
        self.details = details

    def as_string(self):
        # Create the returning result with the combination of error name and the details
        result = f"{self.error_name}: {self.details}\n"
        # Additionaly add the file name and line number of occureance of the error
        result += f"File {self.pos_start.fn}, line {self.pos_start.ln + 1}"
        # Where is error display wit the help of arrows
        result += "\n\n" + string_with_arrows(
            self.pos_start.ftxt, self.pos_start, self.pos_end
        )
        return result


# Implementation of the Illegal Character Error
# If the character from the text is identified as not proper one then this error returns the output
class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "Avaidh Pratik", details)


# Invalid Character error
class ExpectedCharError(Error):
    def __init__(self, pos_start, pos_end, details=""):
        super().__init__(pos_start, pos_end, "Chukiche chinh sapadale", details)


# Invalid Syntax error
class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details=""):
        super().__init__(pos_start, pos_end, "Mandani Avaidh", details)


# Runtime error
# This class is able to handle runtime errors like "divide by zero"
class RTError(Error):
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start, pos_end, "Truti", details)
        self.context = context

    def as_string(self):
        result = self.generate_traceback()
        # Create the returning result with the combination of error name and the details
        result += f"{self.error_name}: {self.details}"
        # Add arrow to that specific error
        result += "\n\n" + string_with_arrows(
            self.pos_start.ftxt, self.pos_start, self.pos_end
        )
        return result

    def generate_traceback(self):
        result = ""
        pos = self.pos_start
        ctx = self.context

        while ctx:
            # Marathi translation of File name and line number of occurance of the error
            result = (
                f"  Dastavej {pos.fn}, rang {str(pos.ln + 1)}, in {ctx.display_name}\n"
                + result
            )
            pos = ctx.parent_entry_pos
            ctx = ctx.parent

        # Traceback (most recent call last)
        result = "Magova (Kahitari chukale):\n" + result
        return result


#######################################
#######################################
# POSITION
#######################################
#######################################


# To keep the track of line and character / col number of current index
class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        # To keep track of the index (No of the character in the sequence)
        self.idx = idx
        # To keep the track of the line
        self.ln = ln
        # To keep the track of the column
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    # Advance method to go to next char and keep the track
    def advance(self, current_char=None):
        # Increase index and column count for each next character
        self.idx += 1
        self.col += 1
        # If the next character is \n (the implementation of next line) then reset column count and add 1 in line count
        if current_char == "\n":
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)


#######################################
#######################################
# TOKENS
#######################################
#######################################

# TT stands for Token Type
TT_INT = "SANKHYA"  # To store values like 10
TT_FLOAT = "DASHANK"  # To store values like 1.8
TT_STRING = "SHABDA"
TT_IDENTIFIER = "OLAKH"  # variable declaration
TT_KEYWORD = "SANKET"  # To recognize keywords like loops
TT_PLUS = "ADHIK"  # To perform addition '+'
TT_MINUS = "VAJA"  # To perform subtraction '-'
TT_MUL = "GUNAKAR"  # To perform multiplication '*'
TT_DIV = "BHAG"  # To perform division '/'
TT_MOD = "BAKI"  # To perform modulus '%'
TT_POW = "GHAT"  # To perform power operation '^'
TT_EQ = "BAROBAR"  # equals '='
TT_EE = "SAMAN"  # equal to '=='
TT_NE = "ASAMAN"  # not equal to '!='
TT_GT = "JADA"  # greater than '>'
TT_LT = "KAMI"  # less than '<'
TT_LTE = "KAMI_SAMAN"  # less than equal to '<='
TT_GTE = "JADA_SAMAN"  # greater than equal to '>='
TT_LPAREN = "DAVA"  # Opening parenthesis '('
TT_RPAREN = "UJAVA"  # Closing parenthesis ')'
TT_COMMA = "SWALPA"  # For comma ','
TT_ARROW = "BAN"  # for '->'
TT_NEWLINE = "PUDH"  # newline
TT_EOF = "SHEVAT"  # End Of File


# 'var a = 10' to be written as 'he a = 10'
KEYWORDS = [
    "he",  # var - the declaration of 'var' im marathi 'he bagh' abbrevation
    "ani",  # and
    "kinva",  # or
    "na",  # not
    "jar",  # if
    "tar",  # then
    "nahijar",  # elif
    "nahitar",  # else
    "jowar",  # while
    "karya",  # function
    "thamb",  # end
    "parat",  # return
    "tod",  # break
    "chal",  # continue
]


class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        # Initialize a new Token with the provided type, value, and position information.
        self.type = type_
        self.value = value

        # If starting position is provided, set pos_start and pos_end accordingly.
        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            # Advance the ending position by one character.
            self.pos_end.advance()

        # If ending position is provided, set pos_end accordingly.
        if pos_end:
            self.pos_end = pos_end.copy()

    def matches(self, type_, value):
        # Check if the token matches the specified type and value.
        return self.type == type_ and self.value == value

    def __repr__(self):
        # Return a string representation of the Token for debugging purposes.
        if self.value:
            return f"{self.type}:{self.value}"
        return f"{self.type}"


#######################################
#######################################
# LEXER
#######################################
#######################################


# a class responsible for breaking down the source code into a stream of tokens


class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        # Extract the text
        self.text = text
        # Initial position of cursor
        self.pos = Position(-1, 0, -1, fn, text)
        # Set empty first char
        self.current_char = None
        # Calling the advance function
        self.advance()

    def advance(self):
        # Advace function is used to change cursor forward by one character
        self.pos.advance(self.current_char)
        # Avoid going beyond the text size
        self.current_char = (
            self.text[self.pos.idx] if self.pos.idx < len(self.text) else None
        )

    def make_tokens(self):
        tokens = []

        while self.current_char != None:
            # If there is space or tab skip that thing
            if self.current_char in " \t":
                self.advance()

            elif self.current_char == "#":
                self.skip_comment()
            elif self.current_char in ";\n":
                tokens.append(Token(TT_NEWLINE, pos_start=self.pos))
                self.advance()
            # If the input contains digits then let it behave like number
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            # If the input contains alphabets check if it is identifier if yes then let if behave like identifier
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier())
            # if there exists double quotation then it must be the string
            elif self.current_char == '"':
                tokens.append(self.make_string())

            #  All the arithmetic operations and parenthesis are implemented here
            elif self.current_char == "+":
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == "-":
                tokens.append(self.make_minus_or_arrow())
            elif self.current_char == "*":
                tokens.append(Token(TT_MUL, pos_start=self.pos))
                self.advance()
            elif self.current_char == "/":
                tokens.append(Token(TT_DIV, pos_start=self.pos))
                self.advance()
            elif self.current_char == "%":
                tokens.append(Token(TT_MOD, pos_start=self.pos))
                self.advance()
            elif self.current_char == "^":
                tokens.append(Token(TT_POW, pos_start=self.pos))
                self.advance()
            elif self.current_char == "(":
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ")":
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == "!":
                token, error = self.make_not_equals()
                if error:
                    return [], error
                tokens.append(token)
            elif self.current_char == "=":
                tokens.append(self.make_equals())
            elif self.current_char == "<":
                tokens.append(self.make_less_than())
            elif self.current_char == ">":
                tokens.append(self.make_greater_than())
            elif self.current_char == ",":
                tokens.append(Token(TT_COMMA, pos_start=self.pos))
                self.advance()
            else:
                # If the character is not either digit or arithmetic operator throw an error
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None

    # Function to return if the number from input is Float (Dashank) of Integer (Sankhya/Purnank)
    def make_number(self):
        num_str = ""
        # Dot count if 0 then Sankhya if 1 then Dashank else invalid one
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in DIGITS + ".":
            if self.current_char == ".":
                # If the current number is . then do
                if dot_count == 1:
                    # If the . count is already one then break as more than one dot count is illegal
                    break
                # Else if 0 then make it one as it may be Dashank
                dot_count += 1
                # Append that dot to the number string
            #     num_str += "."
            # else:
            # If there is no dot then simply append that digit to the number string
            num_str += self.current_char
            self.advance()

        if dot_count == 0:
            # If dot count is one then return Int i.e. Sankhya
            return Token(TT_INT, int(num_str), pos_start, self.pos)
        else:
            # If dot count is one then Dashank
            return Token(TT_FLOAT, float(num_str), pos_start, self.pos)

    def make_string(self):
        # initialisation of string value
        string = ""
        pos_start = self.pos.copy()
        escape_character = False
        self.advance()

        escape_characters = {"n": "\n", "t": "\t"}

        while self.current_char != None and (
            # loop until the end of string
            self.current_char != '"'
            or escape_character
        ):
            if escape_character:
                string += escape_characters.get(self.current_char, self.current_char)
            else:
                if self.current_char == "\\":
                    # escape character
                    escape_character = True
                else:
                    # append the next character
                    string += self.current_char
            self.advance()

            # reset the escape charcter
            escape_character = False

        self.advance()
        # return the token type string with the value
        return Token(TT_STRING, string, pos_start, self.pos)

    def make_identifier(self):
        # Initialize an empty string to store the identifier.
        id_str = ""
        # Copy the starting position for the identifier.
        pos_start = self.pos.copy()

        # Loop until the current character is not None and is a letter, digit, or underscore.
        while self.current_char != None and self.current_char in LETTERS_DIGITS + "_":
            # Add the current character to the identifier string.
            id_str += self.current_char
            # Move to the next character.
            self.advance()

        # Determine the token type based on whether the identifier is a keyword or a general identifier.
        tok_type = TT_KEYWORD if id_str in KEYWORDS else TT_IDENTIFIER
        # Create a Token instance with the determined type, identifier string, and position information.
        return Token(tok_type, id_str, pos_start, self.pos)

    def make_minus_or_arrow(self):
        tok_type = TT_MINUS
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == ">":
            self.advance()
            tok_type = TT_ARROW

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_not_equals(self):
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == "=":
            self.advance()
            return Token(TT_NE, pos_start=pos_start, pos_end=self.pos), None
        self.advance()
        return None, ExpectedCharError(
            pos_start, self.pos, "'!' chya nantar '=' pahije"
        )

    def make_equals(self):
        tok_type = TT_EQ
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == "=":
            self.advance()
            tok_type = TT_EE

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_less_than(self):
        tok_type = TT_LT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == "=":
            self.advance()
            tok_type = TT_LTE

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_greater_than(self):
        tok_type = TT_GT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == "=":
            self.advance()
            tok_type = TT_GTE

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def skip_comment(self):
        self.advance()

        while self.current_char != "\n" and self.current_char is not None:
            self.advance()

        if self.current_char == "\n":
            self.advance()



#######################################
#######################################
# NODES
#######################################
#######################################


# If there is number at the node then
class NumberNode:
    def __init__(self, tok):
        self.tok = tok
        # Retrive all the information related to that node
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        # return the its original value back
        return f"{self.tok}"


class StringNode:
    def __init__(self, tok):
        self.tok = tok

        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f"{self.tok}"


class ListNode:
    def __init__(self, element_nodes, pos_start, pos_end):
        self.element_nodes = element_nodes

        self.pos_start = pos_start
        self.pos_end = pos_end


class VarAccessNode:
    def __init__(self, var_name_tok):
        # Initialize a VarAccessNode with the provided variable name token.
        self.var_name_tok = var_name_tok

        # Set the position start and position end based on the variable name token.
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end


class VarAssignNode:
    def __init__(self, var_name_tok, value_node):
        # Initialize a VarAssignNode with the provided variable name token and value node.
        self.var_name_tok = var_name_tok
        self.value_node = value_node

        # Set the position start to the variable name token's position start.
        # Set the position end to the value node's position end.
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.value_node.pos_end


# If the binary operation is being performed then
# Divide that binary node into left and right part
# like 4+4
class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

        # Below lines divides the original binary operation to the new sub-trees hence evrything returns to the NumberNode
        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f"({self.left_node}, {self.op_tok}, {self.right_node})"


# If the unary operation is being performed then
# like -3
class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node

        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        return f"({self.op_tok}, {self.node})"


class IfNode:
    def __init__(self, cases, else_case):
        self.cases = cases
        self.else_case = else_case

        self.pos_start = self.cases[0][0].pos_start
        self.pos_end = (self.else_case or self.cases[len(self.cases) - 1])[0].pos_end


class WhileNode:
    def __init__(self, condition_node, body_node, should_return_null):
        self.condition_node = condition_node
        self.body_node = body_node
        self.should_return_null = should_return_null

        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end


class FuncDefNode:
    def __init__(self, var_name_tok, arg_name_toks, body_node, should_auto_return):
        self.var_name_tok = var_name_tok
        self.arg_name_toks = arg_name_toks
        self.body_node = body_node
        self.should_auto_return = should_auto_return

        if self.var_name_tok:
            self.pos_start = self.var_name_tok.pos_start
        elif len(self.arg_name_toks) > 0:
            self.pos_start = self.arg_name_toks[0].pos_start
        else:
            self.pos_start = self.body_node.pos_start

        self.pos_end = self.body_node.pos_end


class CallNode:
    def __init__(self, node_to_call, arg_nodes):
        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes

        self.pos_start = self.node_to_call.pos_start

        if len(self.arg_nodes) > 0:
            self.pos_end = self.arg_nodes[len(self.arg_nodes) - 1].pos_end
        else:
            self.pos_end = self.node_to_call.pos_end


class ReturnNode:
    def __init__(self, node_to_return, pos_start, pos_end):
        self.node_to_return = node_to_return

        self.pos_start = pos_start
        self.pos_end = pos_end


class ContinueNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end


class BreakNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end


#######################################
#######################################
# PARSE RESULT
#######################################
#######################################


# Class to add errors while parsing the input like InvalidSystaxError
class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.last_registered_advance_count = 0
        self.advance_count = 0
        self.to_reverse_count = 0

    def register_advancement(self):
        self.last_registered_advance_count = 1
        self.advance_count += 1
        # Register everything

    def register(self, res):
        self.last_registered_advance_count = res.advance_count
        self.advance_count += res.advance_count
        # If there occurs an error return as it is
        if res.error:
            self.error = res.error
        return res.node

    def try_register(self, res):
        if res.error:
            self.to_reverse_count = res.advance_count
            return None
        return self.register(res)

    # If parsing suceeds then return what you have created
    def success(self, node):
        self.node = node
        return self

    # If there is error present then throw error as it is
    def failure(self, error):
        if not self.error or self.last_registered_advance_count == 0:
            self.error = error
        return self


#######################################
#######################################
# PARSER
#######################################
#######################################


# The original parse cass which is used to parse all the input taken
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    # Advance function to look at next character from the input text

    def advance(self):
        self.tok_idx += 1
        self.update_current_tok()
        return self.current_tok

    def reverse(self, amount=1):
        self.tok_idx -= amount
        self.update_current_tok()
        return self.current_tok

    def update_current_tok(self):
        if self.tok_idx >= 0 and self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]

    def parse(self):
        # Parse an expression and store the result in 'res'
        res = self.statements()
        # If there is no error and the current token is not EOF, return a failure result with an InvalidSyntaxError
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Ganitiy Chinh Pahije",
                )
            )
        # Return the parsing result 'res'
        return res

    def statements(self):
        res = ParseResult()
        # empty list of statements
        statements = []
        pos_start = self.current_tok.pos_start.copy()

        while self.current_tok.type == TT_NEWLINE:
            #   skip newlines at the start
            res.register_advancement()
            self.advance()

        statement = res.register(self.statement())
        if res.error:
            return res
        # add the very first expression to the expressions list
        statements.append(statement)

        more_statements = True

        while True:
            #   new line count initially 0
            newline_count = 0
            while self.current_tok.type == TT_NEWLINE:
                # Skip the newline
                res.register_advancement()
                self.advance()
                # after every newline "\n" increment the count by 1
                newline_count += 1
            if newline_count == 0:
                more_statements = False

            # if not more statements then break
            if not more_statements:
                break
            statement = res.try_register(self.statement())
            if not statement:
                self.reverse(res.to_reverse_count)
                more_statements = False
                continue
            statements.append(statement)

        return res.success(
            ListNode(statements, pos_start, self.current_tok.pos_end.copy())
        )

    def statement(self):
        res = ParseResult()
        pos_start = self.current_tok.pos_start.copy()

        if self.current_tok.matches(TT_KEYWORD, "parat"):
            res.register_advancement()
            self.advance()

            expr = res.try_register(self.expr())
            if not expr:
                self.reverse(res.to_reverse_count)
            return res.success(
                ReturnNode(expr, pos_start, self.current_tok.pos_start.copy())
            )

        if self.current_tok.matches(TT_KEYWORD, "chal"):
            res.register_advancement()
            self.advance()
            return res.success(
                ContinueNode(pos_start, self.current_tok.pos_start.copy())
            )

        if self.current_tok.matches(TT_KEYWORD, "tod"):
            res.register_advancement()
            self.advance()
            return res.success(BreakNode(pos_start, self.current_tok.pos_start.copy()))

        expr = res.register(self.expr())
        if res.error:
            return res.failure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "chukichi mandani",
                )
            )
        return res.success(expr)

    def expr(self):
        res = ParseResult()

        if self.current_tok.matches(TT_KEYWORD, "he"):
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_IDENTIFIER:
                return res.failure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Olakh Chinh Pahije",
                    )
                )
            var_name = self.current_tok

            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_EQ:
                return res.failure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "'=' Pahije",
                    )
                )

            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res
            return res.success(VarAssignNode(var_name, expr))

        node = res.register(
            self.bin_op(self.comp_expr, ((TT_KEYWORD, "ani"), (TT_KEYWORD, "kinva")))
        )

        if res.error:
            return res.failure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "Ganitiy Chinh kinva 'he' pahije",
                )
            )

        return res.success(node)

    def comp_expr(self):
        res = ParseResult()

        if self.current_tok.matches(TT_KEYWORD, "na"):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()

            node = res.register(self.comp_expr())
            if res.error:
                return res
            return res.success(UnaryOpNode(op_tok, node))

        node = res.register(
            self.bin_op(self.arith_expr, (TT_EE, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE))
        )

        if res.error:
            return res.failure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    "yapaiki ek pahije hote sankhya, olakh chinh, '+', '-', '(' kinva 'na'",
                )
            )

        return res.success(node)

    ###################################

    def arith_expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    # If *,/ or % symbol is there then follow respective manner to perform binary operation
    # term: factor ((GUNAKAR|BHAG|BAKI) factor)*
    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV, TT_MOD))

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS):
            # Implementation to look at the unary operations
            # Unary operation: + or -
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, factor))

        return self.power()

    def power(self):
        return self.bin_op(self.call, (TT_POW,), self.factor)

    def call(self):
        res = ParseResult()
        atom = res.register(self.atom())
        if res.error:
            return res

        # while self.current_tok.type in (TT_LPAREN, TT_COMMA):
        if self.current_tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            arg_nodes = []

            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
            else:
                arg_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(
                        InvalidSyntaxError(
                            self.current_tok.pos_start,
                            self.current_tok.pos_end,
                            "Chukichi mandani",
                        )
                    )
                while self.current_tok.type == TT_COMMA:
                    res.register_advancement()
                    self.advance()
                    arg_nodes.append(res.register(self.expr()))
                    if res.error:
                        return res
                if self.current_tok.type != TT_RPAREN:
                    return res.failure(
                        InvalidSyntaxError(
                            self.current_tok.pos_start,
                            self.current_tok.pos_end,
                            f"',' kinva ')' pahije hote",
                        )
                    )
                res.register_advancement()
                self.advance()
            return res.success(CallNode(atom, arg_nodes))

        return res.success(atom)

    def atom(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_INT, TT_FLOAT):
            # The block to manage int and float values
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))

        elif tok.type == TT_STRING:
            res.register_advancement()
            self.advance()
            return res.success(StringNode(tok))

        elif tok.type == TT_IDENTIFIER:
            # manage identifiers here
            res.register_advancement()
            self.advance()
            return res.success(VarAccessNode(tok))

        # Implementation to handle opening parenthesis (
        elif tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res
            # If respective closing parenthesis found then continue
            # Return the successful parsing signal
            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            # If no closing parenthesis then throw below error
            else:
                return res.failure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Ujava apekshit hota ')'",
                    )
                )
        elif tok.matches(TT_KEYWORD, "jar"):
            if_expr = res.register(self.if_expr())
            if res.error:
                return res
            return res.success(if_expr)

        elif tok.matches(TT_KEYWORD, "jowar"):
            while_expr = res.register(self.while_expr())
            if res.error:
                return res
            return res.success(while_expr)

        elif tok.matches(TT_KEYWORD, "karya"):
            func_def = res.register(self.func_def())
            if res.error:
                return res
            return res.success(func_def)

        return res.failure(
            InvalidSyntaxError(
                tok.pos_start, tok.pos_end, "Sankhya kinva chinh Pahije hot."
            )
        )

    def if_expr(self):
        res = ParseResult()
        all_cases = res.register(self.if_expr_cases("jar"))
        if res.error:
            return res
        cases, else_case = all_cases
        return res.success(IfNode(cases, else_case))

    def if_expr_b(self):
        return self.if_expr_cases("nahijar")

    def if_expr_c(self):
        res = ParseResult()
        else_case = None
        if self.current_tok.matches(TT_KEYWORD, "nahitar"):
            res.register_advancement()
            self.advance()
            if self.current_tok.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()
                statements = res.register(self.statements())
                if res.error:
                    return res
                else_case = (statements, True)
                if self.current_tok.matches(TT_KEYWORD, "thamb"):
                    res.register_advancement()
                    self.advance()
                else:
                    return res.failure(
                        InvalidSyntaxError(
                            self.current_tok.pos_start,
                            self.current_tok.pos_end,
                            "'thamb' pahije hot",
                        )
                    )
            else:
                expr = res.register(self.statement())
                if res.error:
                    return res
                else_case = (expr, False)
        return res.success(else_case)

    def if_expr_b_or_c(self):
        res = ParseResult()
        cases, else_case = [], None
        if self.current_tok.matches(TT_KEYWORD, "nahijar"):
            all_cases = res.register(self.if_expr_b())
            if res.error:
                return res
            cases, else_case = all_cases
        else:
            else_case = res.register(self.if_expr_c())
            if res.error:
                return res

        return res.success((cases, else_case))

    def if_expr_cases(self, case_keyword):
        res = ParseResult()
        cases = []
        else_case = None
        if not self.current_tok.matches(TT_KEYWORD, case_keyword):
            return res.failure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    f"'{case_keyword}' pahije hote",
                )
            )
        res.register_advancement()
        self.advance()
        condition = res.register(self.expr())
        if res.error:
            return res
        if not self.current_tok.matches(TT_KEYWORD, "tar"):
            return res.failure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    f"'tar' pahije hote",
                )
            )
        res.register_advancement()
        self.advance()
        if self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()
            statements = res.register(self.statements())
            if res.error:
                return res
            cases.append((condition, statements, True))
            if self.current_tok.matches(TT_KEYWORD, "shevat"):
                res.register_advancement()
                self.advance()
            else:
                all_cases = res.register(self.if_expr_b_or_c())
                if res.error:
                    return res
                new_cases, else_case = all_cases
                cases.extend(new_cases)
        else:
            expr = res.register(self.statement())
            if res.error:
                return res
            cases.append((condition, expr, False))
            all_cases = res.register(self.if_expr_b_or_c())
            if res.error:
                return res
            new_cases, else_case = all_cases
            cases.extend(new_cases)
        return res.success((cases, else_case))

    def while_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, "jowar"):
            return res.failure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    f"'jowar' pahije hote",
                )
            )

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error:
            return res

        if not self.current_tok.matches(TT_KEYWORD, "tar"):
            return res.failure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    f"'tar' pahije hote",
                )
            )

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

            body = res.register(self.statements())
            if res.error:
                return res

            if not self.current_tok.matches(TT_KEYWORD, "thamb"):
                return res.failure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        f"'thamb' pahije hot",
                    )
                )

            res.register_advancement()
            self.advance()

            return res.success(WhileNode(condition, body, True))

        body = res.register(self.statement())
        if res.error:
            return res

        return res.success(WhileNode(condition, body, False))

    # If + or - symbol is there then follow respective manner
    # expr: term ((ADHIK|VAJA) term)*
    def func_def(self):
        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, "karya"):
            # if no function is found return function not found error
            return res.failure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    f"'karya' pahije hote",
                )
            )

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_IDENTIFIER:
            # If the function has name
            var_name_tok = self.current_tok
            res.register_advancement()
            self.advance()
            if self.current_tok.type != TT_LPAREN:
                # After function name there must be opening parenthesis if not return error
                return res.failure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        f"'(' pahije hota",
                    )
                )
        else:
            var_name_tok = None
            if self.current_tok.type != TT_LPAREN:
                # if no identifier or opening parenthesis is there
                return res.failure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        f"'Olakh Chinh kinva '(' pahije",
                    )
                )

        res.register_advancement()
        self.advance()
        # Store all the argument names create empty list
        arg_name_toks = []

        if self.current_tok.type == TT_IDENTIFIER:
            # store all the identifiers in that list
            arg_name_toks.append(self.current_tok)
            res.register_advancement()
            self.advance()

            while self.current_tok.type == TT_COMMA:
                # If there is comma present just pass it
                res.register_advancement()
                self.advance()

                if self.current_tok.type != TT_IDENTIFIER:
                    # after comma we expect an identifier if not present throw an error
                    return res.failure(
                        InvalidSyntaxError(
                            self.current_tok.pos_start,
                            self.current_tok.pos_end,
                            f"Olakh chinh pahije hote",
                        )
                    )

                # If there is identifier add it to list
                arg_name_toks.append(self.current_tok)
                res.register_advancement()
                self.advance()

            if self.current_tok.type != TT_RPAREN:
                # If there isn't closing parenthesis at the end throw an error
                return res.failure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        f"',' konva ')' pahije hote",
                    )
                )
        else:
            if self.current_tok.type != TT_RPAREN:
                # IF there isn't identifier or closing parenthesis after the opening one
                return res.failure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        f"Olakh chinh kinva ')' pahije hote",
                    )
                )

        res.register_advancement()
        self.advance()

        # after the defionation of function there must be an arrow to to start function body
        if self.current_tok.type == TT_ARROW:
            res.register_advancement()
            self.advance()

            body = res.register(self.expr())
            if res.error:
                return res

            return res.success(FuncDefNode(var_name_tok, arg_name_toks, body, True))

        if self.current_tok.type != TT_NEWLINE:
            return res.failure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    f"'->' kinva 'PUDH' pahije hot",
                )
            )

        res.register_advancement()
        self.advance()

        body = res.register(self.statements())
        if res.error:
            return res

        if not self.current_tok.matches(TT_KEYWORD, "thamb"):
            return res.failure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    f"'thamb' pahije hot",
                )
            )

        res.register_advancement()
        self.advance()

        return res.success(FuncDefNode(var_name_tok, arg_name_toks, body, False))

    ###################################

    def bin_op(self, func, ops, func2=None):
        if func2 == None:
            func2 = func
        # Create a ParseResult object to track the parsing result
        res = ParseResult()
        # Parse the left operand using the provided parsing function 'func'
        left = res.register(func())
        # If there's an error in parsing the left operand, return the error
        if res.error:
            return res

        # Continue parsing while the current token type is one of the specified operators 'ops'
        while (
            self.current_tok.type in ops
            or (self.current_tok.type, self.current_tok.value) in ops
        ):
            # Get the operator token
            op_tok = self.current_tok
            # Advance to the next token
            res.register_advancement()
            self.advance()
            # Parse the right operand using the provided parsing function 'func'
            right = res.register(func2())
            # If there's an error in parsing the right operand, return the error
            if res.error:
                return res
            # Create a BinOpNode with the left operand, operator, and right operand
            left = BinOpNode(left, op_tok, right)

        # Return a successful result with the final parsed expression tree
        return res.success(left)


#######################################
#######################################
# RUNTIME RESULT
#######################################
#######################################


class RTResult:
    def __init__(self):
        #  Initialize the values as None
        self.reset()

    def reset(self):
        self.value = None
        self.error = None
        self.func_return_value = None
        self.loop_should_continue = False
        self.loop_should_break = False

    def register(self, res):
        #  register the values if there is erro rthen retunrn the error else simply return the value
        self.error = res.error
        self.func_return_value = res.func_return_value
        self.loop_should_continue = res.loop_should_continue
        self.loop_should_break = res.loop_should_break
        return res.value

    def success(self, value):
        # if no error occured then simply return self by assigning the value to it
        self.reset()
        self.value = value
        return self

    def success_return(self, value):
        self.reset()
        self.func_return_value = value
        return self

    def success_continue(self):
        self.reset()
        self.loop_should_continue = True
        return self

    def success_break(self):
        self.reset()
        self.loop_should_break = True
        return self

    def failure(self, error):
        # if there is any error then assign it to the self error and then return self
        self.reset()
        self.error = error
        return self

    def should_return(self):
        # Note: this will allow you to continue and break outside the current function
        return (
            self.error
            or self.func_return_value
            or self.loop_should_continue
            or self.loop_should_break
        )


#######################################
#######################################
# VALUES
#######################################
#######################################


class Value:
    def __init__(self):
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def added_to(self, other):
        return None, self.illegal_operation(other)

    def subbed_by(self, other):
        return None, self.illegal_operation(other)

    def multed_by(self, other):
        return None, self.illegal_operation(other)

    def dived_by(self, other):
        return None, self.illegal_operation(other)

    def powed_by(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_eq(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_ne(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_lt(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_gt(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_lte(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_gte(self, other):
        return None, self.illegal_operation(other)

    def anded_by(self, other):
        return None, self.illegal_operation(other)

    def ored_by(self, other):
        return None, self.illegal_operation(other)

    def notted(self):
        return None, self.illegal_operation()

    def execute(self, args):
        return RTResult().failure(self.illegal_operation())

    def copy(self):
        raise Exception("nan")

    def is_true(self):
        return False

    def illegal_operation(self, other=None):
        if not other:
            other = self
        return RTError(self.pos_start, other.pos_end, "Avaidh karya", self.context)


# This class actually takes the input then if there is arithmetic thing the correct result of that operation will be calculated and returned from this class
class Number(Value):
    def __init__(self, value):
        super().__init__()
        # Retrive value from the input
        self.value = value

    #     self.set_pos()
    #     self.set_context()

    # def set_pos(self, pos_start=None, pos_end=None):
    #     # Save the start and end position to local variables
    #     self.pos_start = pos_start
    #     self.pos_end = pos_end
    #     return self

    # def set_context(self, context=None):
    #     # localize the context
    #     self.context = context
    #     return self

    def added_to(self, other):
        # Perform the addition
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None

        else:
            return None, Value.illegal_operation(self, other)

    def subbed_by(self, other):
        # Perform the subtraction
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def multed_by(self, other):
        # Perform the multiplication
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def powed_by(self, other):
        # Perform the power operation
        if isinstance(other, Number):
            return Number(self.value**other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def dived_by(self, other):
        # Perform the division
        if isinstance(other, Number):
            # If the divisor is 0 then return error : Division by 0
            if other.value == 0:
                return None, RTError(
                    other.pos_start, other.pos_end, "Shunya ne bhag", self.context
                )

            return Number(self.value / other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def mod_by(self, other):
        # Perform the Modulus
        if isinstance(other, Number):
            if other.value == 0:
                # If the divisor is 0 then return error : Division by 0
                return None, RTError(
                    other.pos_start, other.pos_end, "Shunya ne bhag", self.context
                )

            return Number(self.value % other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_eq(self, other):
        if isinstance(other, Number):
            return (
                Number(int(self.value == other.value)).set_context(self.context),
                None,
            )
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_ne(self, other):
        if isinstance(other, Number):
            return (
                Number(int(self.value != other.value)).set_context(self.context),
                None,
            )
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_lt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_gt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_lte(self, other):
        if isinstance(other, Number):
            return (
                Number(int(self.value <= other.value)).set_context(self.context),
                None,
            )
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_gte(self, other):
        if isinstance(other, Number):
            return (
                Number(int(self.value >= other.value)).set_context(self.context),
                None,
            )
        else:
            return None, Value.illegal_operation(self, other)

    def anded_by(self, other):
        if isinstance(other, Number):
            return (
                Number(int(self.value and other.value)).set_context(self.context),
                None,
            )
        else:
            return None, Value.illegal_operation(self, other)

    def ored_by(self, other):
        if isinstance(other, Number):
            return (
                Number(int(self.value or other.value)).set_context(self.context),
                None,
            )
        else:
            return None, Value.illegal_operation(self, other)

    def notted(self):
        return Number(1 if self.value == 0 else 0).set_context(self.context), None

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def is_true(self):
        return self.value != 0

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)


Number.nay = Number(0)
Number.ayogya = Number(0)
Number.yogya = Number(1)
Number.pi = Number(math.pi)


class String(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def added_to(self, other):
        # concatenate two strings together
        if isinstance(other, String):
            return String(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def multed_by(self, other):
        # if the string is multiplied by number it will be duplicated
        if isinstance(other, Number):
            return String(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def is_true(self):
        # string if the length is >=1
        return len(self.value) > 0

    def copy(self):
        copy = String(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __str__(self):
        return self.value

    def __repr__(self):
        return f'"{self.value}"'


class List(Value):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements

    def copy(self):
        copy = List(self.elements)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __str__(self):
        return ", ".join([str(x) for x in self.elements])

    def __repr__(self):
        return f'[{", ".join([repr(x) for x in self.elements])}]'


class BaseFunction(Value):
    def __init__(self, name):
        super().__init__()
        self.name = name or "<anamit>"

    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context

    def check_args(self, arg_names, args):
        res = RTResult()

        if len(args) > len(arg_names):
            return res.failure(
                RTError(
                    self.pos_start,
                    self.pos_end,
                    f"{len(args) - len(arg_names)} karyasathi jast mahiti zali {self}",
                    self.context,
                )
            )

        if len(args) < len(arg_names):
            return res.failure(
                RTError(
                    self.pos_start,
                    self.pos_end,
                    f"{len(arg_names) - len(args)} karyasathi mahiti kami padli {self}",
                    self.context,
                )
            )

        return res.success(None)

    def populate_args(self, arg_names, args, exec_ctx):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.set_context(exec_ctx)
            exec_ctx.symbol_table.set(arg_name, arg_value)

    def check_and_populate_args(self, arg_names, args, exec_ctx):
        res = RTResult()
        res.register(self.check_args(arg_names, args))
        if res.should_return():
            return res
        self.populate_args(arg_names, args, exec_ctx)
        return res.success(None)


class Function(BaseFunction):
    def __init__(self, name, body_node, arg_names, should_auto_return):
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names
        self.should_auto_return = should_auto_return

    def execute(self, args):
        res = RTResult()
        interpreter = Interpreter()
        exec_ctx = self.generate_new_context()

        res.register(self.check_and_populate_args(self.arg_names, args, exec_ctx))
        if res.should_return():
            return res

        value = res.register(interpreter.visit(self.body_node, exec_ctx))
        if res.should_return() and res.func_return_value == None:
            return res

        ret_value = (
            (value if self.should_auto_return else None)
            or res.func_return_value
            or Number.nay
        )
        return res.success(ret_value)

    def copy(self):
        copy = Function(
            self.name, self.body_node, self.arg_names, self.should_auto_return
        )
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<karya {self.name}>"


class BuiltInFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)

    def execute(self, args):
        res = RTResult()
        exec_ctx = self.generate_new_context()

        method_name = f"execute_{self.name}"
        method = getattr(self, method_name, self.no_visit_method)

        res.register(self.check_and_populate_args(method.arg_names, args, exec_ctx))
        if res.should_return():
            return res

        return_value = res.register(method(exec_ctx))
        if res.should_return():
            return res
        return res.success(return_value)

    def no_visit_method(self, node, context):
        raise Exception(f"execute_{self.name} karya milale nahi")

    def copy(self):
        copy = BuiltInFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<mul karya {self.name}>"

    #####################################

    def execute_dakhav(self, exec_ctx):
        # output function
        print(str(exec_ctx.symbol_table.get("value")))
        return RTResult().success(Number.nay)

    execute_dakhav.arg_names = ["value"]

    def execute_ghe(self, exec_ctx):
        # Input function
        text = input()
        return RTResult().success(String(text))

    execute_ghe.arg_names = []

    def execute_sankhya_ghe(self, exec_ctx):
        #  take number as input
        while True:
            # loop till the input is number
            text = input()
            try:
                number = int(text)
                break
            except ValueError:
                # if not a number throw an error
                print(f"'{text}' Sankhya pahije. Punha praytna kara!")
        return RTResult().success(Number(number))

    execute_sankhya_ghe.arg_names = []

    def execute_saf(self, exec_ctx):
        # clear the screen
        os.system("cls" if os.name == "nt" else "clear")
        return RTResult().success(Number.nay)

    execute_saf.arg_names = []

    def execute_sankhya_ahe(self, exec_ctx):
        # check if the input is number or not
        is_number = isinstance(exec_ctx.symbol_table.get("value"), Number)
        return RTResult().success(Number.yogya if is_number else Number.ayogya)

    execute_sankhya_ahe.arg_names = ["value"]

    def execute_shabda_ahe(self, exec_ctx):
        # check if the input is string or not
        is_number = isinstance(exec_ctx.symbol_table.get("value"), String)
        return RTResult().success(Number.yogya if is_number else Number.ayogya)

    execute_shabda_ahe.arg_names = ["value"]

    def execute_karya_ahe(self, exec_ctx):
        # check if the input is function or not
        is_number = isinstance(exec_ctx.symbol_table.get("value"), BaseFunction)
        return RTResult().success(Number.yogya if is_number else Number.ayogya)

    execute_karya_ahe.arg_names = ["value"]

    def execute_chalav(self, exec_ctx):
        fn = exec_ctx.symbol_table.get("fn")

        if not isinstance(fn, String):
            return RTResult().failure(
                RTError(
                    self.pos_start,
                    self.pos_end,
                    "dusara Shabda pahije",
                    exec_ctx,
                )
            )

        fn = fn.value

        try:
            with open(fn, "r") as f:
                script = f.read()
        except Exception as e:
            return RTResult().failure(
                RTError(
                    self.pos_start,
                    self.pos_end,
                    f'vachata nahi aale "{fn}"\n' + str(e),
                    exec_ctx,
                )
            )

        _, error = run(fn, script)

        if error:
            return RTResult().failure(
                RTError(
                    self.pos_start,
                    self.pos_end,
                    f'He vachatana chuk sapadali: "{fn}"\n' + error.as_string(),
                    exec_ctx,
                )
            )

        return RTResult().success(Number.nay)

    execute_chalav.arg_names = ["fn"]


BuiltInFunction.dakhav = BuiltInFunction("dakhav")
BuiltInFunction.ghe = BuiltInFunction("ghe")
BuiltInFunction.sankhya_ghe = BuiltInFunction("sankhya_ghe")
BuiltInFunction.saf = BuiltInFunction("saf")
BuiltInFunction.sankhya_ahe = BuiltInFunction("sankhya_ahe")
BuiltInFunction.shabda_ahe = BuiltInFunction("shabda_ahe")
BuiltInFunction.karya_ahe = BuiltInFunction("karya_ahe")
BuiltInFunction.chalav = BuiltInFunction("chalav")


#######################################
#######################################
# CONTEXT
#######################################
#######################################


class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None


#######################################
# SYMBOL TABLE
#######################################


# Keep track of all variable names and their values
# When a fuction is called new symbol table will be created
# symbol table will store all the variables in that function
# when the symbol table is completed thw symbol table will be removed and all the values in it will be stored in parent symbol table which will be recognized as global symbol table


class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def get(self, name):
        value = self.symbols.get(name, None)
        # If the value is None as well has it has parent
        if value == None and self.parent:
            #  Then just return the parent
            return self.parent.get(name)
        #  else return the value
        return value

    def set(self, name, value):
        # set  the symbol name as the value provided
        self.symbols[name] = value

    def remove(self, name):
        # Delete variables from the symbol table
        del self.symbols[name]


#######################################
#######################################
# INTERPRETER
#######################################
#######################################


class Interpreter:
    def visit(self, node, context):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f"No visit_{type(node).__name__} method defined")

    ###################################

    def visit_NumberNode(self, node, context):
        return RTResult().success(
            Number(node.tok.value)
            .set_context(context)
            .set_pos(node.pos_start, node.pos_end)
        )

    def visit_StringNode(self, node, context):
        return RTResult().success(
            String(node.tok.value)
            .set_context(context)
            .set_pos(node.pos_start, node.pos_end)
        )

    def visit_ListNode(self, node, context):
        res = RTResult()
        elements = []

        for element_node in node.element_nodes:
            elements.append(res.register(self.visit(element_node, context)))
            if res.should_return():
                return res

        return res.success(
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_VarAccessNode(self, node, context):
        # runtime result
        res = RTResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)

        if not value:
            return res.failure(
                RTError(
                    node.pos_start, node.pos_end, f"'{var_name}' milale nahi", context
                )
            )
        value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return res.success(value)

    def visit_VarAssignNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = res.register(self.visit(node.value_node, context))
        if res.should_return():
            return res
        # If there isn't any error then grab the symbol table
        context.symbol_table.set(var_name, value)
        return res.success(value)

    def visit_BinOpNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.should_return():
            return res
        right = res.register(self.visit(node.right_node, context))
        if res.should_return():
            return res

        if node.op_tok.type == TT_PLUS:
            result, error = left.added_to(right)
        elif node.op_tok.type == TT_MINUS:
            result, error = left.subbed_by(right)
        elif node.op_tok.type == TT_MUL:
            result, error = left.multed_by(right)
        elif node.op_tok.type == TT_DIV:
            result, error = left.dived_by(right)
        elif node.op_tok.type == TT_MOD:
            result, error = left.mod_by(right)
        elif node.op_tok.type == TT_POW:
            result, error = left.powed_by(right)
        elif node.op_tok.type == TT_EE:
            result, error = left.get_comparison_eq(right)
        elif node.op_tok.type == TT_NE:
            result, error = left.get_comparison_ne(right)
        elif node.op_tok.type == TT_LT:
            result, error = left.get_comparison_lt(right)
        elif node.op_tok.type == TT_GT:
            result, error = left.get_comparison_gt(right)
        elif node.op_tok.type == TT_LTE:
            result, error = left.get_comparison_lte(right)
        elif node.op_tok.type == TT_GTE:
            result, error = left.get_comparison_gte(right)
        elif node.op_tok.matches(TT_KEYWORD, "ani"):
            result, error = left.anded_by(right)
        elif node.op_tok.matches(TT_KEYWORD, "kinva"):
            result, error = left.ored_by(right)

        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

        # return res.failure(
        #     RTError(
        #         node.pos_start,
        #         node.pos_end,
        #         "Invalid operands for binary operation",
        #         context,
        #     )
        # )

    def visit_UnaryOpNode(self, node, context):
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.should_return():
            return res

        error = None

        if node.op_tok.type == TT_MINUS:
            number, error = number.multed_by(Number(-1))
        elif node.op_tok.matches(TT_KEYWORD, "na"):
            number, error = number.notted()

        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))

    def visit_IfNode(self, node, context):
        res = RTResult()

        for condition, expr, should_return_null in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.should_return():
                return res

            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))
                if res.should_return():
                    return res
                return res.success(Number.nay if should_return_null else expr_value)

        if node.else_case:
            expr, should_return_null = node.else_case
            expr_value = res.register(self.visit(expr, context))
            if res.should_return():
                return res
            return res.success(Number.nay if should_return_null else expr_value)

        return res.success(Number.nay)

    def visit_WhileNode(self, node, context):
        res = RTResult()
        elements = []
        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.should_return():
                return res
            if not condition.is_true():
                break
            value = res.register(self.visit(node.body_node, context))

            if (
                res.should_return()
                and res.loop_should_continue == False
                and res.loop_should_break == False
            ):
                return res

            if res.loop_should_continue:
                continue

            if res.loop_should_break:
                break

            elements.append(value)

        return res.success(
            Number.nay
            if node.should_return_null
            else List(elements)
            .set_context(context)
            .set_pos(node.pos_start, node.pos_end)
        )

    def visit_FuncDefNode(self, node, context):
        res = RTResult()

        func_name = node.var_name_tok.value if node.var_name_tok else None
        body_node = node.body_node
        arg_names = [arg_name.value for arg_name in node.arg_name_toks]
        func_value = (
            Function(func_name, body_node, arg_names, node.should_auto_return)
            .set_context(context)
            .set_pos(node.pos_start, node.pos_end)
        )

        if node.var_name_tok:
            context.symbol_table.set(func_name, func_value)

        return res.success(func_value)

    def visit_CallNode(self, node, context):
        res = RTResult()
        args = []

        value_to_call = res.register(self.visit(node.node_to_call, context))
        if res.should_return():
            return res
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        for arg_node in node.arg_nodes:
            args.append(res.register(self.visit(arg_node, context)))
            if res.should_return():
                return res

        return_value = res.register(value_to_call.execute(args))
        if res.should_return():
            return res
        return_value = (
            return_value.copy()
            .set_pos(node.pos_start, node.pos_end)
            .set_context(context)
        )
        return res.success(return_value)

    def visit_ReturnNode(self, node, context):
        res = RTResult()

        if node.node_to_return:
            value = res.register(self.visit(node.node_to_return, context))
            if res.should_return():
                return res
        else:
            value = Number.nay

        return res.success_return(value)

    def visit_ContinueNode(self, node, context):
        return RTResult().success_continue()

    def visit_BreakNode(self, node, context):
        return RTResult().success_break()


#######################################
#######################################
# RUN
#######################################
#######################################

# global symbol table
global_symbol_table = SymbolTable()
#  no reason
global_symbol_table.set("NULL", Number.nay)
global_symbol_table.set("YOGYA", Number.yogya)
global_symbol_table.set("AYOGYA", Number.ayogya)
global_symbol_table.set("PI", Number.pi)
global_symbol_table.set("dakhav", BuiltInFunction.dakhav)
global_symbol_table.set("ghe", BuiltInFunction.ghe)
global_symbol_table.set("sankhya_ghe", BuiltInFunction.sankhya_ghe)
global_symbol_table.set("saf", BuiltInFunction.saf)
global_symbol_table.set("sankhya_ahe", BuiltInFunction.sankhya_ahe)
global_symbol_table.set("shabda_ahe", BuiltInFunction.shabda_ahe)
global_symbol_table.set("karya_ahe", BuiltInFunction.karya_ahe)
global_symbol_table.set("chalav", BuiltInFunction.chalav)


def run(fn, text):
    # Generate tokens
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error:
        return None, error

    # Generate Abstract Syntax Tree AST
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error:
        return None, ast.error

    # run code
    interpreter = Interpreter()
    context = Context("<program>")
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)

    return result.value, result.error
