
import os, webbrowser
from app_plugin import app,context,SERVER_PORT
import atexit
import sys
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("linebotApp")

@atexit.register
def close_flask():
    logger.info('Close App') # print for debug purpose
   


if __name__ == "__main__":
    try: 
        ret = app.run(ssl_context=context,host="0.0.0.0" ,port=SERVER_PORT, threaded=True)
    except KeyboardInterrupt:
        logger.info ('user interrupt!')
    except BaseException as err:
        logger.info ('exception occured!' + str(err))
    finally:
        logger.info ('finally sec. - related resouces')

