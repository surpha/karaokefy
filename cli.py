import click
from karaokefy.separate import separate_audio

@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output-dir', default='output', help='Directory to save the karaoke version.')
def main(input_file, output_dir):
    """Extracts the instrumental (karaoke) version from a song file."""
    click.echo(f"Processing {input_file}...")
    karaoke_path = separate_audio(input_file, output_dir)
    click.echo(f"Karaoke version saved to: {karaoke_path}")

if __name__ == '__main__':
    main() 