'''
==========================================================================
pull_ifcs.py
==========================================================================
Pull-in and pull-out interfaces.

Author : Yanghui Ou
  Date : May 23, 2022
'''
from pymtl3 import Interface, InPort, OutPort

#-------------------------------------------------------------------------
# PullInIfc
#-------------------------------------------------------------------------

class PullInIfc( Interface ):

  def construct( s, Type ):
    s.en  = OutPort()
    s.msg = InPort( Type )

    s.trace_len = len( f'{Type()}' )

  def __str__( s ):
    return f'{s.msg}' if s.en else ' '.ljust( s.trace_len )

#-------------------------------------------------------------------------
# PullOutIfc
#-------------------------------------------------------------------------

class PullOutIfc( Interface ):

  def construct( s, Type ):
    s.en  = InPort()
    s.msg = OutPort( Type )

    s.trace_len = len( f'{Type()}' )

  def __str__( s ):
    return f'{s.msg}' if s.en else ' '.ljust( s.trace_len )
