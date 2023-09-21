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
from pymtl3.stdlib.test_utils import config_model_with_cmdline_opts, run_sim

from ...ifcs.msg_types import CfgType, mk_cfg_pkt_type
from ...terminal.ConfigTerminal import ConfigTerminal
from ..ReqRespRouter import ReqRespRouter


addr_nbits = 16
TestPkt = mk_cfg_pkt_type( type_nbits=2, addr_nbits=addr_nbits, data_nbits=32 )
wr = CfgType.WRITE
rd = CfgType.READ


def mk_req_resp_msgs( lst ):
  req_msgs =  [ TestPkt( type_, addr, data ) for type_, addr, data in lst[0::2] ]
  resp_msgs = [ TestPkt( type_, addr, data ) for type_, addr, data in lst[1::2] ]
  return req_msgs, resp_msgs


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


class TestHarness( Component ):
  def construct( s, PacketType, req_msgs, resp_msgs, num_terminals=4 ):
    s.src  = StreamSourceFL( PacketType, req_msgs )
    s.sink = StreamSinkFL  ( PacketType, resp_msgs, ordered=False )
    s.dut  = ReqRespRouter( PacketType, mk_bits( addr_nbits ),
                            TestRoutingLogic, num_terminals=num_terminals )
    s.cfg_terminals = [
      ConfigTerminal( PacketType, num_config_regs=1, num_status_regs=0 )
      for _ in range(num_terminals) ]

    s.src.ostream //= s.dut.minion_req
    s.sink.istream //= s.dut.minion_resp

    for i in range( num_terminals ):
      s.cfg_terminals[i].minion_req  //= s.dut.master_req[i]
      s.cfg_terminals[i].minion_resp //= s.dut.master_resp[i]

  def done( s ):
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    return s.dut.line_trace()

@pytest.mark.parametrize( "sink_delay", [0, 20] )
def test_rd_wr_one_debug_unit( cmdline_opts, sink_delay ):
  req_resps = [
    (wr, 0x0000, 0xdeadbeef), (wr, 0x0000, 0),
    (rd, 0x0000, 0         ), (rd, 0x0000, 0xdeadbeef),
  ]
  req_msgs, resp_msgs = mk_req_resp_msgs( req_resps )
  th = TestHarness( TestPkt, req_msgs, resp_msgs )
  th.set_param( "top.sink.construct", initial_delay=sink_delay )
  config_model_with_cmdline_opts( th, cmdline_opts, duts=['dut'] )
  run_sim( th, cmdline_opts )
  assert th.cfg_terminals[0].o_config[0] == 0xdeadbeef

@pytest.mark.parametrize( "sink_delay", [0, 20] )
def test_rd_wr_all_debug_unit( cmdline_opts, sink_delay ):
  req_resps = [
    # debug unit 0
    (wr, 0x0000, 0xdeadbeef), (wr, 0x0000, 0),
    (rd, 0x0000, 0         ), (rd, 0x0000, 0xdeadbeef),
    # debug unit 1
    (wr, 0x1000, 0xcafec001), (wr, 0x1000, 0),
    (rd, 0x1000, 0         ), (rd, 0x1000, 0xcafec001),
    # debug unit 2
    (wr, 0x2000, 0xbadbed00), (wr, 0x2000, 0),
    (rd, 0x2000, 0         ), (rd, 0x2000, 0xbadbed00),
    # debug unit 3
    (wr, 0x3000, 0xc01dbeef), (wr, 0x3000, 0),
    (rd, 0x3000, 0         ), (rd, 0x3000, 0xc01dbeef),
  ]
  req_msgs, resp_msgs = mk_req_resp_msgs( req_resps )
  th = TestHarness( TestPkt, req_msgs, resp_msgs )
  th.set_param( "top.sink.construct", initial_delay=sink_delay )
  config_model_with_cmdline_opts( th, cmdline_opts, duts=['dut'] )
  run_sim( th, cmdline_opts )
  assert th.cfg_terminals[0].o_config[0] == 0xdeadbeef
  assert th.cfg_terminals[1].o_config[0] == 0xcafec001
  assert th.cfg_terminals[2].o_config[0] == 0xbadbed00
  assert th.cfg_terminals[3].o_config[0] == 0xc01dbeef
