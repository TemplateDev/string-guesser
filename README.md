# String Guesser

A command-line tool that searches for a supplied string using a genetic algorithm
and displays its progress in the terminal.

## Requirements

- Python 3.14 or newer
- [uv](https://docs.astral.sh/uv/) for installing and running the project

## Setup

From the project directory, install the locked dependencies:

```sh
uv sync
```

## Usage

Pass the string to find as the required positional argument:

```sh
uv run main.py "hello"
```

The search uses 10,000 iterations by default. You can adjust the search and
progress display with these options:

```text
--iterations N          Maximum number of iterations (default: 10000)
--steps N               Report progress every N iterations (default: 1000)
--target-percentage N   Stop at this match percentage (default: 100)
--delay SECONDS         Pause after each progress update
```

For example:

```sh
uv run main.py "hello" --iterations 20000 --steps 500
```
