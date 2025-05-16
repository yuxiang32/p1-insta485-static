"""Build static HTML site from directory of HTML templates and plain files."""
import click
import pathlib
import json
import jinja2
import sys # Import sys for exiting
import shutil

@click.command()
@click.argument("input_dir", nargs=1, type=click.Path(exists=True))
@click.option("-o", "--output", "output_dir", default="generated_html", type=click.Path(), help="Output directory.")
@click.option("-v", "--verbose", is_flag=True, help="Print more output.")
def main(input_dir, output_dir, verbose):
    """Templated static website generator."""
    input_dir = pathlib.Path(input_dir)
    output_dir = pathlib.Path(output_dir)
    
    # Check if output directory already exists
    if output_dir.exists():
        click.echo(f"insta485generator error: '{output_dir}' already exists.", err=True)
        sys.exit(1)  # Exit with a non-zero status code to indicate an error

    # Construct the path to config.json within input_dir
    config_path = input_dir / "config.json"
    # Read the JSON content from config.json
    try:
        with config_path.open() as config_file:
            config_list = json.load(config_file)
    except FileNotFoundError:
        click.echo(f"insta485generator error: '{config_path}' not found.", err=True)
        sys.exit(1)  # Exit with a non-zero status code to indicate an error
    except json.JSONDecodeError:
        click.echo(f"insta485generator error: '{config_path}'\n{e}", err=True)
        sys.exit(1)  # Exit with a non-zero status code to indicate an error
    
    #Create the output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Copy the static directory to the output directory
    static_dir = input_dir / "static"
    if static_dir.is_dir():
        shutil.copytree(static_dir, output_dir, dirs_exist_ok=True)
        if verbose: # Print verbose message if -v is provided as a command line argument
            print(f"Copied {static_dir} -> {output_dir}")
        print(f"Copied static directory to '{output_dir}'")
    
    template_dir = input_dir / "templates"
    if not template_dir.is_dir():
        click.echo(f"insta485generator error: '{template_dir}' not found.", err=True)
        sys.exit(1)  # Exit with a non-zero status code to indicate an error

    # Configure the Jinja2 environment
    template_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template_dir)),
        autoescape=jinja2.select_autoescape(['html', 'xml']),
    )

    # Process each configuration item
    for config_item in config_list:
        template_filename = config_item.get("template")
        context = config_item.get("context", {}) # Default to empty dict if no context
        url = config_item.get("url")

        url = url.lstrip("/")  # remove leading slash
        output_dir = pathlib.Path(output_dir)  # convert str to Path object, when --output is provided
        output_path = output_dir/url/"index.html"

        try:
            template = template_env.get_template(template_filename)
            rendered_html = template.render(context)
            
            with output_path.open("w") as output_file:
                output_file.write(rendered_html)

            if verbose: # Print verbose message if -v is provided as a command line argument
                print(f"Rendered {template_filename} -> {output_path}")

        except jinja2.TemplateError as e:
            click.echo(f"insta485generator error: '{template_filename}'\n{e}", err=True)
            sys.exit(1)  # Exit with a non-zero status code to indicate an error

if __name__ == "__main__":
    main()