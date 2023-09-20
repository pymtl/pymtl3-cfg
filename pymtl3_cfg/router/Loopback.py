'''
==========================================================================
Loopback.py
==========================================================================
Loopback unit.

Author : Yanghui Ou
  Date : May 24, 2022
'''
from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import IStreamIfc, OStreamIfc
from pymtl3.stdlib.primitive.registers import Reg

class Loopback( Component ):
  def construct( s, CfgPkt ):

    # Interface
    s.loopback_en = InPort()
    s.minion_req  = IStreamIfc( CfgPkt )
    s.minion_resp = OStreamIfc( CfgPkt )
    s.master_req  = OStreamIfc( CfgPkt )
    s.master_resp = IStreamIfc( CfgPkt )

    # Component
    s.lpbk_en_r = Reg( Bits1 )

    # Connections and assignments
    s.lpbk_en_r.in_ //= s.loopback_en

    s.master_req.msg  //= s.minion_req.msg
    s.master_req.val  //= lambda: s.minion_req.val & ~s.lpbk_en_r.out
    s.master_resp.rdy //= lambda: s.minion_resp.rdy & ~s.lpbk_en_r.out

    s.minion_req.rdy  //= lambda: s.master_req.rdy if ~s.lpbk_en_r.out else s.minion_resp.rdy
    s.minion_resp.val //= lambda: s.master_resp.val if ~s.lpbk_en_r.out else s.minion_req.val

    # Logic
    @update
    def up_minion_resp_msg():
      s.minion_resp.msg @= s.master_resp.msg
      if s.lpbk_en_r.out:
        s.minion_resp.msg.type_ @= s.minion_req.msg.type_
        s.minion_resp.msg.addr  @= s.minion_req.msg.addr
        s.minion_resp.msg.data  @= s.minion_req.msg.data

  def line_trace( s ):
    return f'{s.minion}({s.lpbk_en_r.out}){s.master}'
