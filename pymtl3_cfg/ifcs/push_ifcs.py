'''
==========================================================================
push_ifcs.py
==========================================================================
Push-out and push-in interfaces.

Author : Yanghui Ou
  Date : Oct 6, 2021
'''

from pymtl3 import Interface, InPort, OutPort

#-------------------------------------------------------------------------
# PushMasterIfc
#-------------------------------------------------------------------------

class PushOutIfc( Interface ):

  def construct( s, Type ):
    s.en  = OutPort()
    s.msg = OutPort( Type )

    s.trace_len = len( f'{Type()}' )

  def __str__( s ):
    return f'{s.msg}' if s.en else ' '.ljust( s.trace_len )

#-------------------------------------------------------------------------
# PushMinionIfc
#-------------------------------------------------------------------------

class PushInIfc( Interface ):

  def construct( s, Type ):
    s.en  = InPort()
    s.msg = InPort( Type )

    s.trace_len = len( f'{Type()}' )

  def __str__( s ):
    return f'{s.msg}' if s.en else ' '.ljust( s.trace_len )
