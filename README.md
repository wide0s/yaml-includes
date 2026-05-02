# yaml-includes

A lightweight Python library for composing YAML files with `#!include` directives.

## Installation

Install it using `pip`:

```bash
pip install yaml-includes
```

or `poetry`:

```bash
poetry add yaml-includes
```

## Overview

`yaml-includes` lets you split large YAML configurations into smaller, reusable fragments. Any line matching `#!include <path>` is replaced with the contents of the referenced file before parsing.

## Include syntax

```
[indent]#!include relative/path/to/fragment.yaml
```

- Path is resolved relative to the file containing the directive.
- Leading whitespace before `#!include` is prepended to every line of the included content, preserving YAML nesting.
- Fragments can themselves contain `#!include` directives (recursive).

### Example: indented include

```yaml
# config.yaml
services:
  web:
    #!include web.yaml
```

```yaml
# web.yaml
image: nginx
ports:
  - "80:80"
```

Result:

```yaml
services:
  web:
    image: nginx
    ports:
      - "80:80"
```

## Usage example

Loads a YAML file and resolves all `#!include` directives recursively.

```python
import yaml
from yaml_includes import load_text

document = yaml.safe_load(load_text("config.yaml"))
```

## Development

```bash
# Install project dependencies
make install

# Run linter
make lint

# Run tests
make test

# Run tests with coverage
make test-with-cov
```

## License

MIT
