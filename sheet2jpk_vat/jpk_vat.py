# -*- coding: utf-8 -*-

import datetime
from decimal import Decimal
from stdnum.pl import nip
from html import escape
import xmlwitch

from .utils import *


def Write(fo, nip_number, name, email, begin, end, sells, buys, version=0, sysname="LibreOffice+Python3"):

	"""
	<?xml version="1.0" encoding="UTF-8"?>
	<tns:JPK xmlns:etd="http://crd.gov.pl/xml/schematy/dziedzinowe/mf/2016/01/25/eD/DefinicjeTypy/" xmlns:tns="http://jpk.mf.gov.pl/wzor/2017/11/13/1113/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
		<tns:Naglowek>
			<tns:KodFormularza kodSystemowy="JPK_VAT (3)" wersjaSchemy="1-1">JPK_VAT</tns:KodFormularza>
			<tns:WariantFormularza>3</tns:WariantFormularza>
			<tns:CelZlozenia>0</tns:CelZlozenia>
			<tns:DataWytworzeniaJPK>2018-02-17T09:30:47</tns:DataWytworzeniaJPK>
			<tns:DataOd>2018-01-01</tns:DataOd><tns:DataDo>2018-01-31</tns:DataDo>
			<tns:NazwaSystemu>nazwa programu </tns:NazwaSystemu>
		</tns:Naglowek>
		<tns:Podmiot1>
			<tns:NIP>1111111111</tns:NIP>
			<tns:PelnaNazwa>ABCDF sp. z o.o.</tns:PelnaNazwa>
			<tns:Email>adres@e-mail.pl</tns:Email>
		</tns:Podmiot1>
		<tns:SprzedazWiersz>
			<tns:LpSprzedazy>1</tns:LpSprzedazy>
			<tns:NrKontrahenta>2222222222</tns:NrKontrahenta>
			<tns:NazwaKontrahenta>KKKKKKKKKKK</tns:NazwaKontrahenta>
			<tns:AdresKontrahenta>AAAAAAAA</tns:AdresKontrahenta>
			<tns:DowodSprzedazy>111/2018</tns:DowodSprzedazy>
			<tns:DataWystawienia>2018-01-03</tns:DataWystawienia>
			<tns:DataSprzedazy>2018-01-03</tns:DataSprzedazy>
			<tns:K_19>100.78</tns:K_19>
			<tns:K_20>23.18</tns:K_20>
		</tns:SprzedazWiersz>

		<tns:SprzedazCtrl>
			<tns:LiczbaWierszySprzedazy>10</tns:LiczbaWierszySprzedazy>
			<tns:PodatekNalezny>231.80</tns:PodatekNalezny>
		</tns:SprzedazCtrl>

		<tns:ZakupWiersz>
			<tns:LpZakupu>1</tns:LpZakupu>
			<tns:NrDostawcy>9999999999</tns:NrDostawcy>
			<tns:NazwaDostawcy>ZZZZZZ</tns:NazwaDostawcy>
			<tns:AdresDostawcy>ZZZZZZ</tns:AdresDostawcy>
			<tns:DowodZakupu>100/2018</tns:DowodZakupu>
			<tns:DataZakupu>2018-01-05</tns:DataZakupu>
			<tns:DataWplywu>2018-01-05</tns:DataWplywu>
			<tns:K_45>80.25</tns:K_45>
			<tns:K_46>18.46</tns:K_46>
		</tns:ZakupWiersz>

		<tns:ZakupCtrl>
			<tns:LiczbaWierszyZakupow>7</tns:LiczbaWierszyZakupow>
			<tns:PodatekNaliczony>129.22</tns:PodatekNaliczony>
		</tns:ZakupCtrl>
	</tns:JPK>
	"""

	xml = xmlwitch.Builder(version='1.0', encoding='utf-8', indent='')
	with xml.tns__JPK(
			xmlns__etd="http://crd.gov.pl/xml/schematy/dziedzinowe/mf/2016/01/25/eD/DefinicjeTypy/",
			xmlns__tns="http://jpk.mf.gov.pl/wzor/2017/11/13/1113/",
			xmlns__xsi="http://www.w3.org/2001/XMLSchema-instance"):
		with xml.tns__Naglowek():
			xml.tns__KodFormularza('JPK_VAT', kodSystemowy="JPK_VAT (3)", wersjaSchemy="1-1")
			xml.tns__WariantFormularza(str(3))
			xml.tns__CelZlozenia(str(version))
			xml.tns__DataWytworzeniaJPK(datetime.datetime.now().isoformat(timespec='seconds'))
			xml.tns__DataOd(begin.isoformat())
			xml.tns__DataDo(end.isoformat())
			xml.tns__NazwaSystemu(sysname)

		with xml.tns__Podmiot1():
			xml.tns__NIP(nip.compact(nip_number))
			xml.tns__PelnaNazwa(name)
			if email:
				xml.tns__Email(email)

		if sells:
			sum = Decimal(0.00)
			for idx, i in enumerate(sells, 1):
				with xml.tns__SprzedazWiersz():
					xml.tns__LpSprzedazy(str(idx))
					xml.tns__NrKontrahenta(nip.compact(i.info.merchant_nip))
					xml.tns__NazwaKontrahenta(i.info.merchant_name)
					xml.tns__AdresKontrahenta(i.info.merchant_adr)
					xml.tns__DowodSprzedazy(i.info.invoice_number)
					xml.tns__DataWystawienia(i.info.invoice_date.isoformat())
					xml.tns__DataSprzedazy(i.info.ship_date.isoformat())

					# TODO: rozróżnienie na różne stawki podaktu, np. 5%, 12% itd, nie tylko 23%
					
					for net_value, tax_percent, tax_value in i.GroupByTaxPercents():
						if tax_percent == '8,00%':
							xml.tns__K_17(Dec2Str(net_value))
							xml.tns__K_18(Dec2Str(tax_value))
						elif tax_percent == '23,00%':
							xml.tns__K_19(Dec2Str(net_value))
							xml.tns__K_20(Dec2Str(tax_value))
						else:
							raise ValueError('Unknown tax: "{}"'.format(tax_percent))

						sum += tax_value

			with xml.tns__SprzedazCtrl():
				xml.tns__LiczbaWierszySprzedazy(str(len(sells)))
				xml.tns__PodatekNalezny(Dec2Str(sum))

		if buys:
			sum = Decimal(0.00)
			for idx, i in enumerate(buys, 1):
				with xml.tns__ZakupWiersz():
					xml.tns__LpZakupu(str(idx))
					xml.tns__NrDostawcy(nip.compact(i.info.merchant_nip))
					xml.tns__NazwaDostawcy(i.info.merchant_name)
					xml.tns__AdresDostawcy(i.info.merchant_adr)
					xml.tns__DowodZakupu(i.info.invoice_number)
					xml.tns__DataZakupu(i.info.invoice_date.isoformat())
					xml.tns__DataWplywu(i.info.ship_date.isoformat())
					
					for net_value, tax_percent, tax_value in i.GroupByTaxPercents():
						xml.tns__K_45(Dec2Str(net_value))
						xml.tns__K_46(Dec2Str(tax_value))

						sum += tax_value

			with xml.tns__ZakupCtrl():
				xml.tns__LiczbaWierszyZakupow(str(len(buys)))
				xml.tns__PodatekNaliczony(Dec2Str(sum))

	fo.write(str(xml))


def Validate(begin, end, items):

	content = []

	for i in items:
		errors = []
		d = i.info.invoice_date
		if d < begin or d > end:
			errors.append("Data <b>{}</b> wykracza poza okres raportu: <b>{}</b> - <b>{}</b>".format(escape(str(d)), escape(str(begin)), escape(str(end))))

		if not nip.is_valid(i.info.merchant_nip):
			errors.append("NIP <b>{}</b> jest nieprawidłowy".format(escape(i.info.merchant_nip)))
		else:
			imerchant_nip = nip.compact(i.info.merchant_nip)

		if errors:
			content.append("Pozycja <b>{}</b> <small>({})</small>".format(escape(i.invoice_pos), escape(i.info.merchant_name)))
			content.append("""<ul class="errors">""")

			for err in errors:
				content.append("<li>{}</li>".format(err))

			content.append("""</ul>""")

	return content
