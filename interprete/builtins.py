def _builtin_print(*args, **kwargs):
    sep = kwargs.get("sep", " ")
    end = kwargs.get("end", "\n")
    print(sep.join(str(a) for a in args), end=end)
    return None

BUILTIN_FUNCS = {
    "print": _builtin_print,
    "len": len,
    "sum": sum,
    "range": range,
    "int": int,
    "float": float,
    "bool": bool,
    "str": str,
    "list": list,
    "dict": dict,
    "set": set,
    "tuple": tuple,
    "setattr": setattr,
    "getattr": getattr  # <--- AGREGAR ESTA LÍNEA
}       