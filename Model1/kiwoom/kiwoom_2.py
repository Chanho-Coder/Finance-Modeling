# xingAPI가 COM(Component Object Model)방식을 사용하는 것과 달리 키움 Open API는 OCX방식을 사용합니다.
# 따라서 이 책에서는 PyQt패키지의 QAxContainer 모듈을 통해 OCX를 사용합니다.
# 이 책에서는 PyQt를 통해 GUI프로그램을 개발할 예정입니다.

# 먼저 QApplication 클래스에 대한 인스턴스를 생성하고 이를 app이라는 변수로 바인딩합니다. app을 통해 exec_ 메서드를 호출하면
# 프로그램은 이벤트 루트(Event Loop)에 진입합니다.
# 이벤트 루프란 무한 반복하면서 이벤트를 처리하는 상태를 의미합니다

# OpenAPI의 TR 처리순서
# 1. SetInputValue 메서드를 사용해 TR 입력 값을 설정합니다.
# 2. CommRqData 메서드를 사용해 TR을 서버로 송신합니다.
# 3. 서버로부터 이벤트가 발생할 때까지 이벤트 루프를 사용해 대기합니다.
# 4. CommGetData 메서드를 사용해 수신 데이터를 가져옵니다.

from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *
from PyQt5.QtTest import *
# Ctrl키 + 위에거 누르면 이 클래스 안에 뭐가 있는지 알 수 있어.


class Kiwoom_2(QAxWidget):
    # QAxContainer 상속받은거야.

    def __init__(self):
        super().__init__()

        print('키움 클래스 입니다.')

        ####### eventloop 모음 #######
        self.login_event_loop=None
        #############################

        ####### 변수 모음 #######
        self.account_num = None
        ########################

        self.get_ocx_instance()
        self.event_slots()

        self.signal_login_commConnect()
        self.get_account_info()
        self.detail_account_info() # 예수금 가져오는 것


    def get_ocx_instance(self):
        self.setControl('KHOPENAPI.KHOpenAPICtrl.1')
        # 'KHOPENAPI.KHOpenAPICtrl.1'을 파이썬에서 제어할 수 있도록 하는 코드


    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot)
        self.OnReceiveTrData.connect(self.trdata_slot)


    def signal_login_commConnect(self):
        self.dynamicCall('CommConnect()')

        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()


    def login_slot(self, errCode):
        print(errors(errCode))

        self.login_event_loop.exit()


    def get_account_info(self):
        # 계좌번호 가져오기
        account_list = self.dynamicCall('GetLoginInfo(String)', 'ACCNO')  # 이건 KOA Studio에 나온 그대로를 따라줘야해

        self.account_num = account_list.split(';')[0] # '1029304920;' 계좌번호는 이런식으로 뒤에 ;가 붙어서 나오므로
        print('나의 보유 계좌번호 : %s' % self.account_num)


    def detail_account_info(self):
        print('예수금 가져오는 부분')

        self.dynamicCall('SetInputValue(QString, QString)', '계좌번호', self.account_num)
        self.dynamicCall('SetInputValue(QString, QString)', '비밀번호', '0052')
        self.dynamicCall('SetInputValue(QString, QString)', '비밀번호입력매체구분', '00')
        self.dynamicCall('SetInputValue(QString, QString)', '조회구분', '2')
        self.dynamicCall('CommRqData(QString,QString,int, QString)', '예수금상세현황요청','opw00001', '0', '2000')


    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        '''
        :param sScrNo: 스크린번호
        :param sRQName: 내가 요청했을 때 지은 이름
        :param sTrCode: 요청id, tr코드
        :param sRecordName: 사용안함
        :param sPrevNext: 다음 페이지가 있는지
        :return:
        '''
        if sRQName == '예수금상세현황요청':

            deposit = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, 0, '예수금')
            print('예수금 %s' % deposit)

            a = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, 0, '출금가능금액')
            print('출금가능금액 %s' % a)

            rows=self.dynamicCall('GetRepeatCnt(QString,QString)', sTrCode, sRQName) # GetRepeatCnt는 멀티데이터 뽑아오는 곳이야.
            cnt = 0
            for i in range(rows):
                code = self.dynamicCall('GetCommData(QString, QString, int, QString)', )