from kiwoom.kiwoom import * # *은 모든 함수를 가져온다는 뜻이야.
import sys
from PyQt5.QtWidgets import *
# PyQt5는 Ui를 꾸미는걸 손쉽게 해줘

class Ui_class():
# 클래스의 첫 글자는 대문자로 하는게 좋아
    def __init__(self):
        print('Ui_class 입니다.')

        self.app = QApplication(sys.argv)
        # Ui를 실행하기위한 변수들을 초기화

        self.kiwoom = Kiwoom()

        self.app.exec_()
        # .exec()는 프로그램이 종료되지 않도록 하는거야.
        # 장중에 종료되면 안되잖아

