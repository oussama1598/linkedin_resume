import json
import os
import tempfile
import string
import random
import shutil
import subprocess as sp
import re


def get_value_from_data(data, chained_key):
    keys = chained_key.split(".")

    value = data

    for key in keys:
        value = value[key]

    return value


def load_data_from_json(json_file_path):
    if not os.path.exists(json_file_path):
        raise Exception(f"The provided json file does not exist ({json_file_path}).")

    with open(json_file_path, 'r') as file:
        return json.loads(file.read())


def load_tex_template(tex_file_path):
    if not os.path.exists(tex_file_path):
        raise Exception(f"The provided template folder does not exist ({tex_file_path}).")

    with open(tex_file_path, 'r') as file:
        return file.read()


def escape(value):
    return value.translate(str.maketrans({
        '&': r'\&'
    }))


def check_for_conditions_for_macro(template, key, value):
    macros = [
        [
            'MINUS',
            lambda x: (x and '-') or ''
        ],
        [
            'LAST_SLASH',
            lambda x: x.split('/')[-1]
        ]
    ]

    for macro in macros:
        template = template.replace(f'{macro[0]}({key})', macro[1](value))

    return template


def parse_str(template, key, value):
    if type(value) is list:
        return template.replace(key, escape(', '.join(value)))

    template = check_for_conditions_for_macro(template, key, value)

    return template.replace(key, escape(value))


def parse_list(tex_template, key, elements_list):
    # get the template
    template_name = key['template']
    template_match = re.search(f'{template_name}([\\s\\S]*?)END_{template_name}', tex_template)
    template_placeholder = template_match.group(0)

    # remove the template placeholder from the tex file
    tex_template = tex_template.replace(template_placeholder, '')

    templates = []

    for element in elements_list:
        template = re.sub(rf'{template_name}|END_{template_name}', '', template_placeholder).strip()

        for template_key in key:
            if template_key == 'template' or template_key == 'join':
                continue

            if type(key[template_key]) is str:
                template = parse_str(template, key[template_key], element[template_key])

            if type(key[template_key]) is dict:
                template = parse_list(template, key[template_key], element[template_key])

        templates.append(template)

    tempaltes_str = key['join'].join(templates)

    return tex_template[:template_match.start()] + tempaltes_str + tex_template[template_match.start():]


def parse_tex_template(tex_file_path, data):
    tex_raw_template = load_tex_template(tex_file_path)
    parse_mapping = load_data_from_json(
        os.path.join(os.path.dirname(__file__), "../parse_mapping.json")
    )

    for key in parse_mapping:
        parsed_key = parse_mapping[key]
        value = get_value_from_data(data, key)

        if type(parsed_key) is str:
            tex_raw_template = parse_str(tex_raw_template, parsed_key, value)

        if type(parsed_key) is dict:
            tex_raw_template = parse_list(tex_raw_template, parsed_key, value)

    return tex_raw_template


def save_parsed_tex_template(save_path, content):
    with open(save_path, 'w') as file:
        file.write(content)


def generate_tex_file_from_data(json_file_path, output_pdf, template_name):
    user_data = load_data_from_json(json_file_path)

    template_source = f"./resume_templates/{template_name}"

    temp_dir = tempfile.gettempdir()
    random_dir = ''.join([random.choice(string.ascii_letters) for i in range(16)])
    temp_folder = os.path.join(temp_dir, random_dir)

    template_tex_file = os.path.join(temp_folder, 'resume-template.tex')

    # Copy the template folder to a temp directory
    shutil.copytree(template_source, temp_folder)

    # parse the template and replace all the necessary keywords
    parsed_tex_template = parse_tex_template(template_tex_file, user_data)

    # save the newly created and parsed tex template to the temp folder
    save_parsed_tex_template(template_tex_file, parsed_tex_template)

    # generate the pdf file
    command = f'xelatex -interaction=nonstopmode {template_tex_file}'
    FNULL = open(os.devnull, 'w')

    sp.call(command, shell=True, cwd=temp_folder, stdout=FNULL)

    # copy the pdf to the desired output
    shutil.copy2(template_tex_file.replace(".tex", ".pdf"), output_pdf)

    # clean the temp folder
    shutil.rmtree(temp_folder)

    # open file
    sp.run(['xdg-open', output_pdf], check=True)
