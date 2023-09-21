'''
==========================================================================
ConfigTerminal_test.py
==========================================================================
Test cases for ConfigTerminal.

Author : Yanghui Ou
  Date : Sep 20, 2023
'''
import pytest

from pymtl3 import *
from pymtl3.stdlib.stream.StreamSinkFL import StreamSinkFL
from pymtl3.stdlib.stream.StreamSourceFL import StreamSourceFL
from pymtl3.stdlib.test_utils import config_model_with_cmdline_opts, run_sim

from ...ifcs.msg_types import CfgType, mk_cfg_pkt_type
from ..ConfigTerminal import ConfigTerminal


TestPkt = mk_cfg_pkt_type( type_nbits=2, addr_nbits=16, data_nbits=32)
wr = CfgType.WRITE
rd = CfgType.READ


def mk_req_resp_msgs( lst ):
  req_msgs =  [ TestPkt( type_, addr, data ) for type_, addr, data in lst[0::2] ]
  resp_msgs = [ TestPkt( type_, addr, data ) for type_, addr, data in lst[1::2] ]
  return req_msgs, resp_msgs


@pytest.mark.parametrize( "num_config_regs, num_status_regs",
                          [ (1, 0), (0, 1), (2, 2) ] )
def test_elaborate( num_config_regs, num_status_regs ):
  dut = ConfigTerminal( TestPkt, num_config_regs=num_config_regs,
                        num_status_regs=num_status_regs )
  dut.elaborate()
  dut.apply( DefaultPassGroup() )
  dut.sim_reset()
  for _ in range(10): dut.sim_tick()


class TestHarness( Component ):
  def construct( s, PacketType, req_msgs, resp_msgs, num_config_regs=2,
                 num_status_regs=2 ):
    s.src  = StreamSourceFL( PacketType, req_msgs )
    s.sink = StreamSinkFL  ( PacketType, resp_msgs )

    s.dut = ConfigTerminal( PacketType, num_config_regs=num_config_regs,
                            num_status_regs=num_status_regs )

    s.src.ostream  //= s.dut.minion_req
    s.sink.istream //= s.dut.minion_resp

    for i in range( num_status_regs ):
      s.dut.i_status[i] //= num_config_regs + i

  def done( s ):
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    return s.dut.line_trace()


@pytest.mark.parametrize( "num_config_regs, num_status_regs",
                          [ (1, 0), (2, 2) ] )
def test_one_config_wr_rd( cmdline_opts, num_config_regs, num_status_regs ):
  req_resps = [
    (wr, 0x1000, 0xdeadbeef), (wr, 0x1000, 0),
    (rd, 0x1000, 0         ), (rd, 0x1000, 0xdeadbeef),
  ]
  req_msgs, resp_msgs = mk_req_resp_msgs( req_resps )
  th = TestHarness( TestPkt, req_msgs, resp_msgs, num_config_regs,
                    num_status_regs )
  config_model_with_cmdline_opts( th, cmdline_opts, duts=['dut'] )
  run_sim( th, cmdline_opts )


@pytest.mark.parametrize( "num_config_regs, num_status_regs",
                          [ (0, 1), (2, 2) ] )
def test_one_status_rd( cmdline_opts, num_config_regs, num_status_regs ):
  req_resps = []
  for i in range( num_status_regs ):
    req_resps.append( (rd, 0x1000 + num_config_regs + i, 0) )
    req_resps.append( (rd, 0x1000 + num_config_regs + i, num_config_regs + i) )

  req_msgs, resp_msgs = mk_req_resp_msgs( req_resps )
  th = TestHarness( TestPkt, req_msgs, resp_msgs, num_config_regs,
                    num_status_regs )
  config_model_with_cmdline_opts( th, cmdline_opts, duts=['dut'] )
  run_sim( th, cmdline_opts )


@pytest.mark.parametrize( "sink_delay", [ 0, 20 ] )
def test_stream_reqs( cmdline_opts, sink_delay ):
  num_config_regs = 2
  num_status_regs = 2
  req_resps = [
    (wr, 0x1000, 0xdeadbeef), (wr, 0x1000, 0),
    (rd, 0x1000, 0         ), (rd, 0x1000, 0xdeadbeef),
    (wr, 0x1001, 0xc001cafe), (wr, 0x1001, 0),
    (rd, 0x1001, 0         ), (rd, 0x1001, 0xc001cafe),
    (rd, 0x1002, 0         ), (rd, 0x1002, 2),
    (rd, 0x1003, 0         ), (rd, 0x1003, 3),
  ]
  req_msgs, resp_msgs = mk_req_resp_msgs( req_resps )
  th = TestHarness( TestPkt, req_msgs, resp_msgs )
  th.set_param( 'top.sink.construct', initial_delay=sink_delay )
  config_model_with_cmdline_opts( th, cmdline_opts, duts=['dut'] )
  run_sim( th, cmdline_opts )
