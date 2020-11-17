# -*- coding: utf-8 -*-

import collections
import datetime
from decimal import Decimal, ROUND_HALF_UP
from stdnum.pl import nip
from stdnum.eu import vat


def Dec2Str(value):
	return str(Decimal(value).quantize(Decimal('1.00'), rounding=ROUND_HALF_UP))


def Dec2Vat(value):
	return str(Decimal(value).quantize(Decimal('1'), rounding=ROUND_HALF_UP))


class InvoiceInfo:

	def __init__(self, invoice_number, invoice_date, ship_date, merchant_nip, merchant_name, merchant_adr, country, codes):
		self.invoice_number = invoice_number
		self.invoice_date = invoice_date
		self.ship_date = ship_date

		self.merchant_name = merchant_name
		self.merchant_adr = merchant_adr
		self.country = country
		self.codes = codes

		if nip.is_valid(merchant_nip):
			self.merchant_nip = nip.compact(merchant_nip)
			self.is_eu_vat = False
		elif vat.is_valid(merchant_nip):
			self.merchant_nip = vat.compact(merchant_nip)
			self.is_eu_vat = True
		else:
			self.merchant_nip = merchant_nip
			self.is_eu_vat = None

	def __eq__(self, other):

		if not isinstance(other, InvoiceInfo):
			raise TypeError("InvoiceInfo is required")

		return self.invoice_number == other.invoice_number and \
			self.merchant_nip == other.merchant_nip

	def Merge(self, other):

		self.invoice_date = self.invoice_date or other.invoice_date
		self.ship_date = self.ship_date or other.ship_date

		self.merchant_name = self.merchant_name or other.merchant_name
		self.merchant_adr = self.merchant_adr or other.merchant_adr


class InvoiceItem:

	def __init__(self, net_value, tax_percent, tax_value, is_eu_vat):

		if not tax_percent:
			raise ValueError("tax_percent cannot be empty")

		if not isinstance(tax_value, Decimal):
			raise ValueError("tax_value need to be a Decimal value")

		if not isinstance(net_value, Decimal):
			raise ValueError("net_value need to be a Decimal value")

		self.tax_percent = tax_percent
		self.tax_value = tax_value
		self.net_value = net_value
		self.is_eu_vat = is_eu_vat


class Invoice:

	def __init__(self, invoice_pos, invoice_number, country, codes, invoice_date, ship_date, tax_percent, tax_value, net_value, merchant_nip, merchant_name, merchant_adr):

		self.invoice_pos = [invoice_pos]

		self.info = InvoiceInfo(invoice_number, invoice_date, ship_date, merchant_nip, merchant_name, merchant_adr, country, codes)

		self.items = [InvoiceItem(net_value, tax_percent, tax_value, self.info.is_eu_vat)]

	def Merge(self, other):
		self.info.Merge(other.info)
		self.invoice_pos.append(other.invoice_pos)
		self.items.extend(other.items)

	def SumNetValues(self):
		return sum(i.net_value for i in self.items)

	def SumTaxValues(self):
		return sum(i.tax_value for i in self.items)

	def SumValues(self):
		net_value = Decimal(0.00)
		tax_value = Decimal(0.00)
		for i in self.items:
			net_value += i.net_value
			tax_value += i.tax_value

		return net_value, tax_value

	def GroupByTaxPercents(self):

		d = collections.defaultdict(list)
		for i in self.items:
			if i.is_eu_vat:
				d['EU'].append(i)
			else:
				d[i.tax_percent].append(i)

		for tax_percent, items in d.items():
			yield sum(i.net_value for i in items), tax_percent, sum(i.tax_value for i in items)


def ExtractDate(v):
	if not v:
		return None
	return datetime.date(*map(int, v.split('-')))


def ExtractCurrency(cell):

	v = cell.plaintext()
	if not v:
		raise ValueError("Empty value")

	return Decimal(v.strip('zł ').replace(' ', '').replace(' ', '').replace(',', '.'))
