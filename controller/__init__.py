from  flask import Blueprint
modbus_controller       = Blueprint('modbus',__name__)
ssh_controller          = Blueprint('ssh',__name__)
stock_controller        = Blueprint('stock',__name__)
tickerOrder_controller  = Blueprint('tickerOrder',__name__)
from . import modbus
from . import ssh
from . import stock
from . import tickerOrder