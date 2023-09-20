'''
==========================================================================
Router.py
==========================================================================
A generic router parameterized by the routing logic.

Author : Yanghui Ou
  Date : Sep 19, 2023
'''
from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import IStreamIfc, OStreamIfc

from .InputUnitRTL import InputUnitRTL
from .RouteUnitRTL import RouteUnitRTL
from .OutputUnitRTL import OutputUnitRTL
from .SwitchUnitRTL import SwitchUnitRTL


class Router( Component ):
  def construct( s, PacketType, IDType, RoutingLogic, num_inports, num_outports ):
    # Local parameters
    s.num_inports  = num_inports
    s.num_outports = num_outports

    # Interface
    s.recv = [ IStreamIfc( PacketType ) for _ in range( s.num_inports ) ]
    s.send = [ OStreamIfc( PacketType ) for _ in range( s.num_outports ) ]
    s.i_id = InPort( IDType )

    # Components
    s.input_units  = [ InputUnitRTL( PacketType ) for _ in range( s.num_inports ) ]
    s.route_units  = [ RouteUnitRTL( PacketType, IDType, RoutingLogic, s.num_outports )
                       for _ in range( s.num_inports ) ]

    # No switch unit is needed if there is only one input port
    if s.num_inports > 1:
      s.switch_unit  = [ SwitchUnitRTL( PacketType, s.num_inports )
                        for _ in range( s.num_outports ) ]

    s.output_units = [ OutputUnitRTL( PacketType ) for _ in range( s.num_outports ) ]

    # Connections
    for i in range( s.num_inports ):
      s.recv[i]             //= s.input_units[i].recv
      s.input_units[i].send //= s.route_units[i].recv
      s.route_units[i].i_id //= s.i_id

    if s.num_inports > 1:
      for i in range( s.num_inports ):
        for j in range( s.num_outports):
          s.route_units[i].send[j] //= s.switch_unit[j].recv[i]

      for j in range( s.num_outports ):
        s.switch_unit[j].send //= s.output_units[j].recv
        s.output_units[j].send //= s.send[j]

    # Skip the switch unit if there is only one input port
    else:
      for j in range( s.num_outports ):
        s.route_units[0].send[j] //= s.output_units[j].recv
        s.output_units[j].send //= s.send[j]

  def line_trace( s ):
    return ("|".join([ str(x) for x in s.recv ]) + "()" +
            "|".join([ str(x) for x in s.send ]))
