import os

from django.contrib.staticfiles.finders import get_finders
import sass


def find_static_paths():
    """
    Finds all static paths available in this Django project.

    :returns:
        List of paths containing static files.
    """
    found_paths = []
    for finder in get_finders():
        if hasattr(finder, 'storages'):
            for app in finder.storages:
                if hasattr(finder.storages[app], 'location'):
                    abspath = finder.storages[app].location
                    found_paths.append(abspath)
    return found_paths


def find_static_scss():
    """
    Finds all static scss files available in this Django project.

    :returns:
        List of paths of static scss files.
    """
    scss_files = []
    for finder in get_finders():
        for path, storage in finder.list([]):
            if path.endswith(".scss"):
                fullpath = finder.find(path)
                scss_files.append(fullpath)
    return scss_files


def compile_sass(inpath, outpath, output_style=None, precision=None,
                 source_map=False):
    """
    Calls sass.compile() within context of Django's known static file paths,
    and writes output CSS and/or sourcemaps to file.

    :param str inpath:
        Path to SCSS file or directory of SCSS files.
    :param str outpath:
        Path to a CSS file or directory in which to write output. The path will
        be created if it does not exist.
    :param str output_style:
        Corresponds to `output_style` from sass package.
    :param int precision:
        Corresponds to `precision` from sass package.
    :param bool source_map:
        If True, write a source map along with the output CSS file.
        Only valid when `inpath` is a file.
    :returns:
        None
    """

    # If include paths are not specified, use Django static paths
    include_paths = find_static_paths()

    sassargs = {}

    # Handle input files.
    outfile = None
    if os.path.isfile(inpath):
        sassargs.update({"filename": inpath})
        if os.path.isdir(outpath):
            outfile = os.path.join(
                outpath, os.path.basename(inpath.replace(".scss", ".css"))
            )
        else:
            outfile = outpath
        if source_map:
            args.update({"source_map_filename": outfile + ".map"})

    # Compile the sass.
    rval = sass.compile(
        output_style=output_style,
        precision=precision,
        include_paths=include_paths,
        **args
    )

    # Write output.
    # sass.compile() will return None if used with dirname.
    # If used with filename, it will return a string of file contents.
    if rval and outfile:
        # If we got a css and sourcemap tuple, write the sourcemap.
        if isinstance(rval, tuple):
            map_outfile = outfile + ".map"
            outfile_dir = os.path.dirname(map_outfile)
            if not os.path.exists(outfile_dir):
                os.makedirs(outfile_dir, exist_ok=True)
            file = open(map_outfile, "w", encoding="utf8")
            file.write(rval[1])
            file.close()
            rval = rval[0]

        # Write the outputted css to file.
        outfile_dir = os.path.dirname(outfile)
        if not os.path.exists(outfile_dir):
            os.makedirs(outfile_dir, exist_ok=True)
        file = open(outfile, "w", encoding="utf8")
        file.write(rval)
        file.close()