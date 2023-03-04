
import os, webbrowser
from app_plugin import app,context,SERVER_PORT
import atexit
import sys
import logging

@atexit.register
def close_flask():
    logging.info('Close App') # print for debug purpose
   
if __name__ == "__main__":
    try: 
        ret = app.run(ssl_context=context,host="0.0.0.0" ,port=SERVER_PORT, threaded=True)
    except KeyboardInterrupt:
        logging.debug ('web app.py - user interrupt!')
    except BaseException as err:
        logging.debug ('web app.py exception occured!' + str(err))
    finally:
        logging.debug ('web app.py finally sec. - related resouces')

