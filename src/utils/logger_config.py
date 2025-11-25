import logging
import os

def setup_logging():
    
    os.makedirs("logs", exist_ok=True)
    
    log_file_path = "logs/"+"rss-collector"+".log"

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S',
        handlers=[
            logging.FileHandler(log_file_path, encoding='utf-8'),
            # logging.StreamHandler()
        ]
    )

# def setup_logging(level=logging.INFO):
#     logging.basicConfig(
#         level=level,
#         format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#         datefmt='%H:%M:%S',
#         handlers=[
#             # logging.StreamHandler(sys.stdout),  
#             logging.FileHandler('logs/db.log')      
#         ]
#     )


# setup_logging()