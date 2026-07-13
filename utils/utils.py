import json


def print_indented(obj):
    print(json.dumps(obj, indent=2))


def inspect(value, indent=0, prefix=""):
    space = "  " * indent

    if isinstance(value, dict):
        print(f"{space}{prefix}{{")
        for key, v in value.items():
            if isinstance(v, (dict, list)):
                inspect(v, indent + 1, prefix=f"{key!r}: ")
            else:
                print(f"{space}  {key!r}: {type(v).__name__}")
        print(f"{space}}}")

    elif isinstance(value, list):
        item = value[0] if value else None
        if isinstance(item, (dict, list)):
            # nested content -> expand over multiple lines
            print(f"{space}{prefix}[")
            inspect(item, indent + 1)
            print(f"{space}]")
        else:
            # simple type -> all on one line
            item_type = type(item).__name__ if value else ""
            print(f"{space}{prefix}[ {item_type} ]")