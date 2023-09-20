'''
==========================================================================
PushPull2ReqRespAdapter_test.py
==========================================================================
Unit tests for PushPull2ReqRespAdapter.

Author : Yanghui Ou
  Date : May 24, 2022
'''
from pymtl3 import *
from ..PushPull2ReqRespAdapter import PushPull2ReqRespAdapter
from ...ifcs.msg_types import CfgType, mk_cfg_pkt_type


#-------------------------------------------------------------------------
# Local parameters
#-------------------------------------------------------------------------

wr = CfgType.WRITE
rd = CfgType.READ
CfgPkt = mk_cfg_pkt_type()

#-------------------------------------------------------------------------
# Helper functions
#-------------------------------------------------------------------------

def do_push( m, valid, stall, payload ):
  m.push.en             @= 1
  m.push.msg.payload    @= payload
  m.push.msg.valid @= valid
  m.push.msg.stall @= stall
  m.sim_tick()
  m.push.en             @= 0
  m.push.msg.valid @= 0 
  m.push.msg.stall @= 0
  m.sim_eval_combinational()

def do_pull( m ):
  m.pull.en @= 1
  m.sim_tick()
  m.pull.en @= 0
  m.sim_eval_combinational()

def check_pull_msg( m, valid, stall, payload ):
  m.pull.en @= 1
  m.sim_eval_combinational()

  assert m.pull.msg.valid == valid
  assert m.pull.msg.stall  == stall
  if m.pull.msg.valid:
    assert m.pull.msg.payload == payload

  m.sim_tick()
  m.pull.en @= 0

def do_resp( m, msg ):
  while not m.resp.rdy: m.sim_tick()
  m.resp.val @= b1(1)
  m.resp.msg @= msg
  m.sim_tick()
  m.resp.val @= b1(0)
  m.sim_tick()

#-------------------------------------------------------------------------
# test_sanity_check
#-------------------------------------------------------------------------

def test_sanity_check():
  dut = PushPull2ReqRespAdapter( CfgPkt )
  dut.elaborate()
  dut.apply( DefaultPassGroup(linetrace=True) )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()

#-------------------------------------------------------------------------
# test_initial_pull
#-------------------------------------------------------------------------

def test_initial_pull():
  dut = PushPull2ReqRespAdapter( CfgPkt )
  dut.elaborate()
  dut.apply( DefaultPassGroup(linetrace=True) )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()

  check_pull_msg( dut, 0, 0, 0 )
  check_pull_msg( dut, 0, 0, 0 )

#-------------------------------------------------------------------------
# test_push_one_msg
#-------------------------------------------------------------------------

def test_push_one_msg():
  dut = PushPull2ReqRespAdapter( CfgPkt )
  dut.elaborate()
  dut.apply( DefaultPassGroup(linetrace=True) )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()

  dut.req.rdy @= b1(1)

  check_pull_msg( dut, 0, 0, 0 )
  do_pull( dut )

  for _ in range( 10 ): dut.sim_tick()

  do_push( dut, 1, 0, CfgPkt(wr, 0x200, 0xdeadbeef) )

  while not dut.req.val:
    dut.sim_tick()

  assert dut.req.msg == CfgPkt(wr, 0x200, 0xdeadbeef)
  dut.sim_tick()
  dut.sim_tick()

#-------------------------------------------------------------------------
# test_req_stall
#-------------------------------------------------------------------------

def test_req_stall():
  dut = PushPull2ReqRespAdapter( CfgPkt )
  dut.elaborate()
  dut.apply( DefaultPassGroup(linetrace=True) )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()

  dut.req.rdy @= b1(0)

  check_pull_msg( dut, 0, 0, 0 )
  do_pull( dut )

  for _ in range( 10 ): dut.sim_tick()
  do_push( dut, 1, 0, CfgPkt(wr, 0x200, 0xdeadbeef) )

  for _ in range( 10 ): dut.sim_tick()
  check_pull_msg( dut, 0, 0, 0 )

  for _ in range( 10 ): dut.sim_tick()
  do_push( dut, 1, 0, CfgPkt(wr, 0x204, 0xc001c0de) )

  for _ in range( 10 ): dut.sim_tick()
  check_pull_msg( dut, 0, 1, 0 )

  for _ in range( 10 ): dut.sim_tick()
  do_push( dut, 0, 0, CfgPkt(wr, 0x200, 0xdeadbeef) )

  for _ in range( 10 ): dut.sim_tick()
  check_pull_msg( dut, 0, 1, 0 )
  dut.sim_tick()
  dut.sim_tick()

#-------------------------------------------------------------------------
# test_resp_stall
#-------------------------------------------------------------------------

def test_req_stall():
  dut = PushPull2ReqRespAdapter( CfgPkt )
  dut.elaborate()
  dut.apply( DefaultPassGroup(linetrace=False) )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()

  dut.req.rdy @= b1(1)

  check_pull_msg( dut, 0, 0, 0 )

  for _ in range( 10 ): dut.sim_tick()
  do_push( dut, 1, 1, CfgPkt(rd, 0x200, 0) )

  do_resp( dut, CfgPkt(rd, 0, 0xdeadbeef) )

  for _ in range( 10 ): dut.sim_tick()
  check_pull_msg( dut, 0, 0, 0 )

  for _ in range( 10 ): dut.sim_tick()
  do_push( dut, 1, 0, CfgPkt(rd, 0x204, 0) )

  for _ in range( 10 ): dut.sim_tick()
  check_pull_msg( dut, 1, 0, CfgPkt(rd, 0, 0xdeadbeef) )

  dut.sim_tick()
  dut.sim_tick()
