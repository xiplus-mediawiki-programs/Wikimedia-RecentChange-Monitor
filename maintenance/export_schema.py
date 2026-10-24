# -*- coding: utf-8 -*-
# Dump database structure to database.sql
import configparser
import os
import re
import subprocess
import tempfile

basedir = os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../')

config = configparser.ConfigParser()
config.read_file(open(os.path.join(basedir, 'config.ini'), encoding='utf8'))

with tempfile.NamedTemporaryFile('w', suffix='.cnf') as cnf:
    cnf.write('[client]\nhost={}\nuser={}\npassword="{}"\n'.format(
        config.get('database', 'host'),
        config.get('database', 'user'),
        config.get('database', 'passwd'),
    ))
    cnf.flush()
    output = subprocess.run([
        'mysqldump',
        '--defaults-extra-file=' + cnf.name,
        '--no-data',
        '--skip-add-drop-table',
        '--skip-comments',
        '--skip-dump-date',
        config.get('database', 'db'),
    ], check=True, stdout=subprocess.PIPE).stdout.decode('utf8')

output = re.sub(r' AUTO_INCREMENT=\d+', '', output)

with open(os.path.join(basedir, 'database.sql'), 'w', encoding='utf8') as f:
    f.write(output)
