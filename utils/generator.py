import os
import random
import functools
import pendulum
from operator import add, mul
from common.pattern import Singleton


class Generator(Singleton):
    '''
        随机生成测试数据
    '''
    IDENTITY_VALIDATE_CODE = ("1", "0", "X", "9", "8", "7", "6", "5", "4", "3", "2")
    IDENTITY_WEIGHT = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2)
    LOCATION = list()
    NAMES = list()
    BANKS = list()
    PHONE = list()
    BANK_BIN = {}
    MOBILE_ADDRESS = {}

    def __init__(self):
        self._read()

    def _read(self):
        rules = [
            ('location.csv', self._parse_location, self.LOCATION),
            ('names.txt', self._parse_names, self.NAMES),
            ('bin.csv', self._parse_bank_bin, self.BANKS),
            ('phone.csv', self._parse_phone, self.PHONE),
        ]
        path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for filename, method, target in rules:
            if target:
                continue
            filename = path + '/data/' + filename
            print('reading file:', filename)
            with open(filename) as fin:
                for line in fin:
                    if not line:
                        continue
                    result = method(line)
                    if result:
                        target.append(result)

    def _parse_location(self, line):
        tks = line.split(',')
        if tks[0].isdigit() is False:
            return None
        elif tks[0].startswith('9'):
            # 排除海外地区
            return None
        elif len(tks[0]) != 6:
            # 精确到县级
            return None
        return [tks[0], tks[1].strip('"')]

    def _parse_names(self, line):
        return line.strip()

    def _parse_bank_bin(self, line):
        tks = line.strip().split(',')
        return [tks[0], tks[1]]

    def _parse_phone(self, line):
        # phone7, address, company, address_code
        tks = line.strip().split(',')
        if len(tks) == 3:
            extra = None
        else:
            extra = ' '.join(tks[3:])
        return [tks[0], tks[1], tks[2], extra]

    @classmethod
    def _build_bank_bin(cls):
        if cls.BANK_BIN:
            return
        for bin, alias in cls.BANKS:
            if alias in cls.BANK_BIN:
                cls.BANK_BIN[alias].append(bin)
            else:
                cls.BANK_BIN[alias] = [bin, ]

    @classmethod
    def _build_mobile_address(cls):
        if cls.MOBILE_ADDRESS:
            return

    def generate(self, data):
        name = random.choice(self.NAMES)
        home = data.get('home', True)  # 身份证和手机号同一归属地
        while True:
            mobile = self.generate_phone()
            if home is False:
                break
            if mobile[-1] is not None:
                break
        age = (int(data['age_min']), int(data['age_max']))
        addr_code = mobile[-1]
        identity, area = self.generate_identity(age, addr_code if home else None)
        bank_org = data.get('bank_org', '')
        card_no, card_org = self.generate_cardnum(bank_org=bank_org)
        ret = {
            'name': name,
            'identity': identity,
            'address': area,
            'bank_card_no': card_no,
            'bank_card_org': card_org,
            'phone_num': mobile[0],
            'phone_address': mobile[1],
            'phone_company': mobile[2],
        }
        return ret

    def generate_identity(self, age=(20, 30), addr_code=None):
        '''
            6位数字地址码
            8位数字出生日期码
            3位数字顺序码  同一天出生的顺序号 奇数表示男 偶数表示女
            1位校验码
        '''
        if addr_code:
            acode = random.choice(addr_code.split())
            locations = [loc for loc in self.LOCATION if loc[0].startswith(acode)]
        else:
            locations = self.LOCATION
        area = random.choice(locations)
        now = pendulum.now()
        tstart = now.subtract(years=age[1])
        tstop = now.subtract(years=age[0])
        rts = random.randint(tstart.int_timestamp, tstop.int_timestamp)
        birthday = pendulum.from_timestamp(rts).format('YYYYMMDD')
        code = str(random.randint(0, 999)).zfill(3)
        pre = area[0] + birthday + code
        vcode = self.identity_verify_code(pre)
        return pre + vcode, area[1]

    def generate_cardnum(self, bank_org='ICBC'):
        self._build_bank_bin()
        bank_org = bank_org.upper()
        if bank_org in self.BANK_BIN:
            bin = random.choice(self.BANK_BIN[bank_org])
        else:
            bin = random.choice(self.BANK)[0]
        body = ''.join([str(random.randint(0, 9999)).zfill(4) for _ in range(3)])
        pre = bin + body
        vcode = self.bank_card_verify_code(pre)
        return pre + str(vcode), bank_org

    def generate_phone(self):
        company = {
            '1': '中国联通',
            '2': '中国电信',
            '3': '中国移动',
        }
        mobile = random.choice(self.PHONE)
        mobile[0] = mobile[0] + str(random.randint(0, 9999)).zfill(4)
        mobile[2] = company.get(mobile[2], '')
        return mobile

    @classmethod
    def identity_verify_code(cls, pre):
        '''
            1. 前17位数字本体码加权求和公式 S = Sum(Ai * Wi), i = 0, ... , 16
                (1). Ai:表示第i位置上的身份证号码数字值
                (2). Wi:表示第i位置上的加权因子 Wi: 7 9 10 5 8 4 2 1 6 3 7 9 10 5 8 4
            2. 计算模 Y = mod(S, 11)
            3. 通过模得到对应的校验码 Y: 0 1 2 3 4 5 6 7 8 9 10 校验码: 1 0 X 9 8 7 6 5 4 3 2
        '''
        s = functools.reduce(add, map(mul, map(int, pre), cls.IDENTITY_WEIGHT))
        return cls.IDENTITY_VALIDATE_CODE[s % 11]

    @classmethod
    def bank_card_verify_code(cls, card_num):
        '''
        银行卡校验码
        Luhn Check Digit Algorithm
        '''
        total = 0
        even = True
        if isinstance(card_num, int):
            card_num = str(card_num)
        for item in card_num[-1::-1]:
            item = int(item)
            if even:
                item <<= 1
            if item > 9:
                item -= 9
            total += item
            even = not even
        return (10 - (total % 10)) % 10


if __name__ == '__main__':
    for _ in range(10):
        gtor = Generator()
        data = {
            'age_min': random.choice([20, 30]),
            'age_max': random.choice([30, 40]),
            'bank_org': random.choice(['ICBC', 'ABC', 'None']),
            'home': random.choice([True, False]),
        }
        print(gtor.generate(data))
