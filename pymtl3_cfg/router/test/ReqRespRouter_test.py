'''
==========================================================================
ReqRespRouter_test.py
==========================================================================
Test cases for the ReqRespRouter.

Author : Yanghui Ou
  Date : Sep 19, 2023
'''
import pytest
from pymtl3 import *
from pymtl3.stdlib.stream import StreamSinkFL, StreamSourceFL
from pymtl3.stdlib.test_utils import config_model_with_cmdline_opts

from ...ifcs.msg_types import mk_cfg_pkt_type
from ..ReqRespRouter import ReqRespRouter


addr_nbits = 18
TestPkt = mk_cfg_pkt_type( type_nbits=2, addr_nbits=addr_nbits, data_nbits=32 )


class TestRoutingLogic( Component ):
  def construct( s, PacketType, IDType, num_outports ):
    # Local parameters
    assert num_outports >= 4

    # Interface
    s.i_id  = InPort( IDType )
    s.i_pkt = InPort( PacketType )
    s.o_val = OutPort( mk_bits( num_outports ) )

    # Routing logic
    @update
    def up_routing_logic():
      if s.i_pkt.addr < 0x1000:
        s.o_val @= 0b1
      elif s.i_pkt.addr < 0x2000:
        s.o_val @= 0b10
      elif s.i_pkt.addr < 0x3000:
        s.o_val @= 0b100
      else:
        s.o_val @= 0b1000


def test_elaborate( ):
  dut = ReqRespRouter( TestPkt, mk_bits( addr_nbits ), TestRoutingLogic,
                       num_terminals=4 )
  dut.apply( DefaultPassGroup() )
  dut.sim_reset()
  for _ in range(10): dut.sim_tick()


# TODO: add more test cases once config terminal is ready
