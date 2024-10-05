class ClsDualMotorControl:
	def __init__(self, vPortsDrive, vPortsPWM, sFrequency):
		print('ClsDualMotorControl was initialized.')

	def __del__(self):
		print('ClsDualMotorControl was terminated.')

	def resetPort(self):
		print('resetPort was called.')

	def setPWM(self, sDuty, sMotorNumber):
		print('setPWM was called.')

	def stop(self):
		print('stop was called.')

	def driveMotor(self, sMotorNumber, sDirection, sDuty):
		print('driveMotor was called. Motor:', sMotorNumber, 'Direction:', sDirection, 'Duty:', sDuty)

