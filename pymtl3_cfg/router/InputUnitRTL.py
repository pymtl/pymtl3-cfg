"""
=========================================================================
InputUnitRTL.py
=========================================================================
An input unit with val/rdy stream interfaces.

Author : Yanghui Ou
  Date : Mar 23, 2019
"""
from pymtl3 import *
from pymtl3.stdlib.stream.ifcs import OStreamIfc, IStreamIfc
from pymtl3.stdlib.stream.queues import StreamNormalQueue as NormalQueueRTL


class InputUnitRTL( Component ):
  def construct( s, PacketType, QueueType=NormalQueueRTL ):
    # Interface
    s.recv = IStreamIfc( PacketType )
    s.send = OStreamIfc( PacketType )

    # Component
    s.queue = QueueType( PacketType, num_entries=1 )
    s.queue.istream //= s.recv
    s.queue.ostream //= s.send

  def line_trace( s ):
    return f"{s.recv}({s.queue.count}){s.send}"
