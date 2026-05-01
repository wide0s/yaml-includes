import pytest

from yaml_includes import (CyclicInclude, IncludeNotFound, load_text)


def test_no_includes(tmp_path):
    f = tmp_path / "config.yaml"
    f.write_text("key: value\n")
    assert load_text(f) == "key: value"


def test_str_path(tmp_path):
    f = tmp_path / "config.yaml"
    f.write_text("key: value\n")
    assert load_text(str(f)) == "key: value"


def test_single_include(tmp_path):
    fragment = tmp_path / "fragment.yaml"
    fragment.write_text("b: 2\n")
    main = tmp_path / "main.yaml"
    main.write_text("a: 1\n#!include fragment.yaml\nc: 3\n")

    result = load_text(main)
    assert result == "a: 1\nb: 2\nc: 3"


def test_multiple_includes(tmp_path):
    (tmp_path / "x.yaml").write_text("x: 1\n")
    (tmp_path / "y.yaml").write_text("y: 2\n")
    main = tmp_path / "main.yaml"
    main.write_text("#!include x.yaml\n#!include y.yaml\n")

    result = load_text(main)
    assert result == "x: 1\ny: 2"


def test_indented_include(tmp_path):
    fragment = tmp_path / "fragment.yaml"
    fragment.write_text("key: val\n")
    main = tmp_path / "main.yaml"
    main.write_text("outer:\n  #!include fragment.yaml\n")

    result = load_text(main)
    assert result == "outer:\n  key: val"


def test_nested_include(tmp_path):
    leaf = tmp_path / "leaf.yaml"
    leaf.write_text("leaf: true\n")
    middle = tmp_path / "middle.yaml"
    middle.write_text("#!include leaf.yaml\n")
    main = tmp_path / "main.yaml"
    main.write_text("#!include middle.yaml\n")

    assert load_text(main) == "leaf: true"


def test_included_file_not_found(tmp_path):
    main = tmp_path / "main.yaml"
    main.write_text("#!include missing.yaml\n")

    with pytest.raises(IncludeNotFound):
        load_text(main)


def test_cyclic_include_self(tmp_path):
    f = tmp_path / "self.yaml"
    f.write_text("#!include self.yaml\n")

    with pytest.raises(CyclicInclude):
        load_text(f)


def test_cyclic_include_indirect(tmp_path):
    a = tmp_path / "a.yaml"
    b = tmp_path / "b.yaml"
    a.write_text("#!include b.yaml\n")
    b.write_text("#!include a.yaml\n")

    with pytest.raises(CyclicInclude):
        load_text(a)
