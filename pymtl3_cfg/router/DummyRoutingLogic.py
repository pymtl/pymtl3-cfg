'''
==========================================================================
DummyRoutingLogic.py
==========================================================================
A dummy routing logic that routes all requests to the first output port.

Author : Yanghui Ou
  Date : Sep 18, 2023
'''
from pymtl3 import *

class DummyRoutingLogic( Component ):
  def construct( s, PacketType, IDType, num_outports ):
    # Interface
    s.i_id  = InPort( IDType )
    s.i_pkt = InPort( PacketType )
    s.o_val = OutPort( mk_bits( num_outports ) )

    # Connections and assignments
    s.o_val //= 0b1
  
  def line_trace( s ):
    return f"{s.i_pkt}({s.i_id}){s.o_val.bin()}"
