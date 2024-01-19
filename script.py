import basic
import sys
import readline

try:
    while True:
        try:
            text = input("BS > ")
            result, error = basic.run("<stdin>", text)

            if error:
                print(error.as_string())
            elif result:
                print(repr(result))

        except EOFError:
            print("\nSamapt")
            sys.exit(0)

except KeyboardInterrupt:
    print("\nDhanyawad...")
    sys.exit(0)

# import basic


# def print_result(result):
#     if isinstance(result, basic.NumberNode):
#         print(result.tok.value)
#     elif isinstance(result, basic.BinaryOpNode):
#         print_result(result.left_node)
#         print(result.op_tok.type)
#         print_result(result.right_node)


# while True:
#     text = input("BS > ")
#     result, error = basic.run("<stdin>", text)

#     if error:
#         print(error.as_string())
#     else:
#         print(result)
