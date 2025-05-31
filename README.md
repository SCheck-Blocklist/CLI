
# SCheck Blocklist CLI

**Command-line interface tool for interacting with SCheck Blocklist datasets.**  
> Current Version: `1.1.0`  
>  
> Our Website: [scheck-blocklist.vercel.app](https://scheck-blocklist.vercel.app)

---

## Content
- [Installation](#installation)
- [Usage](#usage)
  - [Check](#check-if-a-keyword-exists)
  - [Find](#find-hits-in-text)
  - [Gett](#retrieve-full-list)
  - [Similiar](#find-similar-entries)
- [Help](#help)

---

## Installation

Install the CLI tool via pip:

```bash
pip install scheckbl-cli
````

---

## Usage

The CLI provides multiple commands to interact with blocklists.

### Check if a keyword exists

```bash
scheckbl-cli check <type_name> <category> <keyword>
```

Example:

```bash
scheckbl-cli check phrases vulgarisms "example_word"
```

---

### Find hits in text

Searches if any blocklisted entries appear in the given text:

```bash
scheckbl-cli find <type_name> <category> <text>
```

Example:

```bash
scheckbl-cli find phrases vulgarisms "This is some sample text."
```

---

### Retrieve full list

Get the full blocklist and save or output it:

```bash
scheckbl-cli get <type_name> <category> [options]
```

**Options:**

* `-f, --filename NAME` — specify filename
* `-r, --regex PATTERN` — filter results by regex
* `-o, --output FILE` — save output to a file
* `--stdout` — print output to standard output

Example:

```bash
scheckbl-cli get phrases vulgarisms --stdout
```

---

### Find similar entries

Find blocklist entries similar to a given phrase:

```bash
scheckbl-cli similar <type_name> <category> <phrase> [options]
```

**Options:**

* `-t, --threshold FLOAT` — similarity threshold (default 0.6)
* `--json` — output results as JSON
* `-o, --output FILE` — save output to a file
* `--stdout` — print output to standard output

Example:

```bash
scheckbl-cli similar phrases vulgarisms "example_phrase" --json
```

---

## Help

For detailed help on commands and options:

```bash
scheckbl-cli --help
scheckbl-cli <command> --help
```

---
