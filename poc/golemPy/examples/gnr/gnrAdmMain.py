import logging
import logging.config
import os
import sys

sys.path.append(os.environ.get('GOLEM'))

from tools.uigen import gen_ui_files
gen_ui_files("ui")


from examples.gnr.GNRAdmApplicationLogic import GNRAdmApplicationLogic
from examples.gnr.Application import GNRGui



from examples.gnr.ui.MainWindow import GNRMainWindow
from examples.gnr.customizers.GNRAdministratorMainWindowCustomizer import GNRAdministratorMainWindowCustomizer
from GNRstartApp import start_app

def main():
    logging.config.fileConfig('logging.ini', disable_existing_loggers=False)

    logic   = GNRAdmApplicationLogic()
    app     = GNRGui(logic, GNRMainWindow)
    gui     = GNRAdministratorMainWindowCustomizer
    start_app(logic, app, gui,start_manager = True, start_info_server = True)

from multiprocessing import freeze_support

if __name__ == "__main__":
    freeze_support()
    main()
