> **Thomson**
>
> **6. CAN bus CANopen information**
>
> **6.1** **Introduction to CANopen**
>
> **6.1.1 CANopen standard**
>
> This document assumes the reader is familiar with the CiA 301
> speciﬁcation released by CAN in Automation. Terminology from the
> standard is used, but not described in detail. The Electrak® HD
> actuator is compliant with the standard. The default baudrate is
> 500kbit/s and it will only support the standard CAN frame with 11-bit
> identiﬁer ﬁeld.
>
> **6.1.2 EDS ﬁle**
>
> Thomson provides an electronic data sheet ﬁle (EDS) to integrate the
> Electrak HD into a speciﬁc CANopen network. The EDS ﬁle can be
> downloaded at
> [www.thomsonlinear.com/en/support/docs-linear-actuators](https://www.thomsonlinear.com/en/support/docs-linear-actuators)
> under the Conﬁguration Files section.
>
> **6.1.3 Node ID**
>
> The Electrak HD uses a default node ID of 19 (0x13). In applications
> where the default address is not available, it is possible to select
> an address through hardware switches. Activate the desired address
> select input by connecting it to positive and address select common to
> negative. This allows the user to change the default address using the
> address select inputs as deﬁned in section (CANopen connection
> diagram). Activating individual select pins will create a binary adder
> to the default address. This method can allow up to 8 individual
> actuator addresses on a single bus. Default address 19 (0x13) 20 (0x14) 21 (0x15) 26 ( 0x1A)
>
> **6.1.4 NMT State**
>
> The Electrak HD support the CANopen network management (NMT) slave
> state machine. It needs to be put in the operational state before
> operating properly.
>
> Example
>
> Sending a CAN message with id 0x0, containing the data 0x01 0x00 will
> put all connected actuators in the operational state. Sending a CAN
> message with id 0x0, containing the data 0x01 0x13 will put an
> actuator with the default Node ID in the operational state.
>
> Ensure that the proper node ID is used when referencing multiple
> actuators on a single bus network.
>
> **6.1.5 Sleep operation**
>
> The Electrak HD utilizes a sleep mode operation when positioning is no
> longer required. This feature allows for a constant battery connection
> with minimal drain while the engine or vehicle is not running. After
> 120 seconds of bus inactivity, the actuator will put itself in a state
> of sleep. During this state the quiescent current is \<1 mA for 12 Vdc
> models. The actuator will leave the sleep mode when bus activity is restored.
> 
> **6.2 Actuator control**
> 
> **6.2.1 Control PDO properties**
> 
> Operational control of the actuator is achieved by sending the
> statically mapped RPDO with COB-ID 0x200 + Node ID. It will have the
> following layout:
> 
> Byte 0 Byte 1, Byte 2 Byte 3, Byte 4 Byte 5, Byte 6, Byte 7
>
> Target Position, Current Limit, Target Speed, Movement Proﬁle, Control Bits
> 
> The preferred transmission repetition rate is 100ms (can also be sent as
> required by the application).
> 
> **6.2.2 Control PDO entries**
> 
> The Object Dictionary entries mapped to the RPDO are:
> 
> Index Name Object Type Data Type Description
>
> 0x2100 Target Position VAR UNSIGNED16
>
> The target position for the next actuator motion. The 0.0 mm and full
> extend stroke values represent 0 to 100% stroke and are only rela-tive
> to the actual available stroke of the individual unit. Resolution:
> 0.1mm/bit, 0 offset.
>
> 0x2101 Current Limit VAR UNSIGNED16
>
> The current at which the actuator will cease all motion. In the event
> a force is applied to the actuator that causes the motor current to
> exceed this settable value for more than 8 ms, the actuator will stop
> any current motion and activate a dynamic braking effect on the motor.
> This current limit does not apply during the motor starting phase
> where in rush current can be signiﬁcantly higher than normal running.
> Range: 0.0 A to 25.0 A (12 Vdc models).
>
> Resolution: 0.1 A/bit, 0 offset
>
> 0x2102 Target Speed VAR UNSIGNED16
>
> Controls the PWM driver within the actuator and the voltage applied to
> the motor. The resultant actuator speed will be a ratio of the
> actuators max speed, and also dependent on the load applied to the
> actuator.
>
> Range: 20% to 100% duty cycle. Resolution: 0.1%/bit, 0 offset.
> 
> 0x2103 Movement Proﬁle VAR UNSIGNED8
> 
> Controls the behavior of the actuator when trying to reach the target
> position.
> 
> Value set to 0: Normal operation, the actuator will run towards the
> target position at the target speed. It will stop when the target
> 
> position is reached. This should be the preferred value for most
> ap-plication.
> 
> Value set to 1: Precise operation, the actuator will perform an extra
> move after the target position is reached, this will increase accuracy
> in some applications.
> 
> Value set to 2: Small step operation, the actuator will run with reduced
> speed towards the target position. This will allow proper movement
> during very small positional increments.
> 
> 0x2104 Control bits VAR UNSIGNED8
> 
> Bit 0 (LSB) – Enable bit: This bit is used to enable motion from the
> actuator. If it is low (0), no motion will be allowed. This bit can be
> used to deﬁne the next actuator movement message without starting the
> motor. When movement is required this bit can be changed to high (1) and
> motion will begin using the values of the other objects contained in the
> RPDO.
> 
> **6.2.3 Control PDO example**
>
> Sending a CAN message with ID 0x213 containing the data 0xE8 0x03 0x7D
> 0x00 0x20 0x03 0x00 0x01 will make an actuator to move to position
> 100mm, at 80% duty cycle, with the current limit set to 12.5A. The
> example will work on an actuator with the default Node ID, if it is in
> the operational NMT state.
>
> **6.3 Actuator feedback**
>
> **6.3.1 Feedback PDO properties**
>
> Operational feedback of the actuator is achieved by receiving the
> statically mapped TPDO with COB-ID 0x180 + Node ID. It will have the
> following layout:
>
> Byte 0 Byte 1, Byte 2 Byte 3, Byte 4 Byte 5, Byte 6, Byte 7 
> Measured Position, Measured Limit, Measured Speed, Motion Flags, Error Flags
>
> **6.3.2 Feedback PDO entries**
>
> The Object Dictionary entries mapped to the TPDO are:
>
> Index Name Object Type Data Type
>
> Description
> 
> 0x2200 Measured Position VAR UNSIGNED16
> 
> The measured position of the actuator. The 0.0 mm and ordered full
> extend stroke values represent 0 to 100% stroke but the signaled value
> does not take in to account any mechanical tolerances or play in the
> actuator. Resolution: 0.1mm/bit, 0 offset.
> 
> 0x2201 Measured Current VAR UNSIGNED16
>
> The actual current being used by the actuator. Resolution: 0.1 A/bit,
> 0 offset
>
> 0x2202 Measured Speed VAR UNSIGNED16
>
> The actual duty cycle being applied to the motor through the internal
> actuator controller.
>
> Resolution: 0.1%/bit, 0 offset.
>
> 0x2203 Motion Flags VAR UNSIGNED8
>
> Contains information about the current actuator motion.
>
> Bit 0 (LSB) – Extending: 1 if currently extending, 0 otherwise. Bit 1
> – Retracting: 1 if currently retracting, 0 otherwise.
> 
> 
> 0x2204 Error Flags VAR
> 
> UNSIGNED8
> 
> Contains information about actuator errors.
> 
> Bit 0 (LSB) - Parameter Error: This ﬂag is used to inform the user that
> one of the object values in the RPDO is outside the allowed ranges the
> speciﬁc model will allow. To prevent damage to the actuator motion is
> not allowed after this ﬂag is set.
> 
> Bit 1 – Current Overlaod: This ﬂag is used to inform the user that the
> last motion the actuator attempted caused an overload condi-tion. This
> occurs when the actuator determines the current set in the Current Limit
> object from the RPDO is exceeded for a consecutive
> 
> 8 ms. When this ﬂag is set by the actuator the user must reset the
> Motion Enable bit in the RPDO before attempting additional motion from
> the actuator.
> 
> Bit 2 – Voltage Error: This ﬂag is used to inform the user that the
> operational voltage is outside of allowable running parameters. Any
> motion already in progress will continue for 10 seconds, but
> 
> additional movement request will not be allowed until the operational
> voltage returns within the normal operating range.
> 
> Bit 3- Temperature Error: This ﬂag is used to inform the user that the
> operational temperature is outside of allowable running parameters. Any
> motion already in progress will continue for 10 seconds, but additional
> movement request will not be allowed until the operational temperature
> returns within the normal operating range.
> 
> Bit 4 – Backdrive Detected: This ﬂag is used to inform the user that the
> actuator has determined positional movement in the extension tube that
> was not commanded from the user. This can be caused from excessive
> static load or vibration being applied to the actuator. Bit 5 – Message
> Timeout: This ﬂag is used to inform the user that no RPDO has been
> received within the time speciﬁed in the PDO
> 
> timeout time object(0x2005). When this ﬂag is set by the actuator the
> user must reset the Motion Enable bit is the RPDO before attempt-ing
> additional motion from the actuator. The default value is 5000ms. Bit 6
> – Fatal Error: This ﬂag is used to inform the user that the actua-tor
> was unable to detect any motion while trying to run the motor,
> 
> or that the position was updating in the wrong direction. When this ﬂag
> is set by the actuator the user must reset the Motion Enable bit in the
> RPDO before attempting additional motion from the actuator. Repeated
> activation of this ﬂag indicates problems with the actuator, and it is
> recommended to contact the factory for additional support. Bit 7(MSB)-
> Memory Error: This ﬂag is used to inform the user that the internal
> memory of the actuator is corrupted.
