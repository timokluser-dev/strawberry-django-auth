<!-- shameless copy from graphene-django CONTRIBUTING file -->

# Contributing

Thanks for helping improve Django GraphQL Auth!

All kinds of contributions are welcome:

- Bug fixes
- Documentation improvements
- New features
- Refactoring
- Fix some typo
- Write more tests

## Getting started

If you have a specific contribution in mind, be sure to check the [issues](https://github.com/nrbnlulu/strawberry-django-auth/issues) and [projects](https://github.com/nrbnlulu/strawberry-django-auth/projects) in progress - someone could already be working on something similar and you can help out.

## Project setup

After cloning this repo, ensure dependencies are installed by running:

```bash
poetry install
```

and

```bash
pre-commit install
```

## Running tests

After developing, you can run tests with:

```bash
# python=3.7 and django=3.0
make test
```

## Opening Pull Requests

Please fork the project and open a pull request against the master branch.

This will trigger a series of tests and lint checks.

## Documentation

The documentation is generated using the excellent [MkDocs](https://www.mkdocs.org/) with [material theme](https://squidfunk.github.io/mkdocs-material/).

The documentation dependencies are installed by running:

Then to produce a HTML version of the documentation, for live editing:

```bash
make serve
```

It will run the `docs/pre_build.py` script before building the docs.
