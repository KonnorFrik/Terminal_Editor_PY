from fixed_list import FixedLengthList
from enum import Enum
from typing import Collection
from collections import UserList

class Mode(Enum):
    TEXT = "txt"
    BIN = "bin"

name_help_map = dict()
name_func_map = dict()

def special_command(func):
    name_func_map[func.__name__] = func
    name_help_map[func.__name__] = func.__doc__
    return func


__SPECIAL_PROMPT = "@"
__COMMAND_WORD_COUNT = 2
__prompt = "> "
__buffer_size = 1000
__delimeter = " "
__mode = Mode.TEXT
__number_base = 16


#class FixedBuffer(FixedLengthList):
class ProgrammBuffer(UserList):
    def __init__(self, length: int, *a, **kw):
        super().__init__(*a, **kw)
        self.length = length
        self.re_init()

    def re_init(self):
        self.data = [str() for _ in range(self.length)]

    def __getitem__(self, i):
        return self.data[i]

__user_programm_buffer: Collection# = FixedBuffer(length=__buffer_size)


def get_user_input() -> str:
    return input(__prompt)


def write_line_to_buffer(index: int, line: str):
    global __user_programm_buffer
    index -= 1
    __user_programm_buffer[index] = line

    #print(f"[#] Writed: '{line}' with ind: '{index}'")
    #print(len(__user_programm_buffer))
    #print()


def validate(line: str):
    splitted = line.split(__delimeter)

    try:
        index = int(splitted[0]) - 1
    except ValueError:
        print("Can't get index")
        return False

    if index > __buffer_size:
        print("Line index too big. Maximum is", __buffer_size + 1)
        return False

    if index < 0:
        print("Line index too small. Minimum is", 1)
        return False

    return True


def proccess_command(line: str):
    if not validate(line):
        return

    splitted = line.split(__delimeter)
    index = int(splitted[0])
    write_line_to_buffer(index, __delimeter.join(splitted[1:]))


@special_command
def show(user_slice: str | None = None):
    """Show you programm line by line\n\tUsage: @show [start_line:end_line:step]"""

    slice_: slice

    if not user_slice:
        slice_ = slice(0, __buffer_size, 1)

    else:
        user_slice = user_slice[0]

        if user_slice.startswith(":"):
            user_slice = str(1) + user_slice

        if user_slice.endswith(":"):
            user_slice += str(__buffer_size)

        if all([symb.isdigit() for symb in user_slice]):
            slice_ = int(user_slice)

        else:
            splitted = user_slice.split(":")
            slice_ = slice(*[int(s) - 1 if i == 0 else int(s) for i, s in enumerate(splitted) if s.isdigit()][:3])

    if type(slice_) == int:
        print(f"{slice_} \t{__user_programm_buffer[slice_ - 1]}")

    else:
        for index, val in enumerate(__user_programm_buffer[slice_]):
            if val:
                print(f"{index + 1 + slice_.start} \t{val}")


@special_command
def length(*args, **kwargs):
    """Show available buffer len"""
    print("Programm buffer length:", len(__user_programm_buffer))


@special_command
def save(filename: list | None = None):
    """Save programm to file\n\tUsage: @save [filename]"""
    if not filename:
        filename = input("filename for load ~ ")

    else:
        filename = filename[0]

    if not filename:
        print("No filename given")
        return

    mode: str

    if __mode == Mode.TEXT:
        mode = "w"

    else:
        mode = "wb"

    file = open(filename, mode)
    writed = 0

    for row in __user_programm_buffer:
        if row:
            if __mode == Mode.TEXT:
                file.write(row + "\n")

            else:
                file.write(int(row, base=__number_base).to_bytes())

            writed += 1

    print(f"Writed '{writed}' rows to file")
    file.close()


@special_command
def load(filename: list | None = None):
    """Load programm from file\n\tUsage: @load [filename]"""
    if not filename:
        filename = input("filename for load ~ ")

    else:
        filename = filename[0]

    if not filename:
        print("No filename given")
        return

    mode: str

    if __mode == Mode.TEXT:
        mode = "r"

    else:
        mode = "rb"

    file = open(filename, mode)
    loaded_rows = 0

    if __mode == Mode.TEXT:
        for index, line in enumerate(file):
            line = line.replace("\n", "")
            __user_programm_buffer[index] = line
            loaded_rows += 1

    else:
        index = 0
        while(byte := file.read(1)):
            __user_programm_buffer[index] = f"0x{int.from_bytes(byte):X}"
            loaded_rows += 1
            index += 1


    print(f"Load '{loaded_rows}' rows from file '{filename}'")
    file.close()



@special_command
def clear(answ: str | None = None):
    """Delete all lines of your programm\n\tUsage: @clear [answer(y/n)]"""
    if not answ:
        answ = input("Delete all programm? [y/(n)] ~ ")

    else:
        answ = answ[0]

    if answ == "y" or answ == "yes":
        __user_programm_buffer.re_init()
        print("Programm deleted")


@special_command
def help(*args, **kwargs):
    """Show help page"""
    for spec_com, help_msg in name_help_map.items():
        print(__SPECIAL_PROMPT + spec_com + "\t" + help_msg, "\n")


@special_command
def quit(*args, **kwargs):
    """Exit from editor without save"""
    exit()


def proccess_special_command(line: str):
    if len(splitted := line[1:].split(__delimeter)) > 1:
        name_func_map[splitted[0]](splitted[1:])
        return

    try:
        name_func_map[line[1:]]()

    except KeyError:
        print("Unknown command")


def parse_args(argv: Collection):
    global __buffer_size
    global __mode

    for arg in argv:
        match arg:
            case str() as obj if (all([symb.isdigit() for symb in obj])):
                __buffer_size = int(obj)

            case str() as obj:
                try:
                    __mode = Mode(obj)

                except ValueError:
                    __mode = Mode.TEXT
                    continue


def main():
    global __user_programm_buffer
    __user_programm_buffer = ProgrammBuffer(__buffer_size)#[str() for _ in range(__buffer_size)]#FixedBuffer(length=__buffer_size)

    try:
        while True:
            line = get_user_input().strip()
            match line:
                case str() as special_line if special_line.startswith(__SPECIAL_PROMPT):
                    proccess_special_command(special_line)

                case str() as command:
                    proccess_command(command)

    except KeyboardInterrupt:
        print("\nBye")


#TODO
# special command for setting up number base( 10 or 16 or 8 or ... )
# special command for change mode in runtime (txt or bin) with help msg

if __name__ == "__main__":
    import sys

    if sys.argv[1:]:
        parse_args(sys.argv[1:])

    print("Buffer size:", __buffer_size)
    print("Mode:", __mode.value)
        #try:
            #__buffer_size = int(sys.argv[1])
        #except ValueError:
            #print("Invalid args. Use default")

    main()
