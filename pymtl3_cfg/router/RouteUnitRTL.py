'''
==========================================================================
RouteUnitRTL.py
==========================================================================
Generic route unit parameterized by routing logic.

The routing logic is a component that takes in a packet and outputs an
index indicating which output port the packet should be routed to. The
routing logic component should have the following interface:

Input:
  - i_pkt: PacketType
  - i_id : IDType

Output:
  - o_val: BitsN, where N is the number of output ports

The 'o_val' is a one-hot encoding of the desired output port for the
packet. for example, if `o_val` is 0b0010, then the packet should be
routed to the second output port.

Broadcasting can be achieved by setting multiple bits in `o_val` to 1. For
example, if `o_val` is 0b0110, then the packet should be routed to the
second and third output ports.

TODO: reuse pymtl3_net's RouteUnit once it's ready.

Author : Yanghui Ou
  Date : Sep 18, 2023
'''
from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import IStreamIfc, OStreamIfc


class RouteUnitRTL( Component ):
  def construct( s, PacketType, IDType, RoutingLogic, num_outports ):

    # Local parameters
    s.num_outports = num_outports

    # Interface
    s.i_id  = InPort( IDType )
    s.recv = IStreamIfc( PacketType )
    s.send = [ OStreamIfc( PacketType ) for _ in range( s.num_outports ) ]

    # Components
    s.routing_logic = RoutingLogic( PacketType, IDType, num_outports )

    # Wires and resgisters
    # A one-hot encoded vector indicating which output ports are blocking
    # the message from being sent.
    s.blocking = Wire( s.num_outports )

    # Connections and assignments
    s.routing_logic.i_id  //= s.i_id
    s.routing_logic.i_pkt //= s.recv.msg

    for i in range( s.num_outports ):
      s.send[i].msg //= s.recv.msg
      s.send[i].val //= lambda: s.routing_logic.o_val[i] & s.recv.val

    @update
    def up_blocking():
      s.blocking @= 0
      if s.recv.val:
        for i in range( s.num_outports ):
          s.blocking[i] @= s.routing_logic.o_val[i] & ~s.send[i].rdy

    s.recv.rdy //= lambda: ~reduce_or( s.blocking )

  def line_trace( s ):
    out_str = "|".join([ str(x) for x in s.send ])
    return f'{s.recv}({s.routing_logic.o_val}){out_str}'
