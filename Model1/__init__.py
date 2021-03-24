from ui.ui import Ui_class


class Main():
    def __init__(self):
        print('실행할 메인 클래스')

        Ui_class()
        # 함수나 클래스는 무조건 괄호 붙여줘야해

if __name__=='__main__':
    Main()