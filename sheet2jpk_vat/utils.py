# -*- coding: utf-8 -*-

import datetime
from decimal import Decimal

Dec2Str = '{:.02f}'.format


def ExtractDate(v):
	if not v:
		return None
	return datetime.date(*map(int, v.split('-')))


def ExtractCurrency(cell):
	return Decimal(cell.plaintext().strip('zł ').replace(' ', '').replace(' ', '').replace(',', '.'))
