# -*- coding: utf-8 -*-

class BaseEvent(object):
    def __init__(self, fields, event_name='Event', key_fields=(), recguid=None):
        self.recguid = recguid
        self.name = event_name
        self.fields = list(fields)
        self.field2content = {f: None for f in fields}
        self.nonempty_count = 0
        self.nonempty_ratio = self.nonempty_count / len(self.fields)

        self.key_fields = set(key_fields)
        for key_field in self.key_fields:
            assert key_field in self.field2content

    def __repr__(self):
        event_str = "\n{}[\n".format(self.name)
        event_str += "  {}={}\n".format("recguid", self.recguid)
        event_str += "  {}={}\n".format("nonempty_count", self.nonempty_count)
        event_str += "  {}={:.3f}\n".format("nonempty_ratio", self.nonempty_ratio)
        event_str += "] (\n"
        for field in self.fields:
            if field in self.key_fields:
                key_str = " (key)"
            else:
                key_str = ""
            event_str += "  " + field + "=" + str(self.field2content[field]) + ", {}\n".format(key_str)
        event_str += ")\n"
        return event_str

    def update_by_dict(self, field2text, recguid=None):
        self.nonempty_count = 0
        self.recguid = recguid

        for field in self.fields:
            if field in field2text and field2text[field] is not None:
                self.nonempty_count += 1
                self.field2content[field] = field2text[field]
            else:
                self.field2content[field] = None

        self.nonempty_ratio = self.nonempty_count / len(self.fields)

    def field_to_dict(self):
        return dict(self.field2content)

    def set_key_fields(self, key_fields):
        self.key_fields = set(key_fields)

    def is_key_complete(self):
        for key_field in self.key_fields:
            if self.field2content[key_field] is None:
                return False

        return True

    def is_good_candidate(self):
        raise NotImplementedError()

    def get_argument_tuple(self):
        args_tuple = tuple(self.field2content[field] for field in self.fields)
        return args_tuple


class EquityFreezeEvent(BaseEvent):
    """股票冻结事件"""
    NAME = 'EquityFreeze'
    FIELDS = [
        'EquityHolder',
        'FrozeShares',
        'LegalInstitution',
        'TotalHoldingShares',
        'TotalHoldingRatio',
        'StartDate',
        'EndDate',
        'UnfrozeDate',
    ]

    def __init__(self, recguid=None):
        super().__init__(
            EquityFreezeEvent.FIELDS, event_name=EquityFreezeEvent.NAME, recguid=recguid
        )
        # 设置关键事件角色
        self.set_key_fields([
            'EquityHolder',
            'FrozeShares',
            'LegalInstitution',
        ])

    def is_good_candidate(self, min_match_count=5):
        key_flag = self.is_key_complete()
        if key_flag:
            if self.nonempty_count >= min_match_count:
                return True
        return False


class EquityRepurchaseEvent(BaseEvent):
    """股票回购事件"""
    NAME = 'EquityRepurchase'
    FIELDS = [
        'CompanyName',
        'HighestTradingPrice',
        'LowestTradingPrice',
        'RepurchasedShares',
        'ClosingDate',
        'RepurchaseAmount',
    ]

    def __init__(self, recguid=None):
        super().__init__(
            EquityRepurchaseEvent.FIELDS, event_name=EquityRepurchaseEvent.NAME, recguid=recguid
        )
        self.set_key_fields([
            'CompanyName',
        ])

    def is_good_candidate(self, min_match_count=4):
        key_flag = self.is_key_complete()
        if key_flag:
            if self.nonempty_count >= min_match_count:
                return True
        return False


class EquityUnderweightEvent(BaseEvent):
    """股票减持事件"""
    NAME = 'EquityUnderweight'
    FIELDS = [
        'EquityHolder',
        'TradedShares',
        'StartDate',
        'EndDate',
        'LaterHoldingShares',
        'AveragePrice',
    ]

    def __init__(self, recguid=None):
        super().__init__(
            EquityUnderweightEvent.FIELDS, event_name=EquityUnderweightEvent.NAME, recguid=recguid
        )
        self.set_key_fields([
            'EquityHolder',
            'TradedShares',
        ])

    def is_good_candidate(self, min_match_count=4):
        key_flag = self.is_key_complete()
        if key_flag:
            if self.nonempty_count >= min_match_count:
                return True
        return False


class EquityOverweightEvent(BaseEvent):
    """股权增持"""
    NAME = 'EquityOverweight'
    FIELDS = [
        'EquityHolder',
        'TradedShares',
        'StartDate',
        'EndDate',
        'LaterHoldingShares',
        'AveragePrice',
    ]

    def __init__(self, recguid=None):
        super().__init__(
            EquityOverweightEvent.FIELDS, event_name=EquityOverweightEvent.NAME, recguid=recguid
        )
        self.set_key_fields([
            'EquityHolder',
            'TradedShares',
        ])

    def is_good_candidate(self, min_match_count=4):
        key_flag = self.is_key_complete()
        if key_flag:
            if self.nonempty_count >= min_match_count:
                return True
        return False


class EquityPledgeEvent(BaseEvent):
    """股权解押"""
    NAME = 'EquityPledge'
    FIELDS = [
        'Pledger', #质押方
        'PledgedShares', # 质押股票/股份数量
        'Pledgee', # 质权方
        'TotalHoldingShares', #持有股份总数
        'TotalHoldingRatio', #质押物占持股比
        'TotalPledgedShares', # 已质押股份总数
        'StartDate', #披露时间
        'EndDate', # 结束时间
        'ReleasedDate',
    ]

    def __init__(self, recguid=None):
        # super(EquityPledgeEvent, self).__init__(
        super().__init__(
            EquityPledgeEvent.FIELDS, event_name=EquityPledgeEvent.NAME, recguid=recguid
        )
        self.set_key_fields([
            'Pledger',
            'PledgedShares',
            'Pledgee',
        ])

    def is_good_candidate(self, min_match_count=5):
        key_flag = self.is_key_complete()
        if key_flag:
            if self.nonempty_count >= min_match_count:
                return True
        return False


common_fields = ['StockCode', 'StockAbbr', 'CompanyName']


event_type2event_class = {
    EquityFreezeEvent.NAME: EquityFreezeEvent,
    EquityRepurchaseEvent.NAME: EquityRepurchaseEvent,
    EquityUnderweightEvent.NAME: EquityUnderweightEvent,
    EquityOverweightEvent.NAME: EquityOverweightEvent,
    EquityPledgeEvent.NAME: EquityPledgeEvent,
}


event_type_fields_list = [
    (EquityFreezeEvent.NAME, EquityFreezeEvent.FIELDS),
    (EquityRepurchaseEvent.NAME, EquityRepurchaseEvent.FIELDS),
    (EquityUnderweightEvent.NAME, EquityUnderweightEvent.FIELDS),
    (EquityOverweightEvent.NAME, EquityOverweightEvent.FIELDS),
    (EquityPledgeEvent.NAME, EquityPledgeEvent.FIELDS),
]


