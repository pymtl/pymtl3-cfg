'''
==========================================================================
msg_types.py
==========================================================================
Bit structs for the SPI stack.

Author : Yanghui Ou
  Date : May 20, 2022
'''
from pymtl3 import *

#-------------------------------------------------------------------------
# CfgType
#-------------------------------------------------------------------------

class CfgType:
  WRITE = 0
  READ  = 1

#-------------------------------------------------------------------------
# CfgReq
#-------------------------------------------------------------------------

# @bitstruct
# class CfgReq:
#   req_type : Bits2
#   addr     : Bits18
#   data     : Bits32

#-------------------------------------------------------------------------
# CfgResp
#-------------------------------------------------------------------------

# @bitstruct
# class CfgResp:
#   resp_type : Bits2
#   addr      : Bits18
#   data      : Bits32

#-------------------------------------------------------------------------
# CfgReq
#-------------------------------------------------------------------------

# @bitstruct
# class CfgMsg:
#   type_ : Bits2
#   addr  : Bits17
#   data  : Bits32

def mk_cfg_pkt_type( type_nbits=2, addr_nbits=16, data_nbits=32,
                     prefix='CfgPkt'):
  new_name = f'{prefix}_{type_nbits}_{addr_nbits}_{data_nbits}'
  str_method = lambda s: f'{s.type_}:{s.addr}:{s.data}'
  return mk_bitstruct( new_name, {
    'type_' : mk_bits(type_nbits),
    'addr'  : mk_bits(addr_nbits),
    'data'  : mk_bits(data_nbits),
  }, namespace={ '__str__' : str_method})
