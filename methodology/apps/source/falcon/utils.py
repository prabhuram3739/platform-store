import logging
import pathlib
import readline


def get_platform(source_tree, name, simics_version):
    splatform = source_tree.get_platform(name, simics_version)
    if not splatform:
        splatform = get_platform_user(source_tree)

    return splatform


def get_platform_user(source_tree):
    platforms_filtered = filter_platforms(source_tree)

    map_names_platform = {x.name: x for x in platforms_filtered}
    names = map_names_platform.keys()
    message_names = ', '.join(names)
    message = f'enter platform name from the list: {message_names}\n'
    def completer(text, state):
        options = [name for name in names if name.startswith(text)]
        try:
            return options[state]
        except IndexError:
            return None
    readline.set_completer(completer)
    readline.parse_and_bind('tab: complete')
    while True:
        name = input(message).strip()
        if name not in names:
            logging.error("'%s' not in the list above, try again...", name)
            continue
        splatform = map_names_platform[name]
        break

    return splatform


def filter_platforms(source_tree):
    path = pathlib.Path.cwd()
    path_repo = source_tree.path
    splatforms = source_tree.get_platforms()
    map_path_platform = {}
    for splatform in splatforms:
        if splatform.path in map_path_platform:
            map_path_platform[splatform.path].append(splatform)
        else:
            map_path_platform[splatform.path] = [splatform]

    while True:
        if path == path_repo:
            break
        if path in map_path_platform:
            splatforms = map_path_platform.get(path)
            break

        path = path.parent

    return splatforms
