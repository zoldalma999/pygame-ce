#!/usr/bin/env python

import sys
import os
import subprocess
import glob

rst_dir = 'docs'
rst_source_dir = os.path.join(rst_dir, 'reST')
rst_build_dir = os.path.join('docs', 'generated')
rst_doctree_dir = os.path.join(rst_build_dir, 'doctrees')
c_header_dir = os.path.join(rst_build_dir, 'c_headers')

special_paths = {
    "music": os.path.join("src", "mixer"),
    "pygame": os.path.join("src", "base")
}

def move_doc_headers():
    # will not find (and is fine): examples, cdrom, overlay, tests
    for file in glob.glob(f"{c_header_dir}/*.h"):
        is_sdl2 = False
        module_name = file.replace("_doc.h", "").replace(c_header_dir + os.sep, "")

        if "sdl2_" in module_name:
            is_sdl2 = True
            module_name = module_name.replace("sdl2_", "")

        args = ["src", "_sdl2", module_name]
        if not is_sdl2:
            args.pop(1)

        path = os.path.join(*args)
        file_name = f"{module_name}_doc.h"

        if module_name in special_paths:
            path = special_paths[module_name]

        if os.path.exists(path):
            os.replace(file, os.path.join(path, file_name))
            print(f"Moved file {file_name} from {file} to {os.path.join(path, file_name)}")
        else:
            print(f"Skipping file {file} because there is no destination")


def run():
    full_generation_flag = False
    for argument in sys.argv[1:]:
        if argument == 'full_generation':
            full_generation_flag = True
    try:
        subprocess_args = [sys.executable, '-m', 'sphinx',
                           '-b', 'html',
                           '-d', rst_doctree_dir,
                           '-D', f'headers_dest={c_header_dir}',
                           '-D', 'headers_mkdirs=1',
                           rst_source_dir,
                           rst_build_dir, ]
        if full_generation_flag:
            subprocess_args.append('-E')
        print("Executing sphinx in subprocess with args:", subprocess_args)
        retcode = subprocess.run(subprocess_args).returncode
        if retcode != 0:
            return retcode

        move_doc_headers()

    except Exception:
        print('---')
        print('Have you installed sphinx?')
        print('---')
        raise


if __name__ == '__main__':
    sys.exit(run())
