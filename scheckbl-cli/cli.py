from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
from colorama import Fore, Style, init as colorama_init
from scheckbl import blocklist

colorama_init(autoreset=True)

class CustomHelpFormatter(click.HelpFormatter):
    def write_heading(self, heading):
        heading = f"{Style.BRIGHT}{Fore.RED}■ {heading}:{Style.RESET_ALL}"
        super().write_heading(heading)
    
    def write_usage(self, prog, args='', prefix='Usage: '):
        prefix = f"{Style.BRIGHT}{Fore.RED}{prefix}{Style.RESET_ALL}{Style.BRIGHT}"
        super().write_usage(prog, args, prefix)
    
    def write_text(self, text):
        if text:
            text = re.sub(r'(-[a-zA-Z](?:\s|,|$))', f'{Style.BRIGHT}{Fore.RED}\\1{Style.RESET_ALL}', text)
            text = re.sub(r'(--[a-zA-Z-]+)', f'{Style.BRIGHT}{Fore.RED}\\1{Style.RESET_ALL}', text)
            text = re.sub(r'([A-Z_]+)(?=\s|$|\n)', f'{Style.BRIGHT}{Fore.RED}\\1{Style.RESET_ALL}', text)
        super().write_text(text)

class CustomGroup(click.Group):
    def get_help(self, ctx):
        formatter = CustomHelpFormatter(width=100)
        self.format_help(ctx, formatter)
        return formatter.getvalue()

@click.group(
    cls=CustomGroup,
    context_settings={"help_option_names": ["-h", "--help"]}
)
@click.version_option(package_name="scheckbl", prog_name="scheckbl-cli")
def cli():
    """
    \b
    ╔══════════════════════════════════════════════════════════════╗
    ║                     scheckbl-cli                             ║
    ║          Search & Filter Tool for SCheck Blocklist           ║
    ╚══════════════════════════════════════════════════════════════╝
    
    Search & filter tool for SCheck Blocklist datasets.
    https://scheck-blocklist.vercel.app
    
    \b
    Available commands:
      check    - check if keyword exists in blocklist
      find     - find any hits in text  
      get      - retrieve full list and save to file
      similar  - find entries similar to given phrase
    
    \b
    Usage: scheckbl-cli [COMMAND] [OPTIONS] [ARGUMENTS]
    Help:  scheckbl-cli [COMMAND] --help
    """
    pass

def _slugify(text: str) -> str:
    return re.sub(r"[^\w\-]+", "_", text).strip("_").lower()

def _auto_filename(*parts: str, ext: str) -> Path:
    stamp = datetime.now().strftime("%Y-%m-%d")
    slug = "_".join(_slugify(p) for p in parts)
    return Path(f"{slug}_{stamp}.{ext}")

def _write_output(content: str, output: Optional[Path]) -> None:
    try:
        Path(output).write_text(content, encoding="utf-8")
        click.echo(f"{Style.BRIGHT}{Fore.GREEN}✓ Saved → {Style.RESET_ALL}{output}")
    except Exception as e:
        click.echo(f"{Style.BRIGHT}{Fore.RED}✗ Write error: {Style.RESET_ALL}{e}")
        sys.exit(1)

def echo_result(result: bool) -> None:
    if result:
        click.echo(f"{Style.BRIGHT}{Fore.GREEN}✓ FOUND{Style.RESET_ALL}")
        click.echo(f"{Fore.GREEN}Result: {Style.BRIGHT}True{Style.RESET_ALL}")
    else:
        click.echo(f"{Style.BRIGHT}{Fore.RED}✗ NOT FOUND{Style.RESET_ALL}")
        click.echo(f"{Fore.RED}Result: {Style.BRIGHT}False{Style.RESET_ALL}")

@cli.command(
    name="check",
    short_help="Check if keyword exists in blocklist",
    help="""\
Check if a given keyword exists in a blocklist.

\b
Arguments:
  TYPE_NAME   Blocklist type (e.g., phrases, urls)
  CATEGORY    Category (e.g., vulgarisms, nsfw)  
  KEYWORD     Exact keyword to verify

\b
Example:
  scheckbl-cli check phrases vulgarisms "bad_word"
"""
)
@click.argument("type_name")
@click.argument("category")
@click.argument("keyword")
def check(type_name: str, category: str, keyword: str) -> None:
    try:
        result = blocklist.check(type_name, category, keyword)
        echo_result(result)
        sys.exit(0 if result else 1)
    except Exception as e:
        click.echo(f"{Style.BRIGHT}{Fore.RED}✗ Error: {Style.RESET_ALL}{e}")
        sys.exit(1)

@cli.command(
    name="find",
    short_help="Find any hits in text",
    help="""\
Scan a text for any blocklisted entry.

\b
Arguments:
  TYPE_NAME   Blocklist type
  CATEGORY    Category to search
  TEXT        Full sentence or message to analyze

\b
Example:
  scheckbl-cli find phrases vulgarisms "This is some text to check"
"""
)
@click.argument("type_name")
@click.argument("category")
@click.argument("text")
def find(type_name: str, category: str, text: str) -> None:
    try:
        result = blocklist.find(type_name, category, text)
        echo_result(result)
        sys.exit(0 if result else 1)
    except Exception as e:
        click.echo(f"{Style.BRIGHT}{Fore.RED}✗ Error: {Style.RESET_ALL}{e}")
        sys.exit(1)

@cli.command(
    name="get",
    short_help="Retrieve full list and save to TXT file",
    help="""\
Retrieve all entries from a blocklist and write them to a file.

\b
Arguments:
  TYPE_NAME   Blocklist type
  CATEGORY    Category to retrieve

\b
Options:
  -f, --filename NAME     Specific dataset file
  -r, --regex PATTERN     Filter lines by regex
  -o, --output FILE       Custom output path
  --stdout                Print to stdout instead of file

\b
Example:
  scheckbl-cli get phrases vulgarisms
  scheckbl-cli get phrases vulgarisms --stdout
"""
)
@click.argument("type_name")
@click.argument("category")
@click.option("-f", "--filename", metavar="NAME", help="Specific dataset file")
@click.option("-r", "--regex", metavar="PATTERN", help="Filter with regex")
@click.option("-o", "--output", type=click.Path(writable=True), help="Write to custom file")
@click.option("--stdout", is_flag=True, help="Force print to terminal")
def get(type_name: str, category: str,
        filename: Optional[str], regex: Optional[str],
        output: Optional[Path], stdout: bool) -> None:

    try:
        data = blocklist.get(type_name, category, filename=filename, regex=regex)
        if isinstance(data, str):
            content = data
        elif hasattr(data, '__iter__') and not isinstance(data, str):
            content = "\n".join(str(item) for item in data)
        else:
            content = str(data)

        if stdout:
            click.echo_via_pager(content)
        else:
            output = output or _auto_filename(type_name, category, "get", ext="txt")
            _write_output(content, output)
            
    except Exception as e:
        click.echo(f"{Style.BRIGHT}{Fore.RED}✗ Error: {Style.RESET_ALL}{e}")
        sys.exit(1)

@cli.command(
    name="similar",
    short_help="Find entries similar to given phrase",
    help="""\
Find entries similar to a phrase and store them.

\b
Arguments:
  TYPE_NAME   Blocklist type
  CATEGORY    Category
  PHRASE      Input phrase to compare

\b
Options:
  -t, --threshold FLOAT   Minimum similarity (0.0–1.0), default 0.6
  --json                  Output JSON instead of text
  -o, --output FILE       Custom output path
  --stdout                Print to stdout instead of file

\b
Example:
  scheckbl-cli similar phrases vulgarisms "example_phrase"
  scheckbl-cli similar phrases vulgarisms "example_phrase" --json
"""
)
@click.argument("type_name")
@click.argument("category")
@click.argument("phrase")
@click.option("-t", "--threshold", type=float, default=0.6, show_default=True, 
              help="Minimum similarity (0.0-1.0)")
@click.option("--json", "as_json", is_flag=True, help="Write JSON file")
@click.option("-o", "--output", type=click.Path(writable=True), help="Custom output file")
@click.option("--stdout", is_flag=True, help="Force print to terminal")
def similar(type_name: str, category: str, phrase: str,
            threshold: float, as_json: bool,
            output: Optional[Path], stdout: bool) -> None:

    try:
        results = blocklist.similar(type_name, category, phrase, threshold)
        
        if not results:
            click.echo(f"{Style.BRIGHT}{Fore.YELLOW}⚠ No similar entries found for threshold {threshold}{Style.RESET_ALL}")
            return

        if stdout:
            if as_json:
                click.echo(json.dumps(results, ensure_ascii=False, indent=2))
            else:
                click.echo(f"{Style.BRIGHT}{Fore.CYAN}Similar entries (threshold: {threshold}):{Style.RESET_ALL}")
                click.echo("-" * 60)
                for entry, score in results:
                    score_color = Fore.GREEN if score > 0.8 else Fore.YELLOW if score > 0.6 else Fore.RED
                    click.echo(f"{entry:<50} {score_color}{Style.BRIGHT}{score:.2%}{Style.RESET_ALL}")
            return

        if as_json:
            output = output or _auto_filename(type_name, category, "similar", ext="json")
            json_content = json.dumps(results, ensure_ascii=False, indent=2)
            _write_output(json_content, output)
        else:
            lines = [f"{entry}\t{score:.4f}" for entry, score in results]
            output = output or _auto_filename(type_name, category, "similar", ext="txt")
            _write_output("\n".join(lines), output)
            
    except Exception as e:
        click.echo(f"{Style.BRIGHT}{Fore.RED}✗ Error: {Style.RESET_ALL}{e}")
        sys.exit(1)

def main() -> None:
    if (
        len(sys.argv) >= 3
        and sys.argv[1] in ("-h", "--help")
        and sys.argv[2] in cli.commands
    ):
        cmd = cli.commands[sys.argv[2]]
        with click.Context(cmd) as ctx:
            click.echo(cmd.get_help(ctx))
        sys.exit(0)

    try:
        cli()
    except KeyboardInterrupt:
        click.echo(f"\n{Style.BRIGHT}{Fore.YELLOW}⚠ Interrupted by user{Style.RESET_ALL}")
        sys.exit(130)
    except Exception as e:
        click.echo(f"{Style.BRIGHT}{Fore.RED}✗ Unexpected error: {Style.RESET_ALL}{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()