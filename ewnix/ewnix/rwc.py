import click
import requests

@click.command()
@click.option("-c", "--bytes", "show_bytes", is_flag=True, help="print the byte counts")
@click.option("-l", "--lines", "show_lines", is_flag=True, help="print the newline counts")
@click.option("-L", "--max-line-length", "show_max_line_length", is_flag=True, help="print the maximum display width")
@click.option("-w", "--words", "show_words", is_flag=True, help="print the word counts")
@click.argument("url")
def command(show_bytes, show_lines, show_max_line_length, show_words, url):
    """Count statistics in a remote file retrieved through HTTP/HTTPS."""
    response = requests.get(url)
    response.raise_for_status()

    text = response.text

    # Compute all stats
    byte_count = len(response.content)
    line_count = text.count("\n")
    word_count = len(text.split())
    max_line_length = max((len(line) for line in text.splitlines()), default=0)

    # If no flags were provided, show everything (wc default behavior)
    if not (show_bytes or show_lines or show_max_line_length or show_words):
        show_bytes = show_lines = show_max_line_length = show_words = True

    output_parts = []

    if show_lines:
        output_parts.append(f"{line_count}")
    if show_words:
        output_parts.append(f"{word_count}")
    if show_bytes:
        output_parts.append(f"{byte_count}")
    if show_max_line_length:
        output_parts.append(f"{max_line_length}")

    # Append the URL at the end, like wc prints the filename
    output_parts.append(url)

    click.echo(" ".join(output_parts))