from  flask import Blueprint
Modbus_controller       = Blueprint('Modbus',__name__)
SSH_controller          = Blueprint('SSH',__name__)
Stock_controller        = Blueprint('Stock',__name__)
TickerOrder_controller  = Blueprint('TickerOrder',__name__)
from . import Modbus
from . import SSH
from . import Stock
from . import TickerOrder