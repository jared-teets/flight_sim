# import the library
import can

# create a bus instance using 'with' statement,
# this will cause bus.shutdown() to be called on the block exit;
# many other interfaces are supported as well (see documentation)
with can.Bus(interface='socketcan',
              channel='can0',
              receive_own_messages=True) as bus:

   # send a message
   message = can.Message(arbitration_id=123, is_extended_id=True,
                         data=[0x11, 0x22, 0x33])
   # bus.send(message, timeout=0.2)
   
   print(bus._can_protocol)
   
   try:
       bus.send(message)
       print(f"Message sent on {bus.channel_info}")
       print(message.data[0])
       # look up other methods of bus class to see what I can use
   except can.CanError:
       print("Message not sent")

   # iterate over received messages
   #print(bus)
   #for msg in bus:
   #    print(f"{msg.arbitration_id:X}: {msg.data}")

   # or use an asynchronous notifier
   #notifier = can.Notifier(bus, [can.Logger("recorded.log"), can.Printer()])