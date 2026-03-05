# Dev

## Editable install

In the virtual environment:
```
pip install -e ".[dev]"
```

## Run tests

```bash
pytest tests/ -v
```

## Build

```bash
uv build
```

## Local test install

```bash
uv pip install dist/*.whl
```

## Publish

Test PyPI:

```bash
uv publish --index testpypi
```

PyPI:
```bash
uv publish
```
