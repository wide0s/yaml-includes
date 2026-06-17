import re
from pathlib import Path
from typing import Optional, Set, Union

from .exceptions import CyclicInclude, IncludeNotFound


INCLUDE_REGEX = re.compile(r'^(\s*)#\s*!include\s+(.*)$')

def resolve_includes(
        text: str,
        base_dir: Path,
        seen: Optional[Set[Path]] = None
) -> str:
    """Resolve ``#!include`` directives in YAML text.

    Each line matching ``#!include <filename>`` is replaced with the contents
    of the referenced file. Leading whitespace before the directive is
    preserved and prepended to every line of the included text, so nested
    structures stay correctly indented.

    Relative include paths are resolved against ``base_dir``.

    :param text: YAML source text to process.
    :param base_dir: Base directory used to resolve relative include paths.
    :param seen: Set of already-visited absolute paths used to detect cycles.
        Pass ``None`` (the default) on the initial call; the set is populated
        automatically during recursion.
    :returns: The fully-resolved YAML source as a single string.
    :raises IncludeNotFound: If a file referenced by ``#!include`` does
        not exist on the filesystem.
    :raises CyclicInclude: If a chain of includes forms a cycle.

    **Include syntax**::

        #!include relative/path/to/fragment.yaml

    **Example**::

        from pathlib import Path

        from yaml_includes import resolve_includes

        text = '''
        application:
          #!include config/database.yaml
        '''

        document = resolve_includes(
            text,
            base_dir=Path('.'),
        )
    """
    if seen is None:
        seen = set()

    output_lines = []

    for lineno, line in enumerate(text.splitlines(), 1):
        match = INCLUDE_REGEX.match(line)

        if match is None:
            output_lines.append(line)
            continue

        indent, filename = match.groups()
        include_path = (base_dir / filename).resolve()

        if include_path in seen:
            raise CyclicInclude(
                f'Cyclic include detected: {include_path}'
            )

        if not include_path.exists():
            raise IncludeNotFound(
                f'<input>:{lineno}: included file not found: {filename}'
            )

        seen.add(include_path)

        try:
            included_text = resolve_includes(
                text=include_path.read_text(),
                base_dir=include_path.parent,
                seen=seen,
            )
        finally:
            seen.remove(include_path)

        # preserve identation
        for included_line in included_text.splitlines():
            output_lines.append(indent + included_line)

    return '\n'.join(output_lines)


def load_text(
    path: Union[str, Path],
    seen: Optional[Set[Path]] = None,
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
    :raises IncludeNotFound: If a file referenced by ``#!include`` does
        not exist on the filesystem.
    :raises CyclicInclude: If a chain of includes forms a cycle.

    **Include syntax**::

        #!include relative/path/to/fragment.yaml

    **Example**::

        import yaml

        from yaml_includes import load_text

        document = yaml.safe_load(load_text('config.yaml'))
    """
    path = Path(path).resolve()

    if seen is None:
        seen = set()

    if path in seen:
        raise CyclicInclude(f'Cyclic include detected: {path}')

    seen.add(path)

    try:
        return resolve_includes(
            text=path.read_text(),
            base_dir=path.parent,
            seen=seen,
        )
    finally:
        seen.remove(path)
