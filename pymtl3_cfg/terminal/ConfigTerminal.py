'''
==========================================================================
ConfigTerminal.py
==========================================================================
A config terminal that takes in a config packet and sends back a response.
It contains a small register file that stores the configuration values.
The config terminal can have read-only status registers and/or
read-write config registers. The number of read-only and read-write
registers are parameterized.

The config terminal uses the LSBs of the address field to index into the
the config and status registers. The config registers occupy the lower
addresses and the status registers occupy the higher addresses. For
example, if the address field is 8 bits wide and there are 2 config
registers and 2 status registers, then the config registers will be
indexed by address 0x00 and 0x01 and the status registers will be indexed
by address 0x02 and 0x03.

Author : Yanghui Ou
  Date : June 13, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.primitive import Reg, RegEnRst
from pymtl3.stdlib.stream.ifcs import IStreamIfc, OStreamIfc
from pymtl3.stdlib.stream.queues import StreamNormalQueue

from ..ifcs.msg_types import CfgType


class ConfigTerminal( Component ):
  def construct( s, PacketType, num_config_regs=2, num_status_regs=2, qsize=1 ):
    # Local parameters
    assert (num_config_regs >= 0 and num_status_regs >= 0 and
            num_status_regs + num_config_regs > 0)

    s.num_config_regs = num_config_regs
    s.num_status_regs = num_status_regs
    s.total_num_regs  = num_config_regs + num_status_regs
    s.csr_addr_nbits  = max( clog2( s.total_num_regs ), 1 )
    s.DType           = PacketType.get_field_type( 'data' )

    # Minion Interface
    s.minion_req  = IStreamIfc( PacketType )
    s.minion_resp = OStreamIfc( PacketType )

    # Components
    s.req_q  = StreamNormalQueue( PacketType, num_entries=1 )
    s.resp_q = StreamNormalQueue( PacketType, num_entries=1 )

    # Config and status interface
    if s.num_config_regs > 0:
      s.o_config = [ OutPort( s.DType ) for i in range( s.num_config_regs ) ]
      s.config_r = [ RegEnRst( s.DType, reset_value=0 )
                     for i in range( s.num_config_regs ) ]
      for i in range( s.num_config_regs ):
        s.o_config[i]     //= s.config_r[i].out
        s.config_r[i].in_ //= s.req_q.ostream.msg.data

    if s.num_status_regs > 0:
      s.i_status = [ InPort ( s.DType ) for i in range( s.num_status_regs ) ]
      s.status_r = [ Reg( s.DType ) for i in range( s.num_status_regs ) ]

      for i in range( s.num_config_regs ):
        s.i_status[i] //= s.status_r[i].in_

    # Wires and register
    s.is_write     = Wire()
    s.is_read      = Wire()
    s.req_deq_xfer = Wire()
    s.csr_addr     = Wire( s.csr_addr_nbits )

    # Connections
    s.minion_req  //= s.req_q.istream
    s.minion_resp //= s.resp_q.ostream

    s.resp_q.istream.msg.type_ //= s.req_q.ostream.msg.type_
    s.resp_q.istream.msg.addr  //= s.req_q.ostream.msg.addr
    s.resp_q.istream.val       //= s.req_q.ostream.val
    s.req_q.ostream.rdy        //= s.resp_q.istream.rdy

    # Logic
    s.is_write //= lambda: s.req_q.ostream.msg.type_ == CfgType.WRITE
    s.is_read  //= lambda: s.req_q.ostream.msg.type_ == CfgType.READ
    s.req_deq_xfer //= lambda: s.req_q.ostream.val & s.req_q.ostream.rdy
    s.csr_addr //= s.req_q.ostream.msg.addr[0:s.csr_addr_nbits]

    # Write enable logic
    if s.num_config_regs > 0:
      for i in range( s.num_config_regs ):
        s.config_r[i].en //= lambda: ( s.req_deq_xfer & s.is_write &
                                        ( s.csr_addr == i ) )

    # Read data logic
    # Only has config registers
    if s.num_config_regs > 0 and s.num_status_regs == 0:
      @update
      def up_read_data_config_only():
        s.resp_q.istream.msg.data @= 0
        if s.is_read:
          for i in range( s.num_config_regs ):
            if ( s.req_q.ostream.val & ( s.csr_addr == i ) ):
              s.resp_q.istream.msg.data @= s.config_r[i].out

    # Only has status registers
    elif s.num_config_regs == 0 and s.num_status_regs > 0:
      @update
      def up_read_data_status_only():
        s.resp_q.istream.msg.data @= 0
        if s.is_read:
          for i in range( s.num_status_regs ):
            if ( s.req_q.ostream.val & ( s.csr_addr == i ) ):
              s.resp_q.istream.msg.data @= s.status_r[i].out

    # Has both config and status registers
    else:
      @update
      def up_read_data():
        s.resp_q.istream.msg.data @= 0
        if s.is_read:
          for i in range( s.total_num_regs ):
            if ( s.req_q.ostream.val & ( s.csr_addr == i ) ):
              s.resp_q.istream.msg.data @= (
                s.config_r[i].out if i < s.num_config_regs
                                  else s.status_r[i-s.num_config_regs].out )

  def line_trace( s ):
    return f'{s.minion_req}(){s.minion_resp}'
