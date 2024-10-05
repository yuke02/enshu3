# 状態定義 ----------------------------------------------------
IDLE = 0
FORWARD = 1
BACKWARD = 2
RIGHT = 3
LEFT = 4
ABOID = 5

# ステートマシン -------------------------------------------------
def stateMachine(sState, vFlagInfo, vEnemyInfo):

    sHorizontalCenter = 160
    sPositionThreshHigh = 15
    sPositionThreshLow = 5
    sSizeThreshHigh = 80
    sSizeThreshLow = 5

    if sState == IDLE:
        # vFlagInfo[0] が -1 ではない（つまり、オブジェクトが検出されている）。
        # vFlagInfo[2] が sSizeThreshHigh より小さい（オブジェクトが十分近づいていない）場合。
        if vFlagInfo[0] != -1 and vFlagInfo[2] < sSizeThreshHigh:
            sState = FORWARD
            
    elif sState == FORWARD:
        if vFlagInfo[0] > sHorizontalCenter + sPositionThreshHigh:
            sState = RIGHT
        elif vFlagInfo[0] < sHorizontalCenter - sPositionThreshHigh:
            sState = LEFT
        elif vFlagInfo[2] < sSizeThreshLow or vFlagInfo[2] > sSizeThreshHigh or vFlagInfo[0] == -1:
            sState = IDLE
    elif sState == RIGHT:
        if vFlagInfo[0] < sHorizontalCenter + sPositionThreshLow:
            sState = FORWARD
        elif vFlagInfo[2] < sSizeThreshLow or vFlagInfo[2] > sSizeThreshHigh or vFlagInfo[0] == -1:
            sState = IDLE
    elif sState == LEFT:
        if vFlagInfo[0] > sHorizontalCenter - sPositionThreshLow:
            sState = FORWARD
        elif vFlagInfo[2] < sSizeThreshLow or vFlagInfo[2] > sSizeThreshHigh or vFlagInfo[0] == -1:
            sState = IDLE
    elif sState == ABOID:
        # 敵が近くにいる場合、後退する
        if vEnemyInfo[0] != -1 and vEnemyInfo[2] > sSizeThreshHigh:
            sState = BACKWARD
        # 敵がいない、または遠くにいる場合、IDLE状態に戻る
        elif vEnemyInfo[0] == -1 or vEnemyInfo[2] < sSizeThreshHigh:
            sState = IDLE
        pass

    return sState