
import os, webbrowser
from app_plugin import app,context,SERVER_PORT
import atexit
import sys
import logging

logformat = f"%(asctime)s - %(name)s - %(levelname)s - %(message)s"
handler = logging.FileHandler('lintbotApp.log')
formatter = logging.Formatter(logformat)
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO, format=logformat)
logger = logging.getLogger("linebotApp")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

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

