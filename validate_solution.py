# -*- coding: utf-8 -*-

import json
import pprint
import requests
import sys


def validate():
    nr_params_command_line = len(sys.argv[1:])
    if nr_params_command_line == 0:
        print("Erro: Sintaxe incorreta!")
        print("Sintaxe: python validate_solution.py solucao.xml")
        sys.exit(0)

    username = 'marlucioapires@gmail.com'
    password = 'N@qxk#2C'
    source_file = sys.argv[1]
    upload_url = "https://www.itc2019.org/itc2019-validator"
    headers = {"Content-Type": "text/xml;charset=UTF-8"}

    file = open(source_file, 'rb')
    r = requests.post(upload_url, auth=(username, password), data=file, headers=headers)

    if r.status_code == requests.codes.ok:
        pprint.pprint(json.loads(r.content))


if __name__ == "__main__":
    validate()
    sys.exit(0)
