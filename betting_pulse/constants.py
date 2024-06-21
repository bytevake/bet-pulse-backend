# all constant values are stored here
from decimal import Decimal

MIN_TRANS = 3 # num of minimum transactions for a loan pass
LOAN_THRES = 1 # the threshold that determines loan pass
LOAN_WIN_IRT = round(Decimal(0.2), 1) # loan interest if user wins bet
LOAN_LOSE_IRT = round(Decimal(0.1), 1) # loan interest if user loses bet
GLOBAL_CAP = round(Decimal(50000), 2) # global loan CAP
LOCAL_CAP = round(Decimal(10000), 2) # glocal CAP