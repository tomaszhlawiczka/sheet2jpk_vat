# -*- coding: utf-8 -*-

import ezodf

from utils import *


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
				# LP	Data Sprzedaży	Data Wystawienia	Nazwa Kontrahenta	Adres Kontrahenta	NIP	Nr Faktury	Netto
				descr = {cell.value: idx for idx, cell in enumerate(sheet.row(i)) if cell.value}
				continue

			values = [cell.value for cell in sheet.row(i) if cell.value]
			if len(values) == 1:
				current_period = values[0]
				periods[current_period] = []
			else:
				values = [cell for cell in sheet.row(i)]

				item = {
					'LP': values[descr['LP']].value,
					'Data Sprzedaży': values[descr['Data Sprzedaży']].value,
					'NIP': values[descr['NIP']].plaintext(),
					'Nr Faktury': values[descr['Nr Faktury']].plaintext(),
					'Netto': values[descr['Netto']].value,
					'Kwota VAT': values[descr['Kwota VAT']].value
				}
				if sum(1 if v is None else 0 for v in item.values()) == 0:
					item.update({
						'Data Wystawienia': values[descr['Data Wystawienia']].value,
						'Nazwa Kontrahenta': values[descr['Nazwa Kontrahenta']].value,
						'Adres Kontrahenta': values[descr['Adres Kontrahenta']].value,
						'Netto': ExtractCurrency(values[descr['Netto']]),
						'Kwota VAT': ExtractCurrency(values[descr['Kwota VAT']])
					})
					periods[current_period].append(item)
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
