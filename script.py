import basic, sys, readline

try:
    while True:
        try:
            text = input("BS > ")
            if text.strip() == "":
                continue
            result, error = basic.run("<ghetana>", text)
            if error:
                print(error.as_string())
            elif result:
                if len(result.elements) == 1:
                    print(repr(result.elements[0]))
                else:
                    print(repr(result))
        except EOFError:
            print("\nSamapt")
            sys.exit(0)
except KeyboardInterrupt:
    print("\nDhanyawad...")
    sys.exit(0)
