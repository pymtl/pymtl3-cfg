'''
==========================================================================
PushPull2CfgRespAdapter.py
==========================================================================
Adapter that converts push/pull interface to latency-insensitive req/resp
interface.

Author : Yanghui Ou
  Date : May 24, 2022
'''
from pymtl3 import *
from pymtl3.stdlib.stream.queues import StreamNormalQueue as NormalQueueRTL
from pymtl3.stdlib.stream.ifcs import IStreamIfc, OStreamIfc

from ..ifcs import PushInIfc, PullOutIfc

#-------------------------------------------------------------------------
# Helper functions
#-------------------------------------------------------------------------

def mk_push_pull_bitstruct( Cfg ):
  return mk_bitstruct( f'PushPullPkt_{Cfg.__name__}', {
    'valid'   : Bits1,
    'stall'   : Bits1,
    'payload' : Cfg,
  })

#-------------------------------------------------------------------------
# PushPull2CfgRespAdapter
#-------------------------------------------------------------------------

class PushPull2ReqRespAdapter( Component ):
  def construct( s, Cfg, num_entries=2 ):
    # Local earameters
    s.PushPullPkt = mk_push_pull_bitstruct( Cfg )
    s.num_entries = num_entries

    # Interface
    s.push = PushInIfc ( s.PushPullPkt )
    s.pull = PullOutIfc( s.PushPullPkt )

    s.req  = OStreamIfc( Cfg )
    s.resp = IStreamIfc( Cfg )

    s.parity = OutPort()

    # Components
    s.req_q  = NormalQueueRTL( Cfg, num_entries=num_entries )
    s.resp_q = NormalQueueRTL( Cfg, num_entries=num_entries )

    # Wires
    s.req_send_xfer  = Wire()
    s.resp_send_xfer = Wire()

    # Registers
    s.resp_stall_r  = Wire()
    s.send_msg_bits = Wire( mk_bits(Cfg.nbits) )

    # Connections
    s.req  //= s.req_q.ostream
    s.resp //= s.resp_q.istream

    s.req_send_xfer  //= lambda: s.req_q.ostream.val  & s.req_q.ostream.rdy
    s.resp_send_xfer //= lambda: s.resp_q.ostream.val & s.resp_q.ostream.rdy

    s.req_q.istream.val  //= lambda: s.push.en & s.push.msg.valid
    s.req_q.istream.msg  //= lambda: s.push.msg.payload

    s.resp_q.ostream.rdy //= lambda: (s.pull.en & ~s.resp_stall_r & 
                                      ~(s.push.en & s.push.msg.stall))

    s.pull.msg.payload  //= s.resp_q.ostream.msg
    s.pull.msg.valid    //= s.resp_send_xfer
    s.pull.msg.stall    //= lambda: (
      ~s.req_q.istream.rdy | (s.req_q.istream.val & 
                              (s.req_q.count == s.num_entries-1) & 
                              ~s.req_send_xfer))

    s.parity //= lambda: reduce_xor( s.send_msg_bits )

    # Logic
    @update_ff
    def up_resp_stall_r():
      if s.reset:
        s.resp_stall_r <<= b1(0)
      elif ~s.resp_stall_r:
        s.resp_stall_r <<= s.push.en & s.push.msg.stall
      else:
        s.resp_stall_r <<= ~s.pull.en

    @update
    def up_send_msg_bits():
      s.send_msg_bits @= s.req.msg

  # Line trace
  def line_trace( s ):
    return f'{s.push}|{s.pull}({s.req_q.istream}|{s.resp_q.ostream}|{s.parity}<{s.resp_stall_r}>){s.req}|{s.resp}'
