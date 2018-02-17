# -*- coding: utf-8 -*-

import datetime
from decimal import Decimal
from stdnum.pl import nip
from html import escape
import xmlwitch

from utils import *


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

		sum = Decimal(0.00)
		for idx, i in enumerate(sells, 1):
			with xml.tns__SprzedazWiersz():
				xml.tns__LpSprzedazy(str(idx))
				xml.tns__NrKontrahenta(nip.compact(i['NIP']))
				xml.tns__NazwaKontrahenta(i['Nazwa Kontrahenta'])
				xml.tns__AdresKontrahenta(i['Adres Kontrahenta'])
				xml.tns__DowodSprzedazy(i['Nr Faktury'])
				if i['Data Wystawienia']:
					xml.tns__DataWystawienia(ExtractDate(i['Data Wystawienia']).isoformat())
				if i['Data Sprzedaży']:
					xml.tns__DataSprzedazy(ExtractDate(i['Data Sprzedaży']).isoformat())

				# TODO: rozróżnienie na różne stawki podaktu, np. 5%, 12% itd, nie tylko 23%
				xml.tns__K_19(Dec2Str(i['Netto']))
				xml.tns__K_20(Dec2Str(i['Kwota VAT']))

			sum += i['Kwota VAT']

		with xml.tns__SprzedazCtrl():
			xml.tns__LiczbaWierszySprzedazy(str(len(sells)))
			xml.tns__PodatekNalezny(Dec2Str(sum))

		sum = Decimal(0.00)
		for idx, i in enumerate(buys, 1):
			with xml.tns__ZakupWiersz():
				xml.tns__LpZakupu(str(idx))
				xml.tns__NrDostawcy(nip.compact(i['NIP']))
				xml.tns__NazwaDostawcy(i['Nazwa Kontrahenta'])
				xml.tns__AdresDostawcy(i['Adres Kontrahenta'])
				xml.tns__DowodZakupu(i['Nr Faktury'])
				if i['Data Wystawienia']:
					xml.tns__DataZakupu(ExtractDate(i['Data Wystawienia']).isoformat())
				if i['Data Sprzedaży']:
					xml.tns__DataWplywu(ExtractDate(i['Data Sprzedaży']).isoformat())
				xml.tns__K_45(Dec2Str(i['Netto']))
				xml.tns__K_46(Dec2Str(i['Kwota VAT']))

			sum += i['Kwota VAT']

		with xml.tns__ZakupCtrl():
			xml.tns__LiczbaWierszyZakupow(str(len(buys)))
			xml.tns__PodatekNaliczony(Dec2Str(sum))

	fo.write(str(xml))


def Validate(begin, end, items):

	content = []

	for i in items:
		errors = []
		d = ExtractDate(i['Data Sprzedaży'])
		if d < begin or d > end:
			errors.append("Data <b>{}</b> wykracza poza okres raportu: <b>{}</b> - <b>{}</b>".format(escape(str(d)), escape(str(begin)), escape(str(end))))

		if not nip.is_valid(i['NIP']):
			errors.append("NIP <b>{}</b> jest nieprawidłowy".format(escape(i['NIP'])))
		else:
			i['NIP'] = nip.compact(i['NIP'])

		if errors:
			content.append("Pozycja <b>{}</b> <small>({})</small>".format(escape(i['LP']), escape(i['Nazwa Kontrahenta'])))
			content.append("""<ul class="errors">""")

			for i in errors:
				content.append("<li>{}</li>".format(i))

			content.append("""</ul>""")

	return content
