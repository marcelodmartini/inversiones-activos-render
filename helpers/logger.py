import logging
import sys

# Crear logger global
logger = logging.getLogger("app_logger")
logger.setLevel(logging.DEBUG)

# Formato de log
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Log a consola (stdout)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)

# Evitar agregar múltiples handlers si se recarga
if not logger.hasHandlers():
    logger.addHandler(console_handler)

# Función de uso rápido
def log_info(message):
    logger.info(message)

def log_warning(message):
    logger.warning(message)

def log_error(message):
    logger.error(message)

def log_debug(message):
    logger.debug(message)