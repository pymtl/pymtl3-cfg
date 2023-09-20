'''
==========================================================================
spi_ifcs.py
==========================================================================
Master and minion SPI interfaces.

Author : Kyle Infantino, Yanghui Ou
  Date : Mar 22, 2022
'''
# from pymtl3 import Interface, InPort, OutPort
from pymtl3 import *

#-------------------------------------------------------------------------
# Helper function
#-------------------------------------------------------------------------

def _spi_to_str( s ):
  ...

#-------------------------------------------------------------------------
# SPIMasterIfc
#-------------------------------------------------------------------------

class SpiMasterIfc( Interface ):

  def construct( s ):
    s.cs    = OutPort()
    s.sclk  = OutPort()
    s.mosi  = OutPort()
    s.miso  = InPort()

  def __str__( s ):
    return f"{s.sclk}|{s.cs}|{s.mosi}|{s.miso}"

#-------------------------------------------------------------------------
# SPIMinionIfc
#-------------------------------------------------------------------------

class SpiMinionIfc( Interface ):

  def construct( s ):
    s.cs    = InPort()
    s.sclk  = InPort()
    s.mosi  = InPort()
    s.miso  = OutPort()

  def __str__( s ):
    return f"{s.sclk}|{s.cs}|{s.mosi}|{s.miso}"
