import sys, readline

# If 'basic' is in the same package as script.py
# from . import basic

# If 'basic' is in a different package
from bhashascript import basic


def main():
    print(
        """  
\033[33m  ____  _    _           _____ _    _           _____  _____ _____  _____ _____ _______ \033[0m
\033[33m |  _ \| |  | |   /\    / ____| |  | |   /\    / ____|/ ____|  __ \|_   _|  __ \__   __|\033[0m
\033[97m | |_) | |__| |  /  \  | (___ | |__| | \033[94m /  \  | (___ \033[97m| |    | |__) | | | | |__) | | |   \033[0m
\033[97m |  _ <|  __  | / /\ \  \___ \|  __  |\033[94m / /\ \  \___ \033[97m\| |    |  _  /  | | |  ___/  | |   \033[0m
\033[92m | |_) | |  | |/ ____ \ ____) | |  | |/ ____ \ ____) | |____| | \ \ _| |_| |      | |   \033[0m
\033[92m |____/|_|  |_/_/    \_\_____/|_|  |_/_/    \_\_____/ \_____|_|  \_\_____|_|      |_|   \033[0m
                                                                                         
         """
    )
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


if __name__ == "__main__":
    main()
