import click

@click.command()
@click.option('--name', default='World', help='The name to greet.') 
def greet(name):
    click.echo(f"Hello, {name}!")

def main():
    greet()

if __name__ == "__main__":
    main()
