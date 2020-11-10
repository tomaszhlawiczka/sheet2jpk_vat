#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import datetime
import calendar
from decimal import Decimal
import collections
import itertools
import argparse
from stdnum.pl import nip
from html import escape
import xmlwitch
from dateutil.relativedelta import relativedelta

from .utils import *
# from . import ui_pyside as ui
from . import ui_qt5 as ui
from . import src_ods
from . import jpk_vat


def SelectFile(dir):
	files = sorted([i for i in os.listdir(dir) if i.endswith(src_ods.SupportedExts)])

	if not files:
		ui.MsgBoxCritical("Uwaga!", u"Wkazany katalog nie zawiera wspieranych plików z arkuszami.")
		raise ui.Cancelled()

	value = ui.SelectOneOf("Wybierz plik źródłowy", "Dostępne pliki w katalogu:", files)
	return os.path.join(dir, value)


def SelectSheet(ods):
	sheets = [i.name for i in ods.sheets]

	if not sheets:
		ui.MsgBoxCritical("Uwaga!", u"Wkazany plik nie zawiera poprawnych arkuszy.")
		raise ui.Cancelled()

	value = ui.SelectOneOf("Wybierz arkusz", "Dostępne arkusze:", sheets)
	return [i for i in ods.sheets if value == i.name][0]


def GetSurplus():
	value = ui.MsgBoxNumber("Kwota nadwyżki", "Wysokość nadwyżki podatku naliczonego nad należnym z poprzedniej deklaracji")
	return value


def SelectPeriod(sells, buys):
	periods = collections.defaultdict(int)
	for priod, items in itertools.chain(sells.items(), buys.items()):
		periods[priod] += len(items)

	periods = sorted(k for k, v in periods.items() if v > 0)

	if not periods:
		ui.MsgBoxCritical("Uwaga!", u"W wskazanym arkuszu nie udało się odnaleźć poprawnych okresów.")
		raise ui.Cancelled()

	value = ui.SelectOneOf("Wybierz", "Wybierz uzupełniony okres:", periods)

	year, month = map(int, value.split('/'))
	weekday, ndays = calendar.monthrange(year, month)

	begin = datetime.date(year, month, 1)
	end = datetime.date(year, month, ndays)

	return value, begin, end


def ValidateTable(begin, end, items):

	# https://poradnikprzedsiebiorcy.pl/-czy-wiesz-jak-ujac-w-ewidencjach-zapomniana-fakture-kosztowa
	content = jpk_vat.Validate(begin - relativedelta(months=2), end, items)

	if content:
		"""Pozycja 1.<br/><b class="error">Coś poszło źle</b>:</br/>"""
		dlg = ui.ReportDialog("".join(content))
		dlg.run()
		raise ui.Cancelled()


def ConfirmData(begin, end, sells, buys):

	content = []

	if sells:
		content.append('<b>Sprzedaż:</b><br/>')
		content.append('<table class="invoices" width="100%">')

		sum_net = Decimal(0.00)
		sum_vat = Decimal(0.00)

		for i in sells:
			content.append('<tr>')

			content.append('<td>{}</td>'.format(", ".join(map(escape, map(str, i.invoice_pos)))))
			content.append('<td>{}</td>'.format(escape(str(i.info.invoice_date))))
			content.append('<td>{}<br/><small>{}</small><br/><small>{}</small></td>'.format(escape(i.info.merchant_name or ''),
																							escape(i.info.merchant_adr or ''), escape(nip.format(i.info.merchant_nip))))
			content.append('<td>{}</td>'.format(escape(' '.join(i.info.codes))))
			content.append('<td class="currency">{:.02f} zł</td>'.format(i.SumNetValues()))
			content.append('<td class="currency">{:.02f} zł</td>'.format(i.SumTaxValues()))

			content.append('</tr>')

			sum_net += i.SumNetValues()
			sum_vat += i.SumTaxValues()

		content.append('</table><br/>')

		content.append('Suma netto: <b>{}</b><br/>'.format(Dec2Str(sum_net)))
		content.append('Suma VAT: <b>{}</b><br/>'.format(Dec2Str(sum_vat)))

	if buys:
		content.append('<b>Zakupy:</b><br/>')
		content.append('<table class="invoices" width="100%">')

		sum_net = Decimal(0.00)
		sum_vat = Decimal(0.00)

		for i in buys:
			content.append('<tr>')

			content.append('<td>{}</td>'.format(", ".join(map(escape, map(str, i.invoice_pos)))))
			content.append('<td>{}</td>'.format(escape(str(i.info.invoice_date))))
			content.append('<td>{}<br/><small>{}</small><br/><small>{}</small></td>'.format(escape(i.info.merchant_name or ''),
																							escape(i.info.merchant_adr or ''), escape(nip.format(i.info.merchant_nip))))

			content.append('<td>{}</td>'.format(escape(' '.join(i.info.codes))))
			content.append('<td class="currency">{:.02f} zł</td>'.format(i.SumNetValues()))
			content.append('<td class="currency">{:.02f} zł</td>'.format(i.SumTaxValues()))

			content.append('</tr>')

			sum_net += i.SumNetValues()
			sum_vat += i.SumTaxValues()

		content.append('</table>')

		content.append('Suma netto: <b>{}</b><br/>'.format(Dec2Str(sum_net)))
		content.append('Suma VAT: <b>{}</b><br/>'.format(Dec2Str(sum_vat)))


	dlg = ui.ReportDialog("".join(content), allow_cancel=True, msg="Potwierdz poprawność odczytanych danych")
	return dlg.run() is True


def Main(argv=None):
	try:
		cmdline = argparse.ArgumentParser()
		cmdline.add_argument("--path", default="", help="Katalog z plikami ods")
		cmdline.add_argument("--nip", default="", help="NIP firmy składającej raport JPK_VAT")
		cmdline.add_argument("--firstname", default="", help="Imię osoby fizycznej")
		cmdline.add_argument("--lastname", default="", help="Nazwisko osoby fizycznej.")
		cmdline.add_argument("--birth", default="", help="Data urodzenia osoby fizycznej np. 1999-01-30")
		cmdline.add_argument("--email", default="", help="Adres email osoby składającej raport")
		cmdline.add_argument("--type", default="", help="Typ składanej deklaracji VAT7K czy VAT7")
		cmdline.add_argument("--departmentcode", default="", help="Kod urzędu skarbowego np. 2407")
		cmdline.add_argument("--output", default="", help="Katalog na zrzut raportów JPK_VAT")
		args = cmdline.parse_args(argv)

		if not args.nip:
			raise ValueError("Podaj NIP w argumentach programu")

		if not nip.is_valid(args.nip):
			raise ValueError("Podaj poprawny NIP w argumentach programu")

		if not args.firstname:
			raise ValueError("Podaj imię osoby fizycznej")

		if not args.lastname:
			raise ValueError("Podaj nazwisko osoby fizycznej")

		if not args.birth:
			raise ValueError("Podaj date urodzienia osoby fizycznej")

		try:
			datetime.datetime.strptime(args.birth, "%Y-%m-%d")
		except ValueError:
			raise ValueError("Błędy format daty urodzenia. Poprawna wartość to np. 1999-01-30")

		if not args.type:
			raise ValueError("Podaj typ składanej deklaracji")

		if args.type not in ("VAT7K", "VAT7"):
			raise ValueError("Typ składanej deklaracji musi VAT7K lub VAT7")

		if not args.departmentcode:
			raise ValueError("Podaj kod urzędu skarbowego")


		filepath = SelectFile(args.path or os.getcwd())

		# TODO: Trzeba sprawdzić magic filepath i wybrać odpowiedni driver (np. src_ods) do otworzenia pliku

		src = src_ods.OpenFile(filepath)

		sheet = SelectSheet(src)
		sells, buys = src_ods.ReadData(sheet)
		period, begin, end = SelectPeriod(sells, buys)

		sells = sells.get(period) or []
		buys = buys.get(period) or []

		ValidateTable(begin, end, sells)
		ValidateTable(begin, end, buys)

		surplus = Decimal(GetSurplus())

		if ConfirmData(begin, end, sells, buys):

			output = args.output or os.getcwd()

			filename = os.path.join(output, "JPK_VAT_{}-{:02d}.xml".format(begin.year, begin.month))

			if os.path.exists(filename):
				if not ui.MsgBoxYesNo("Uwaga!", "Plik {} już istnieje.\nCzy go nadpisać nowymi danymi?".format(filename)):
					raise ui.Cancelled()

			with open(filename, "w") as xml:
				# TODO: dodać opcję wyboru złożenia dokumentu lub korekty - version
				tax, tax_next_month = jpk_vat.Write(xml, args.nip, args.firstname, args.lastname, args.birth, args.email, args.type == "VAT7K", args.departmentcode, begin, end, sells, buys, surplus=surplus, version=0)

			ui.MsgBoxInfo("Sukces!", "Podatek do zapłacenia {}zł\n Kwota przeniesienia na następny okres rozliczeniowy {}zł\n Utworzyony plik to:\n{}".format(tax, tax_next_month, os.path.abspath(filename)))
		return 0

	except ValueError as ex:
		raise
		print("Program napotkał błąd: {}".format(ex))
		ui.MsgBoxCritical("Program napotkał problem", str(ex))
		return 2

	except (KeyboardInterrupt, ui.Cancelled):
		return 1


if __name__ == '__main__':
	Main()
