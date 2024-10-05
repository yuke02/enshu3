# ライブラリ等のインポート ------------------------------------------
import cv2
import numpy as np
import locateTarget as lt
import stateMachine as sm
import time  

from ClsDualMotorControl import ClsDualMotorControl
#from ClsDualMotorControlDummy import ClsDualMotorControl

# イメージセンサの初期化 ------------------------------------------
videoCap = cv2.VideoCapture(0)
sWidthSensor = 640
sHeightSensor = 480
videoCap.set(cv2.CAP_PROP_FRAME_WIDTH, sWidthSensor)
videoCap.set(cv2.CAP_PROP_FRAME_HEIGHT, sHeightSensor)

# 処理画像サイズの決定 ------------------------------------------
sResizeRatio = 0.5
if videoCap.isOpened():
	sReturn, imCamera = videoCap.read()
	print('W: ', imCamera.shape[1], ', H:', imCamera.shape[0])
	sWidth = int(imCamera.shape[1] * sResizeRatio)
	sHeight = int(imCamera.shape[0] * sResizeRatio)

# 画像処理・表示ループ外の変数 ------------------------------------
sDisplayRate = 5
sMode = 1
sFrame = 0

# 画像記録バッファ -----------------------------------------------
imGray = np.ndarray((sHeight, sWidth))
imRedBinary = np.ndarray((sHeight, sWidth))
imGreenBinary = np.ndarray((sHeight, sWidth))

# ステート初期化 -------------------------------------------------
sState = sm.IDLE

# Dual motor controller初期設定 ---------------------------------
vPortsDrive = [23, 22, 25, 9, 10]  #AIN1, AIN2, BIN1, BIN2, STBY
vPortsPWM = [12, 13]
sFrequency = 10000
ClsDmc = ClsDualMotorControl(vPortsDrive, vPortsPWM, sFrequency)

# 画像処理・表示ループ -------------------------------------------
while videoCap.isOpened() :
	# 画像の取得 -----------------------------------------------
	sReturn, imCamera = videoCap.read()
	if not sReturn:
		break

	# 画像サイズの変更 ------------------------------------------
	imResize = cv2.resize(imCamera , (sWidth, sHeight))
	
	# キーボード入力 -------------------------------------------- 
	sKey = cv2.waitKey(1) & 0xFF
	if sKey >= ord('0') and sKey <= ord('9'):
		sMode = sKey - ord('0')

	# 動作モードの選択 ------------------------------------------- 
#  ClsDmc.driveMotor()関数が使用されています。この関数の引数は以下の通りです：

# モーターの番号：0または1。ロボットには通常2つのモーターがあり、それぞれに番号が割り当てられています。
# 方向：0または1。0は前進、1は後進を示します。
# 速度：この例では80が指定されています。速度の単位や範囲は、driveMotor()関数の実装やロボットのハードウェアに依存します。
# したがって、例えばClsDmc.driveMotor(0, 0, 80)は「モーター0を速度80で前進させる」という動作を指示します。
	if sMode == 1:
		imDisplay = imResize
		if sKey == ord('u'):
			ClsDmc.stop()
			ClsDmc.driveMotor(0, 0, 80)
			ClsDmc.driveMotor(1, 0, 80)
		elif sKey == ord('m'):
			ClsDmc.stop()
		elif sKey == ord('h'):
			ClsDmc.stop()
			ClsDmc.driveMotor(0, 0, 80)
			ClsDmc.driveMotor(1, 1, 80)
		elif sKey == ord('k'):
			ClsDmc.stop()
			ClsDmc.driveMotor(0, 1, 80)
			ClsDmc.driveMotor(1, 0, 80)
		elif sKey == ord('j'):
			ClsDmc.stop()
			ClsDmc.driveMotor(0, 1, 80)
			ClsDmc.driveMotor(1, 1, 80)
			
		if sFrame == 999:
			print('1000 frames have passed')
			
	elif sMode == 2:
		imDisplay = imResize
  
		imGaussianHSV = lt.preprocess(imResize)
		vFlagInfo, imRedBinary = lt.locateFlag(imGaussianHSV)
		vEnemyInfo, imGreenBinary = lt.locateEnemy(imGaussianHSV)
		sPreviousState = sState
		sState = sm.stateMachine(sState, vFlagInfo, vEnemyInfo)
		
		if sState == sm.IDLE:
			ClsDmc.stop()
		elif sState == sm.FORWARD:
			ClsDmc.stop()
			ClsDmc.driveMotor(0, 0, 80)
			ClsDmc.driveMotor(1, 0, 80)
		elif sState == sm.LEFT:
			ClsDmc.stop()
			ClsDmc.driveMotor(0, 0, 80)
			ClsDmc.driveMotor(1, 1, 80)
		elif sState == sm.RIGHT:
			ClsDmc.stop()
			ClsDmc.driveMotor(0, 1, 80)
			ClsDmc.driveMotor(1, 0, 80)
		
		if vFlagInfo[0] != -1:
			cv2.line(imDisplay, (vFlagInfo[0], 1), (vFlagInfo[0], sHeight), (0,0,255))
		if vEnemyInfo[0] != -1:
			cv2.line(imDisplay, (vEnemyInfo[0], 1), (vEnemyInfo[0], sHeight), (0,255,0))
		
		if sPreviousState != sState:
			print('current state is :', sState)

	# 画像の表示 ----------------------------------------------
	if sFrame % sDisplayRate == 0:
		cv2.imshow('input', imDisplay)
		#cv2.imshow('red', imRedBinary)
		#cv2.imshow('green', imGreenBinary)

	# コマンドの処理 --------------------------------------------
	if sKey == ord('q'):
		break

	# フレーム番号の更新 ----------------------------------------    
	if sFrame == 999:
		sFrame = 0
	else:
		sFrame =sFrame + 1

# 終了処理 ----------------------------------------------------
ClsDmc.stop()            
cv2.destroyAllWindows()
videoCap.release()
