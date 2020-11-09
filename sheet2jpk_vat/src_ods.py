# -*- coding: utf-8 -*-

import ezodf

from .utils import *


SupportedMimeTypes = ['application/vnd.oasis.opendocument.spreadsheet']
SupportedExts = (".ods",)

def OpenFile(filepath):
	return ezodf.opendoc(filepath)


def ReadData(sheet):
	sells = False
	buys = False

	sells_descr = None
	buys_descr = None
	sells_periods = {}
	buys_periods = {}

	current_period = None

	for i in range(sheet.nrows()):

		all_empty = sum(1 if cell.value is not None else 0 for cell in sheet.row(i)) == 0
		if all_empty:
			buys = False
			sells = False
			current_period = None
			descr = None

		if sells or buys:

			if sells:
				periods = sells_periods
			else:
				periods = buys_periods

			if descr is None:
				# LP	Data Sprzedaży	Data Wystawienia	Nazwa Kontrahenta	Adres Kontrahenta	NIP	Nr Faktury Kraj	Kody Netto
				descr = {cell.value: idx for idx, cell in enumerate(sheet.row(i)) if cell.value}
				continue

			values = [cell.value for cell in sheet.row(i) if cell.value]
			if len(values) == 1:
				current_period = values[0]
				periods[current_period] = []
			else:
				values = list(sheet.row(i))

				try:
					new_invoice = Invoice(
						invoice_pos = values[descr['LP']].value,
						invoice_number = values[descr['Nr Faktury']].plaintext(),
						country = values[descr['Kraj']].plaintext(),
						codes = [ i.strip().upper() for i in values[descr['Kody']].plaintext().split(' ')],

						invoice_date = ExtractDate(values[descr['Data Wystawienia']].value),

						ship_date = ExtractDate(values[descr['Data Sprzedaży']].value),

						tax_percent = values[descr['Stawka VAT']].plaintext(),
						tax_value = ExtractCurrency(values[descr['Kwota VAT']]),
						net_value = ExtractCurrency(values[descr['Netto']]),

						merchant_nip = values[descr['NIP']].plaintext(),
						merchant_name = values[descr['Nazwa Kontrahenta']].value,
						merchant_adr = values[descr['Adres Kontrahenta']].value,
					)

					for invoice in periods[current_period]:
						if invoice.info == new_invoice.info:
							invoice.Merge(new_invoice)
							break
					else:
						periods[current_period].append(new_invoice)

				except (ValueError, TypeError) as ex:
					pass

		else:
			for cell in sheet.row(i):

				if cell.value == 'Ewidencja sprzedaży VAT':
					sells = True
					buys = False
					current_period = None
					descr = None
					break
				elif cell.value == 'Ewidencja zakupów VAT':
					sells = False
					buys = True
					current_period = None
					descr = None
					break

	return sells_periods, buys_periods
