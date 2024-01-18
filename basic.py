#######################################
#######################################
# IMPORTS
#######################################
#######################################

# Import to add arrow where error is occured
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
    "te",  # to
    "karya",  # function
    # "chal" # for
    # "step"
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
            # If the input contains digits then let it behave like number
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            # If the input contains alphabets check if it is identifier if yes then let if behave like identifier
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier())
            # TODO Implement comment
            # elif self.current_char == "#":
            # # Skip comments until the end of the line
            #     while self.current_char not in "\n":
            #         self.advance()

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
        self.pos_end = (self.else_case or self.cases[len(self.cases) - 1][0]).pos_end


class WhileNode:
    def __init__(self, condition_node, body_node):
        self.condition_node = condition_node
        self.body_node = body_node

        self.pos_start = self.condition_node.pos_start
        self.pos_end = self.body_node.pos_end


class FuncDefNode:
    def __init__(self, var_name_tok, arg_name_toks, body_node):
        self.var_name_tok = var_name_tok
        self.arg_name_toks = arg_name_toks
        self.body_node = body_node

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
    def advance(
        self,
    ):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def parse(self):
        # Parse an expression and store the result in 'res'
        res = self.expr()
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
        cases = []
        else_case = None

        if not self.current_tok.matches(TT_KEYWORD, "jar"):
            return res.failure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    f"'jar' pahije hote",
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

        expr = res.register(self.expr())
        if res.error:
            return res
        cases.append((condition, expr))

        while self.current_tok.matches(TT_KEYWORD, "nahijar"):
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

            expr = res.register(self.expr())
            if res.error:
                return res
            cases.append((condition, expr))

        if self.current_tok.matches(TT_KEYWORD, "nahitar"):
            res.register_advancement()
            self.advance()

            else_case = res.register(self.expr())
            if res.error:
                return res

        return res.success(IfNode(cases, else_case))

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

        body = res.register(self.expr())
        if res.error:
            return res

        return res.success(WhileNode(condition, body))

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

        if self.current_tok.type != TT_ARROW:
            # after the defionation of function there must be an arrow to to start function body
            return res.failure(
                InvalidSyntaxError(
                    self.current_tok.pos_start,
                    self.current_tok.pos_end,
                    f"'->' pahije hote",
                )
            )

        res.register_advancement()
        self.advance()
        node_to_return = res.register(self.expr())
        if res.error:
            return res

        return res.success(FuncDefNode(var_name_tok, arg_name_toks, node_to_return))

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
        self.value = None
        self.error = None

    def register(self, res):
        #  register the values if there is erro rthen retunrn the error else simply return the value
        if res.error:
            self.error = res.error
        return res.value

    def success(self, value):
        # if no error occured then simply return self by assigning the value to it
        self.value = value
        return self

    def failure(self, error):
        # if there is any error then assign it to the self error and then return self
        self.error = error
        return self


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

    def __repr__(self):
        return str(self.value)


class Function(Value):
    def __init__(self, name, body_node, arg_names):
        super().__init__()
        self.name = name or "<anamit>"
        self.body_node = body_node
        self.arg_names = arg_names

    def execute(self, args):
        res = RTResult()
        interpreter = Interpreter()
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)

        if len(args) > len(self.arg_names):
            return res.failure(
                RTError(
                    self.pos_start,
                    self.pos_end,
                    f"{len(args) - len(self.arg_names)}  mahiti jast zali '{self.name}'",
                    self.context,
                )
            )

        if len(args) < len(self.arg_names):
            return res.failure(
                RTError(
                    self.pos_start,
                    self.pos_end,
                    f"{len(self.arg_names) - len(args)} mahiti kami zali '{self.name}'",
                    self.context,
                )
            )

        for i in range(len(args)):
            arg_name = self.arg_names[i]
            arg_value = args[i]
            arg_value.set_context(new_context)
            new_context.symbol_table.set(arg_name, arg_value)

        value = res.register(interpreter.visit(self.body_node, new_context))
        if res.error:
            return res
        return res.success(value)

    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_names)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<karya {self.name}>"


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

    def no_visit_method(self, node):
        raise Exception(f"No visit_{type(node).__name__} method defined")

    ###################################

    def visit_NumberNode(self, node, context):
        return RTResult().success(
            Number(node.tok.value)
            .set_context(context)
            .set_pos(node.pos_start, node.pos_end)
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
        value = value.copy().set_pos(node.pos_start, node.pos_end)
        return res.success(value)

    def visit_VarAssignNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = res.register(self.visit(node.value_node, context))
        if res.error:
            return res
        # If there isn't any error then grab the symbol table
        context.symbol_table.set(var_name, value)
        return res.success(value)

    def visit_BinOpNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.error:
            return res
        right = res.register(self.visit(node.right_node, context))
        if res.error:
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
        if res.error:
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

        for condition, expr in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.error:
                return res

            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))
                if res.error:
                    return res
                return res.success(expr_value)

        if node.else_case:
            else_value = res.register(self.visit(node.else_case, context))
            if res.error:
                return res
            return res.success(else_value)

        return res.success(None)

    def visit_WhileNode(self, node, context):
        res = RTResult()

        while True:
            condition = res.register(self.visit(node.condition_node, context))
            if res.error:
                return res

            if not condition.is_true():
                break

            res.register(self.visit(node.body_node, context))
            if res.error:
                return res

        return res.success(None)

    def visit_FuncDefNode(self, node, context):
        res = RTResult()

        func_name = node.var_name_tok.value if node.var_name_tok else None
        body_node = node.body_node
        arg_names = [arg_name.value for arg_name in node.arg_name_toks]
        func_value = (
            Function(func_name, body_node, arg_names)
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
        if res.error:
            return res
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        for arg_node in node.arg_nodes:
            args.append(res.register(self.visit(arg_node, context)))
            if res.error:
                return res

        return_value = res.register(value_to_call.execute(args))
        if res.error:
            return res
        return res.success(return_value)


#######################################
#######################################
# RUN
#######################################
#######################################

# global symbol table
global_symbol_table = SymbolTable()
#  no reason
global_symbol_table.set("NULL", Number(0))
global_symbol_table.set("YOGYA", Number(1))
global_symbol_table.set("AYOGYA", Number(0))


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
