# log.py
import logging

# Configurer le logger
logging.basicConfig(filename='api_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

logger = logging.getLogger(__name__)
