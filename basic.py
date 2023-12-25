#######################################
#######################################
# IMPORTS
#######################################
#######################################

from strings_with_arrows import *

#######################################
#######################################
# CONSTANTS
#######################################
#######################################

# Digits present in the input
DIGITS = "0123456789"

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
            # Marathi translation of File name and line number of occurance o f the error
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
TT_PLUS = "ADHIK"  # TO perform addition '+'
TT_MINUS = "KAMI"  # TO perform subtraction '-'
TT_MUL = "GUNAKAR"  # TO perform multiplication '*'
TT_DIV = "BHAG"  # TO perform division '/'
TT_MOD = "BAKI"  # TO perform modulus '%'
TT_LPAREN = "DAVA"  # Opening parenthesis '('
TT_RPAREN = "UJAVA"  # Closing parenthesis ')'
TT_EOF = "SHEVAT"  # End Of File


class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end

    def __repr__(self):
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
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            # TODO
            # elif self.current_char == "#":
            # # Skip comments until the end of the line
            #     while self.current_char not in "\n":
            #         self.advance()
            elif self.current_char == "+":
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == "-":
                tokens.append(Token(TT_MINUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == "*":
                tokens.append(Token(TT_MUL, pos_start=self.pos))
                self.advance()
            elif self.current_char == "/":
                tokens.append(Token(TT_DIV, pos_start=self.pos))
                self.advance()
            elif self.current_char == "%":
                tokens.append(Token(TT_MOD, pos_start=self.pos))
                self.advance()
            elif self.current_char == "(":
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ")":
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
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
                num_str += "."
            else:
                # If there is no dot then simply append that digit to the number string
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            # If dot count is one then return Int i.e. Sankhya
            return Token(TT_INT, int(num_str), pos_start, self.pos)
        else:
            # If dot count is one then Dashank
            return Token(TT_FLOAT, float(num_str), pos_start, self.pos)


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

    # Register everything
    def register(self, res):
        if isinstance(res, ParseResult):
            if res.error:
                self.error = res.error
            return res.node
        return res

    # If parsing suceeds then return what you have created
    def success(self, node):
        self.node = node
        return self

    # If there is error present then throw error as it is
    def failure(self, error):
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

    ###################################

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS):
            # Implementation to look at the unary operations
            # Unary operation: + or -
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, factor))

        elif tok.type in (TT_INT, TT_FLOAT):
            # The block to manage int and float values
            res.register(self.advance())
            return res.success(NumberNode(tok))

        # Implementation to handle opening parenthesis (
        elif tok.type == TT_LPAREN:
            res.register(self.advance())
            expr = res.register(self.expr())
            if res.error:
                return res
            # If respective closing parenthesis found then continue
            # Return the successful parsing signal
            if self.current_tok.type == TT_RPAREN:
                res.register(self.advance())
                return res.success(expr)
            # If no closing parenthesis then throow below error
            else:
                return res.failure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Ujava apekshit hota ')'",
                    )
                )

        return res.failure(
            InvalidSyntaxError(tok.pos_start, tok.pos_end, "Sankhya Pahije hoti.")
        )

    # If *,/ or % symbol is there then follow respective manner to perform binary operation
    # term: factor ((GUNAKAR|BHAG|BAKI) factor)*
    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV, TT_MOD))

    # If + or - symbol is there then follow respective manner
    # expr: term ((ADHIK|KAMI) term)*
    def expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    ###################################

    def bin_op(self, func, ops):
        # Create a ParseResult object to track the parsing result
        res = ParseResult()
        # Parse the left operand using the provided parsing function 'func'
        left = res.register(func())
        # If there's an error in parsing the left operand, return the error
        if res.error:
            return res

        # Continue parsing while the current token type is one of the specified operators 'ops'
        while self.current_tok.type in ops:
            # Get the operator token
            op_tok = self.current_tok
            # Advance to the next token
            res.register(self.advance())
            # Parse the right operand using the provided parsing function 'func'
            right = res.register(func())
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
        self.value = None
        self.error = None

    def register(self, res):
        if res.error:
            self.error = res.error
        return res.value

    def success(self, value):
        self.value = value
        return self

    def failure(self, error):
        self.error = error
        return self


#######################################
#######################################
# VALUES
#######################################
#######################################


# This class actually takes the input then if there is arithmetic thing the correct result of that operation will be calculated and returned from this class
class Number:
    def __init__(self, value):
        # Retrive value from the input
        self.value = value
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        # Save the start and end position to local variables
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        # localize the context
        self.context = context
        return self

    def added_to(self, other):
        # Perform the addition
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None

    def subbed_by(self, other):
        # Perform the subtraction
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None

    def multed_by(self, other):
        # Perform the multiplication
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None

    def dived_by(self, other):
        # Perform the division
        if isinstance(other, Number):
            # If the divisor is 0 then return error : Division by 0
            if other.value == 0:
                return None, RTError(
                    other.pos_start, other.pos_end, "Shunya ne bhag", self.context
                )

            return Number(self.value / other.value).set_context(self.context), None

    def mod_by(self, other):
        # Perform the Modulus
        if isinstance(other, Number):
            if other.value == 0:
                # If the divisor is 0 then return error : Division by 0
                return None, RTError(
                    other.pos_start, other.pos_end, "Shunya ne bhag", self.context
                )

            return Number(self.value % other.value).set_context(self.context), None

    def __repr__(self):
        return str(self.value)


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

        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))


#######################################
#######################################
# RUN
#######################################
#######################################


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
    result = interpreter.visit(ast.node, context)

    return result.value, result.error


while True:
    text = input("BS > ")
    result, error = run("<stdin>", text)

    if error:
        print(error.as_string())
    else:
        print(result)
