class CyclicInclude(Exception):
    """Raised when a chain of ``#!include`` directives forms a cycle."""

class IncludeNotFound(FileNotFoundError):
    """Raised when a file referenced by a ``#!include`` directive does not exist."""
