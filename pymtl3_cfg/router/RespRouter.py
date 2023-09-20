'''
==========================================================================
RespRouter.py
==========================================================================

Author : Yanghui Ou
  Date : Sep 12, 2022
'''

from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import RecvIfcRTL, SendIfcRTL

from .InputUnitRTL  import InputUnitRTL
from .SwitchUnitRTL import SwitchUnitRTL
from .OutputUnitRTL import OutputUnitRTL

from ..ifcs.msg_types import CfgResp

class RespRouter( Component ):
  def construct( s ):

    # Local parameters

    s.num_inports  = 5
    s.num_outports = 1

    # Interface

    s.recv = [ RecvIfcRTL( CfgResp ) for _ in range( s.num_inports) ]
    s.send = SendIfcRTL( CfgResp )

    # Components

    s.input_units = [ InputUnitRTL( CfgResp ) for _ in range( s.num_inports ) ]
    s.switch_unit = SwitchUnitRTL( CfgResp, s.num_inports )
    s.output_unit = OutputUnitRTL( CfgResp )

    # Connections

    for i in range( s.num_inports ):
      s.recv[i]             //= s.input_units[i].recv
      s.input_units[i].send //= s.switch_unit.recv[i]

    s.switch_unit.send //= s.output_unit.recv
    s.output_unit.send //= s.send

  def line_trace( s ):
    in_str = '|'.join([ str(x) for x in s.recv ])
    return f'{in_str}(){s.send}'

