import logging
import sys
from src.app import ThermalFileDialog

LOGGER = logging.getLogger(__name__)

def main():
    win = ThermalFileDialog()
    # win.mainloop()

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(filename)12s:L%(lineno)3s [%(levelname)8s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        stream=sys.stdout
    )
    main()