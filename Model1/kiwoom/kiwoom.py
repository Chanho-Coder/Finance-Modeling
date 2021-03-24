from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *
from PyQt5.QtTest import *
# Ctrl키 + 위에거 누르면 이 클래스 안에 뭐가 있는지 알 수 있어.


class Kiwoom(QAxWidget):
    # QAxContainer 상속받은거야.

    def __init__(self):
        super().__init__()

        print('키움 클래스 입니다.')

        ####### eventloop 모음 #######
        self.login_event_loop=None
        self.detail_account_info_event_loop = QEventLoop()
        #self.calculator_event_loop = QEventLoop()
        #self.purchase_event_loop = QEventLoop()
        #############################

        ####### 변수 모음 #######
        self.account_num = None
        self.account_stock_dict = {}
        self.not_account_stock_dict = {}
        self.purchase_dict = {}
        ########################

        ####### 계좌 관련 변수 #######
        self.use_money = 0
        self.use_money_percent = 0.5
        self.use_money_divide = 4
        ###########################

        ####### 종목 분석용 #######
        self.calcul_data = []
        #########################

        ####### 스크린번호 모음 #######
        self.screen_my_info = '2000'
        self.screen_calculation_stock = '4000'
        self.screen_calculation_stock_2 = '6000'
        ############################

        self.get_ocx_instance()
        self.event_slots()

        self.signal_login_commConnect()
        self.get_account_info()
        #self.detail_account_info() # 예수금 요청
        self.detail_account_mystock() # 계좌평가 잔고 내역 요청
        #self.not_concluded_account() # 미체결 요청

        #self.calculator_fnc() # 종목 분석용, 임시용으로 실행

        #self.calculator_fnc_2()

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


    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName,  sPrevNext): # 나머지는 사용안함이니까 안써도 될듯!
        '''
        tr요청을 받는 구역이다! 슬롯이다!
        :param sScrNo: 스크린번호
        :param sRQName: 내가 요청했을 때 지은 이름
        :param sTrCode: 요청id, tr코드
        :param sRecordName: 사용 안함
        :param sPrevNext: 다음 페이지가 있는지
        :return:
        '''

        if sRQName == '예수금상세현황요청':
            deposit = self.dynamicCall('GetCommData(String, String, int, String)', sTrCode, sRQName, 0, '예수금')
            print('예수금 : %s' % deposit)
            print('예수금 형변환 : %s' % int(deposit))

            self.use_money = int(deposit) * self.use_money_percent
            self.use_money = self.use_money / self.use_money_divide

            ok_deposit = self.dynamicCall('GetCommData(String, String, int, String)', sTrCode, sRQName, 0, '출금가능금액')
            print('출금가능금액 : %s' % ok_deposit)
            print('출금가능금액 형변환 : %s' % int(ok_deposit))

            self.detail_account_info_event_loop.exit()

        if sRQName == '계좌평가잔고내역요청':
            total_buy_money = self.dynamicCall('GetCommData(String, String, int, String)', sTrCode, sRQName, 0, '총매입금액')
            total_buy_money_result = int(total_buy_money)
            print('총매입금액 : %s' % total_buy_money_result)

            total_profit_loss_rate = self.dynamicCall('GetCommData(String, String, int, String)', sTrCode, sRQName, 0, '총수익률(%)')
            total_profit_loss_rate_result = float(total_profit_loss_rate)
            print('총수익률(%s) : %s' % ('%', total_profit_loss_rate_result)) # %를 그냥 %로 쓰는게 아니라 %s를 써놓은 후 대입해준 부분!! 여기 조심해 !!

            # 이 밑에는 eventloop를 막 끊으면 안돼. 종목을 가져와야되는데 끊으면 안되잖아.

            rows = self.dynamicCall('GetRepeatCnt(QString,QString)', sTrCode, sRQName)


            for i in range(rows):
                code = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '종목번호')
                code = code.strip()[1:]
                code_nm = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '종목명')
                stock_quantity = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '보유수량')
                buy_price = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '매입가')
                learn_rate = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '수익률(%)')
                current_price = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '현재가')
                total_chegual_price = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '매입금액')
                possible_quantity = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '매매가능수량')

                if code in self.account_stock_dict:
                    pass
                else:
                    self.account_stock_dict.update({code:{}})


                code_nm = code_nm.strip()
                stock_quantity = int(stock_quantity.strip())
                buy_price = int(buy_price.strip())
                learn_rate = float(learn_rate.strip())
                current_price = int(current_price.strip())
                total_chegual_price = int(total_chegual_price.strip())
                possible_quantity = int(possible_quantity.strip())

                self.account_stock_dict[code].update({'종목명' : code_nm})
                self.account_stock_dict[code].update({'보유수량' : stock_quantity})
                self.account_stock_dict[code].update({'매입가' : buy_price})
                self.account_stock_dict[code].update({'수익률(%)' : learn_rate})
                self.account_stock_dict[code].update({'현재가' : current_price})
                self.account_stock_dict[code].update({'매입금액' : total_chegual_price})
                self.account_stock_dict[code].update({'매매가능수량' : possible_quantity})

            print('계좌에 가지고 있는 종목 : %s' % self.account_stock_dict)
            print('계좌에 가지고 있는 종목 수 : %s' % len(self.account_stock_dict))



            if sPrevNext == '2':
                self.detail_account_mystock(sPrevNext='2')
            else :
                self.detail_account_info_event_loop.exit()

        elif sRQName == '실시간미체결요청':

            rows = self.dynamicCall('GetRepeatCnt(QString,QString)', sTrCode, sRQName)

            for i in range(rows):
                code = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '종목번호')
                code_nm = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '종목명')
                order_no = self.dynamicCall('GetCommData(QString, QString, int QString)', sTrCode, sRQName, i, '주문번호')
                order_status = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '주문상태')
                order_quantity = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '주문수량')
                order_price = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '주문가격')
                order_guban = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '주문구분')
                not_quantity = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '미체결수량')
                ok_quantity = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '체결량')

                code = code.strip() # 양 옆에 공백 있을 까봐 공백 없애주는거야.
                code_nm = code_nm.strip()
                order_no = int(order_no.strip()) # String 형으로 나오므로 숫자로 바꿔주는거야.
                order_status = order_status.strip()
                order_quantity = int(order_quantity.strip())
                order_price = int(order_price.strip())
                order_guban = order_guban.strip().lstrip('+').lstrip('-')
                not_quantity = int(not_quantity.strip())
                ok_quantity = int(ok_quantity.strip())

                if order_no in self.not_account_stock_dict:
                    pass
                else :
                    self.not_account_stock_dict[order_no] = {}


                self.not_account_stock_dict[order_no].update({'종목번호' : code})
                self.not_account_stock_dict[order_no].update({'종목명': code_nm})
                self.not_account_stock_dict[order_no].update({'주문번호': order_no})
                self.not_account_stock_dict[order_no].update({'주문상태' : order_status})
                self.not_account_stock_dict[order_no].update({'주문수량' : order_quantity})
                self.not_account_stock_dict[order_no].update({'주문가격' : order_price})
                self.not_account_stock_dict[order_no].update({'주문구분' : order_guban})
                self.not_account_stock_dict[order_no].update({'미체결수량' : not_quantity})
                self.not_account_stock_dict[order_no].update({'체결량' : ok_quantity})

                print('미체결 종목 : %s' % self.not_account_stock_dict[order_no])
                print('미체결 종목 수 : %s' % len(self.not_account_stock_dict[order_no]))

            self.detail_account_info_event_loop.exit()


        elif '주식일봉차트조회' == sRQName:

            code = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, 0, '종목코드')
            code = code.strip()
            print('%s 일봉데이터요청' % code)

            cnt = self.dynamicCall('GetRepeatCnt(QString, QString)', sTrCode, sRQName)
            print('데이터 일수 %s' % cnt)

            # 한 번 조회하면 600일치까지 일봉데이터를 받을 수 있다.

            for i in range(cnt):
                data = []

                current_price = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '현재가')
                value = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '거래량')
                trading_value = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '거래대금')
                date = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '일자')
                start_price = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '시가')
                high_price = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '고가')
                low_price = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '저가')

                data.append('')
                data.append(current_price.strip())
                data.append(value.strip())
                data.append(trading_value.strip())
                data.append(date.strip())
                data.append(start_price.strip())
                data.append(high_price.strip())
                data.append(low_price.strip())
                data.append('')

                self.calcul_data.append(data.copy())

            print(len(self.calcul_data))

            if sPrevNext =='2':
                self.day_kiwoom_db(code=code, sPrevNext=sPrevNext)

            else:
                print('총 일수 %s' % len(self.calcul_data))

                pass_success = False

                # 120일 이평선을 그릴만큼의 데이터가 있는지 체크
                if self.calcul_data == None or len(self.calcul_data) < 120 :
                    pass_success = False

                else :
                    total_price=0
                    for value in self.calcul_data[:120]:
                        total_price += int(value[1])

                    moving_average_price = total_price / 120

                    # 오늘자 주가가 120일 이평선에 걸쳐있는지 확인
                    bottom_stock_price = False
                    check_price=None
                    if int(self.calcul_data[0][7]) <= moving_average_price and moving_average_price >= int(self.calcul_data[0][6]):
                        print('오늘 주가 120 이평선에 걸쳐있는 것 확인')
                        bottom_stock_price = True
                        check_price = int(self.calcul_data[0][6])

                    # 과거 일봉들이 120일 이평선보다 밑에 있는지 확인
                    # 그렇게 확인을 하다가 일봉이 120일 이평선보다 위에 있으면 계산 진행
                    prev_price = None # 과거의 일봉 저가
                    if bottom_stock_price == True :

                        moving_average_price_prev = 0
                        price_top_moving = False

                        idx = 1
                        while True:
                            if len(self.calcul_data[idx:]) < 120:# 120일치가 있는지 계속 확인
                                print('120일치가 없음')
                                break

                            total_price = 0
                            for value in self.calcul_data[idx:120+idx]:
                                total_price += int(value[1])

                            moving_average_price_prev = total_price / 120

                            if moving_average_price_prev <= int(self.calcul_data[idx][6]) and idx <= 20:
                                print('20일 동안 주가가 120일 이평선과 같거나 위에 있으면 조건 통과 못함')
                                price_top_moving = False
                                break

                            elif int(self.calcul_data[idx][7]) > moving_average_price_prev and idx > 20:
                                print('120일 이평선 위에 있는 일봉 확인됨')
                                price_top_moving = True
                                prev_price = int(self.calcul_data[idx][7])
                                break

                            idx += 1

                        # 해당 부분 이평선이 가장 최근 일자의 이평선 가격보다 낮은지 확인
                        if price_top_moving == True:
                            if moving_average_price > moving_average_price_prev and check_price > prev_price:
                                print('포착된 이평선의 가격이 오늘자(최근일자) 이평선 가격보다 낮은 것 확인됨')
                                print('포착된 부분의 일봉 저가가 오늘자 일봉의 고가보다 낮은지 확인됨')
                                pass_success = True

                if pass_success == True :
                    print('조건부 통과됨')

                    code_nm = self.dynamicCall('GetMasterCodeName(QString)', code)
                    f = open('files/condition_stock.txt', 'a', encoding='utf8')
                    f.write('%s\t%s\t%s\n' % (code, code_nm, str(self.calcul_data[0][1])))
                    f.close()

                elif pass_success == False:
                    print('조건부 통과 못함')

                self.calcul_data.clear()
                self.calculator_event_loop.exit()

        elif sRQName == '일별주가요청':
            code = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, 0, '종목코드')
            code = code.strip()[1:]
            print('%s 일봉주가요청' % code)

            rows = self.dynamicCall('GetRepeatCnt(QString, QString)', sTrCode, sRQName)
            print('데이터 일수 %s' % rows)

            for i in range(rows):
                code = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '종목번호')
                code = code.strip()[1:]
                code_nm = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '종목명')
                for_purc = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '외인순매수')
                ins_purc = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '기관순매수')
                per_purc = self.dynamicCall('GetCommData(QString, QString, int, QString)', sTrCode, sRQName, i, '개인순매수')


                if code in self.purchase_dict:
                    pass
                else:
                    self.purchase_dict.update({code:{}})

                code_nm = code_nm.strip()
                for_purc = int(for_purc.strip())
                ins_purc = int(ins_purc.strip())
                per_purc = int(per_purc.strip())

                self.purchase_dict.update({'종목명': code_nm})
                self.purchase_dict.update({'외인순매수': for_purc})
                self.purchase_dict.update({'기관순매수': ins_purc})
                self.purchase_dict.update({'개인순매수': per_purc})

                print('하나 받아옴')

                self.purchase_event_loop.exit()
            print('불러오기 끝')

    def get_account_info(self):
        # 계좌번호 가져오기
        account_list = self.dynamicCall('GetLoginInfo(String)', 'ACCNO')  # 이건 KOA Studio에 나온 그대로를 따라줘야해

        self.account_num = account_list.split(';')[0] # '1029304920;' 계좌번호는 이런식으로 뒤에 ;가 붙어서 나오므로
        print('나의 보유 계좌번호 : %s' % self.account_num)


    def detail_account_info(self):
        print('예수금을 요청하는 부분')

        self.dynamicCall('SetInputValue(String, String)', '계좌번호', self.account_num)
        self.dynamicCall('SetInputValue(String, String)', '비밀번호', '0052')
        self.dynamicCall('SetInputValue(String, String)', '비밀번호입력매체구분', '00')
        self.dynamicCall('SetInputValue(String, String)', '조회구분', '2')
        self.dynamicCall('CommRqData(String, String, int, String)', '예수금상세현황요청', 'opw00001', '0', self.screen_my_info)

        self.detail_account_info_event_loop = QEventLoop()
        self.detail_account_info_event_loop.exec_()


    def detail_account_mystock(self, sPrevNext='0'):
        print('계좌평가 잔고내역 요청하기 연속조회 %s' % sPrevNext)

        self.dynamicCall('SetInputValue(String, String)', '계좌번호', self.account_num)
        self.dynamicCall('SetInputValue(String, String)', '비밀번호입력매체구분', '00')
        self.dynamicCall('SetInputValue(String, String)', '조회구분', '2')
        self.dynamicCall('CommRqData(String, String, int, String)', '계좌평가잔고내역요청', 'opw00018', sPrevNext, self.screen_my_info)


        self.detail_account_info_event_loop.exec_()


    def not_concluded_account(self, sPrevNext='0'):
        print('미체결 주문 요청')






        self.dynamicCall('SetInputValue(QString, QString)', '계좌번호', self.account_num)
        self.dynamicCall('SetInputValue(QString, QString)', '체결구분', '1')
        self.dynamicCall('SetInputValue(QString, QString)', '매매구분', '0')
        self.dynamicCall('CommRqData(QString, QString, int, QString)', '실시간미체결요청', 'opt10075', sPrevNext, self.screen_my_info)

        self.detail_account_info_event_loop.exit()


    def get_code_list_by_market(self, market_code):
        '''
        종목 코드들 반환
        :param market_code:
        :return:
        '''

        code_list = self.dynamicCall('GetCodeListByMarket(QString)', market_code)
        code_list = code_list.split(';')[:-1]
        return code_list


    def calculator_fnc(self):
        # 빠르게 돌리려고하면 에러가 나.
        # 일정 텀을 두고 데이터를 받아와야해.

        code_list = self.get_code_list_by_market('10')
        print('코스닥 개수 : %s' % len(code_list))

        for idx, code in enumerate(code_list):
            self.dynamicCall('DisconnectRealData(QString)', self.screen_calculation_stock)
            print('%s / %s : KOSDAQ Stock Code : %s is updating... ' %(idx+1, len(code_list), code))

            self.day_kiwoom_db(code=code)


    def day_kiwoom_db(self, code=None, date=None, sPrevNext='0'):

        QTest.qWait(3600)

        self.dynamicCall('SetInputValue(QString,QString)', '종목코드', code)
        self.dynamicCall('SetInputValue(QString,QString)', '수정주가구분', '1')

        if date != None :
            self.dynamicCall('SetInputValue(QString, QString)', '기준일자',date)

        self.dynamicCall('CommRqData(QString, QString, int, QString)', '주식일봉차트조회', 'opt10081', sPrevNext, self.screen_calculation_stock)

        self.calculator_event_loop.exec_()

    def calculator_fnc_2(self):
        # 빠르게 돌리려고하면 에러가 나.
        # 일정 텀을 두고 데이터를 받아와야해.

        code_list = self.get_code_list_by_market('0')
        print('코스피 개수 : %s' % len(code_list))

        for idx, code in enumerate(code_list):
            self.dynamicCall('DisconnectRealData(QString)', self.screen_calculation_stock_2)
            print('%s / %s : KOSPI Stock Code : %s is updating... ' %(idx+1, len(code_list), code))

            self.purchase_stock(code=code)


    def purchase_stock(self, code=None, date=None, sPrevNext='0'):

        QTest.qWait(3600)

        self.dynamicCall('SetInputValue(QString, QString)', '종목코드', code)
        self.dynamicCall('SetInputValue(QString, QString)', '표시구분', '1')

        if date != None :
            self.dynamicCall('SetInputValue(QString, QString)', '조회일자', date)

        self.dynamicCall('CommRqData(QString, QString, int, QString)', '일별주가요청', 'op10086', sPrevNext, self.screen_calculation_stock_2)

        self.purchase_event_loop.exec_()