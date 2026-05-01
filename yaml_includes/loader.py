import re
from pathlib import Path
from typing import Optional, Set, Union

from .exceptions import CyclicInclude, IncludeNotFound


INCLUDE_REGEX = re.compile(r'^(\s*)#\s*!include\s+(.*)$')

def load_text(
        path: Union[str, Path],
        seen: Optional[Set[Path]] = None
) -> str:
    """Load a YAML file as text, recursively resolving ``#!include`` directives.

    Each line matching ``#!include <filename>`` is replaced with the contents
    of the referenced file. Leading whitespace before the directive is
    preserved and prepended to every line of the included text, so nested
    structures stay correctly indented.

    :param path: Path to the YAML file to load (``str`` or :class:`~pathlib.Path`).
    :param seen: Set of already-visited absolute paths used to detect cycles.
        Pass ``None`` (the default) on the initial call; the set is populated
        automatically during recursion.
    :returns: The fully-resolved YAML source as a single string.
    :raises IncludedFileNotFound: If a file referenced by ``#!include`` does
        not exist on the filesystem.
    :raises CyclicInclude: If a chain of includes forms a cycle.

    **Include syntax**::

        #!include relative/path/to/fragment.yaml

    **Example**::

        import yaml

        from yaml_include import include_yaml

        document = yaml.safe_load(load_text('config.yaml'))
    """
    if seen is None:
        seen = set()
    path = Path(path).resolve()
    if path in seen:
        raise CyclicInclude(f'Cyclic include detected: {path}')
    seen.add(path)

    base_dir = path.parent
    output_lines = []

    for lineno, line in enumerate(path.read_text().splitlines(), 1):
        match = INCLUDE_REGEX.match(line)
        if match is not None:
            indent, filename = match.groups()
            include_path = (base_dir / filename).resolve()

            if not include_path.exists():
                raise IncludeNotFound(
                    f'{path}:{lineno}: included file not found: {filename}',
                )

            included_text = load_text(include_path, seen)

            # preserve identation
            for included_line in included_text.splitlines():
                output_lines.append(indent + included_line)
        else:
            output_lines.append(line)

    return '\n'.join(output_lines)
