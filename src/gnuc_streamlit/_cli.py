import os
from streamlit.web import bootstrap
from streamlit import config as _config

def main():
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'report.py')

    _config.set_option("server.headless", True)
    args = []

    bootstrap.run(filename, '', args, flag_options=[])


if __name__ == '__main__':
    main()
