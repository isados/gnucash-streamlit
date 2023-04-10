import os
from streamlit.web import bootstrap
from streamlit import config as _config

def main():
    dirname = os.path.dirname(__file__)
    config_filename = os.path.join(dirname, '.streamlit/config.toml')
    _config.CONFIG_FILENAMES.append(config_filename)
    _config.set_option("server.headless", True)

    exec_filename = os.path.join(dirname, 'report.py')
    args = []
    bootstrap.run(exec_filename, '', args, flag_options=[])


if __name__ == '__main__':
    main()
