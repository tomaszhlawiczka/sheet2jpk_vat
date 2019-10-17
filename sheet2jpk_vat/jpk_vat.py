# -*- coding: utf-8 -*-

import datetime
from decimal import Decimal
from stdnum.pl import nip
from stdnum.eu import vat
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

					"""
						K_10 Kwota netto – Dostawa towarów oraz świadczenie usług na terytorium kraju, zwolnione od podatku (pole opcjonalne)
						K_11 Kwota netto – Dostawa towarów oraz świadczenie usług poza terytorium kraju (pole opcjonalne)
						K_12 Kwota netto – w tym świadczenie usług, o których mowa w art. 100 ust. 1 pkt 4 ustawy (pole opcjonalne)
						✓ K_13 Kwota netto – Dostawa towarów oraz świadczenie usług na terytorium kraju, opodatkowane stawką 0% (pole opcjonalne)
						✓ K_14 Kwota netto – w tym dostawa towarów, o której mowa w art. 129 ustawy (pole opcjonalne)
						✓ K_15 Kwota netto – Dostawa towarów oraz świadczenie usług na terytorium kraju, opodatkowane stawką 5% (pole opcjonalne)
						✓ K_16 Kwota podatku należnego – Dostawa towarów oraz świadczenie usług na terytorium kraju, opodatkowane stawką 5% (pole opcjonalne)
						✓ K_17 Kwota netto – Dostawa towarów oraz świadczenie usług na terytorium kraju, opodatkowane stawką 7% albo 8% (pole opcjonalne)
						✓ K_18 Kwota podatku należnego – Dostawa towarów oraz świadczenie usług na terytorium kraju, opodatkowane stawką 7% albo 8% (pole opcjonalne)
						✓ K_19 Kwota netto – Dostawa towarów oraz świadczenie usług na terytorium kraju, opodatkowane stawką 22% albo 23% (pole opcjonalne)
						✓ K_20 Kwota podatku należnego – Dostawa towarów oraz świadczenie usług na terytorium kraju, opodatkowane stawką 22% albo 23% (pole opcjonalne)
						K_21 Kwota netto – Wewnątrzwspólnotowa dostawa towarów (pole opcjonalne)
						K_22 Kwota netto – Eksport towarów (pole opcjonalne)
						K_23 Kwota netto – Wewnątrzwspólnotowe nabycie towarów (pole opcjonalne)
						K_24 Kwota podatku należnego – Wewnątrzwspólnotowe nabycie towarów (pole opcjonalne)
						K_25 Kwota netto – Import towarów podlegający rozliczeniu zgodnie z art. 33a ustawy (pole opcjonalne)
						K_26 Kwota podatku należnego – Import towarów podlegający rozliczeniu zgodnie z art. 33a ustawy (pole opcjonalne)
						K_27 Kwota netto – Import usług z wyłączeniem usług nabywanych od podatników podatku od wartości dodanej, do których stosuje się art. 28b ustawy (pole opcjonalne)
						K_28 Kwota podatku należnego – Import usług z wyłączeniem usług nabywanych od podatników podatku od wartości dodanej, do których stosuje się art. 28b ustawy (pole opcjonalne)
						K_29 Kwota netto – Import usług nabywanych od podatników podatku od wartości dodanej, do których stosuje się art. 28b ustawy (pole opcjonalne)
						K_30 Kwota podatku należnego – Import usług nabywanych od podatników podatku od wartości dodanej, do których stosuje się art. 28b ustawy (pole opcjonalne)
						K_31 Kwota netto – Dostawa towarów oraz świadczenie usług, dla których podatnikiem jest nabywca zgodnie z art. 17 ust. 1 pkt 7 lub 8 ustawy (wypełnia dostawca) (pole opcjonalne)
						K_32 Kwota netto – Dostawa towarów, dla których podatnikiem jest nabywca zgodnie z art. 17 ust. 1 pkt 5 ustawy (wypełnia nabywca) (pole opcjonalne)
						K_33 Kwota podatku należnego – Dostawa towarów, dla których podatnikiem jest nabywca zgodnie z art. 17 ust. 1 pkt 5 ustawy (wypełnia nabywca) (pole opcjonalne)
						K_34 Kwota netto – Dostawa towarów oraz świadczenie usług, dla których podatnikiem jest nabywca zgodnie z art. 17 ust. 1 pkt 7 lub 8 ustawy (wypełnia nabywca) (pole opcjonalne) 
						K_35 Kwota podatku należnego – Dostawa towarów oraz świadczenie usług, dla których podatnikiem jest nabywca zgodnie z art. 17 ust. 1 pkt 7 lub 8 ustawy (wypełnia nabywca) (pole opcjonalne)
						K_36 Kwota podatku należnego od towarów i usług objętych spisem z natury, o którym mowa w art. 14 ust. 5 ustawy (pole opcjonalne)
						K_37 Zwrot odliczonej lub zwróconej kwoty wydatkowanej na zakup kas rejestrujących, o którym mowa w art. 111 ust. 6 ustawy (pole opcjonalne)
						K_38 Kwota podatku należnego od wewnątrzwspólnotowego nabycia środków transportu, wykazanego w poz. 24, podlegająca wpłacie w terminie, o którym mowa w art. 103 ust. 3, w związku z ust. 4 ustawy (pole opcjonalne)
						K_39 Kwota podatku od wewnątrzwspólnotowego nabycia paliw silnikowych, podlegająca wpłacie w terminach, o których mowa w art. 103 ust. 5a i 5b ustawy (pole opcjonalne)
					"""

					for net_value, tax_percent, tax_value in i.GroupByTaxPercents():
						if tax_percent == '0,00%':
							xml.tns__K_13(Dec2Str(net_value))
						elif tax_percent == '5,00%':
							xml.tns__K_15(Dec2Str(net_value))
							xml.tns__K_16(Dec2Str(tax_value))
						elif tax_percent == '8,00%':
							xml.tns__K_17(Dec2Str(net_value))
							xml.tns__K_18(Dec2Str(tax_value))
						elif tax_percent == '23,00%':
							xml.tns__K_19(Dec2Str(net_value))
							xml.tns__K_20(Dec2Str(tax_value))
						elif tax_percent == 'EU':
							xml.tns__K_11(Dec2Str(net_value))
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
					xml.tns__NrDostawcy(i.info.merchant_nip)
					xml.tns__NazwaDostawcy(i.info.merchant_name)
					xml.tns__AdresDostawcy(i.info.merchant_adr)
					xml.tns__DowodZakupu(i.info.invoice_number)
					xml.tns__DataZakupu(i.info.invoice_date.isoformat())
					xml.tns__DataWplywu(i.info.ship_date.isoformat())

					"""
						K_43 Kwota netto – Nabycie towarów i usług zaliczanych u podatnika do środków trwałych (pole opcjonalne)
						K_44 Kwota podatku naliczonego – Nabycie towarów i usług zaliczanych u podatnika do środków trwałych (pole opcjonalne)
						✓ K_45 Kwota netto – Nabycie towarów i usług pozostałych (pole opcjonalne)
						✓ K_46 Kwota podatku naliczonego – Nabycie towarów i usług pozostałych (pole opcjonalne)
						K_47 Korekta podatku naliczonego od nabycia środków trwałych (pole opcjonalne)
						K_48 Korekta podatku naliczonego od pozostałych nabyć (pole opcjonalne)
						K_49 Korekta podatku naliczonego, o której mowa w art. 89b ust. 1 ustawy (pole opcjonalne)
						K_50 Korekta podatku naliczonego, o której mowa w art. 89b ust. 4 ustawy (pole opcjonalne)
					"""

					net_value, tax_value = i.SumValues()

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
			if not vat.is_valid(i.info.merchant_nip):
				errors.append("NIP <b>{}</b> jest nieprawidłowy".format(escape(i.info.merchant_nip)))	
		else:
			imerchant_nip = nip.compact(i.info.merchant_nip)

		if errors:
			content.append("Pozycja <b>{}</b> <small>({})</small>".format(escape(','.join(i.invoice_pos)), escape(i.info.merchant_name)))
			content.append("""<ul class="errors">""")

			for err in errors:
				content.append("<li>{}</li>".format(err))

			content.append("""</ul>""")

	return content
