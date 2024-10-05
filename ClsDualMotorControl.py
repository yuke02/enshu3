import lgpio


class ClsDualMotorControl:
	def __init__(self, vPortsDrive, vPortsPWM, sFrequency):
		self.__hGPIO = lgpio.gpiochip_open(0)
		self.__vPortsDrive = vPortsDrive
		self.resetPort()

		self.__vPortsPWM = vPortsPWM
		self.__sFrequency = sFrequency
		self.setPWM(0, 0)

	def __del__(self):
		self.resetPort()
		self.setPWM(0, 0)
		self.setPWM(0, 1)
		lgpio.gpiochip_close(self.__hGPIO)

	def resetPort(self):
		for sPortNum in range(5):
			lgpio.gpio_write(self.__hGPIO, self.__vPortsDrive[sPortNum], 0)

	def setPWM(self, sDuty, sMotorNumber):
		lgpio.tx_pwm(self.__hGPIO, self.__vPortsPWM[sMotorNumber], self.__sFrequency, sDuty)

	def stop(self):
		self.resetPort()
		self.setPWM(0,0)
		self.setPWM(0,1)

	def driveMotor(self, sMotorNumber, sDirection, sDuty):
		sPort = sMotorNumber * 2 + sDirection
		lgpio.gpio_write(self.__hGPIO, self.__vPortsDrive[4], 1) 		# negate STBY port
		lgpio.gpio_write(self.__hGPIO, self.__vPortsDrive[sPort], 1)	# assert direction port
		self.setPWM(sDuty, sMotorNumber)


if __name__ == "__main__":
	import time

	vPortsDrive = [23, 22, 25, 9, 10]  #AIN1, AIN2, BIN1, BIN2, STBY
	vPortsPWM = [12, 13]
	sFrequency = 10000

	ClsDmc = ClsDualMotorControl(vPortsDrive, vPortsPWM, sFrequency)
	ClsDmc.stop()

	try:
		while True:
			ClsDmc.driveMotor(0, 0, 80)
			time.sleep(2)

			ClsDmc.driveMotor(0, 1, 80)
			time.sleep(2)

			ClsDmc.driveMotor(1, 0, 80)
			time.sleep(2)

			ClsDmc.driveMotor(1, 1, 80)
			time.sleep(2)

	except KeyboardInterrupt:
		del ClsDmc
