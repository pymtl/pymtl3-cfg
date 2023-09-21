'''
==========================================================================
ReqRespRouter.py
==========================================================================
A req/resp router that routes incoming requests based on the address and
sends back corresponding responses. It is parameterized by the routing
logic.

Author : Yanghui Ou
  Date : Sep 19, 2023
'''
from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import IStreamIfc, OStreamIfc

from .Router import Router
from .DummyRoutingLogic import DummyRoutingLogic


class ReqRespRouter( Component ):
  def construct( s, PacketType, IDType, RoutingLogic, num_terminals ):

    # Local parameters
    s.num_terminals = num_terminals

    # Interface
    s.minion_req  = IStreamIfc( PacketType )
    s.minion_resp = OStreamIfc( PacketType )

    s.master_req  = [ OStreamIfc( PacketType ) for _ in range( s.num_terminals ) ]
    s.master_resp = [ IStreamIfc( PacketType ) for _ in range( s.num_terminals ) ]

    # Components
    s.req_router = Router( PacketType, IDType, RoutingLogic,
                           num_inports=1, num_outports=s.num_terminals )
    s.resp_router = Router( PacketType, IDType, DummyRoutingLogic,
                            num_inports=s.num_terminals, num_outports=1 )

    # Connections
    s.minion_req  //= s.req_router.recv[0]
    s.minion_resp //= s.resp_router.send[0]

    for i in range( s.num_terminals ):
      s.master_req[i]  //= s.req_router.send[i]
      s.master_resp[i] //= s.resp_router.recv[i]

    # ID port of the router is not used since we expect there is only one
    # ReqRespRouter in the system.
    s.req_router.i_id  //= 0
    s.resp_router.i_id //= 0

  def line_trace( s ):
    return f'{s.req_router.line_trace()} <> {s.resp_router.line_trace()}'
