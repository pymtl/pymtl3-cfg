'''
==========================================================================
ReqRouter.py
==========================================================================

Author : Yanghui Ou
  Date : Sep 12, 2022
'''

from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import RecvIfcRTL, SendIfcRTL

from .InputUnitRTL  import InputUnitRTL
from .ReqRouteUnit import ReqRouteUnit
from .OutputUnitRTL import OutputUnitRTL

from ..ifcs.msg_types import CfgType, CfgReq, CfgResp

class ReqRouter( Component ):

  def construct( s ):

    # Local parameters

    s.num_inports  = 1
    s.num_outports = 5

    # Interface

    s.recv = RecvIfcRTL( CfgReq )
    s.send = [ SendIfcRTL( CfgReq ) for _ in range( s.num_outports ) ]

    # Components

    s.input_unit   = InputUnitRTL( CfgReq )
    s.route_unit   = ReqRouteUnit()
    s.output_units = [ OutputUnitRTL( CfgReq ) for _ in range( s.num_outports ) ]

    # Connections

    s.recv            //= s.input_unit.recv
    s.input_unit.send //= s.route_unit.recv

    for i in range( s.num_outports ):
      s.route_unit.send[i]   //= s.output_units[i].recv
      s.output_units[i].send //= s.send[i]

  def line_trace( s ):
    out_str = "|".join([ str(x) for x in s.send ])
    return f'{s.recv}(){out_str}'
