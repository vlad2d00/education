import os

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

from education.settings import BASE_DIR
from education.utils.bytes_convertor import b_to_mb
from education.utils.datetime_service import datetime_now

gauth = None
# gauth = GoogleAuth()
# gauth.LocalWebserverAuth()


def backup(compress: bool = False,
           upload_to_drive: bool = False,
           is_save: bool = True):

    dt = datetime_now()
    file_base_name = dt.strftime('%Y-%m-%d-%H%M%S') + '.dump'
    command = 'python manage.py dbbackup --noinput'

    if compress:
        command += ' -z'
        file_base_name += '.gz'

    file_name = os.path.join(BASE_DIR, 'backup', file_base_name)

    command += ' -o' + file_name

    print('Creating a database backup...')
    os.system(command)

    with open(os.path.join(BASE_DIR, 'backup', file_name), 'rb') as f:
        data = f.read()
    print(f'Database backup \"{file_base_name}\" created! Size: {round(b_to_mb(len(data)), 3)} Mb')

    if upload_to_drive:
        drive = GoogleDrive(gauth)
        file = drive.CreateFile({'title': file_base_name})
        file.SetContentFile(file_name)
        file.Upload()

    if not is_save:
        os.remove(file_name)


def dump_data(app_label: str = None,
              model_name: str = None,
              format_: str = None,
              indent: int = 4):
    if app_label:
        if model_name:
            file_name = f'{app_label}.{model_name}.{format_}'
            target = f'{app_label}.{model_name}'
        else:
            file_name = f'{app_label}.{format_}'
            target = f'{app_label}'

        os.system(f'python manage.py dumpdata {target} '
                  f'{"--indent " + str(indent) if indent else ""} '
                  f'{"--format " + format_ if format_ else ""} '
                  f'> {file_name}')

    else:
        file_name = f'db.{format_}'
        target = f'--exclude auth.permission --exclude contenttypes'

    os.system(f'python manage.py dumpdata {target} '
              f'{"--indent " + str(indent) if indent else ""} '
              f'{"--format " + format_ if format_ else ""} '
              f'> {file_name}')

    return file_name


def load_data(file_name: str):
    os.system(f'python manage.py loaddata {file_name}')
