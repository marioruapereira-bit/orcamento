import React, { useState, useMemo } from "react";

const DATA = {"budget": {"Habitação - Prestação": 1500, "Habitação - Empregada doméstica": 100, "Habitação - Obras": 0, "Utilities - Eletricidade": 55, "Utilities - Gás": 40, "Utilities - Telecomunicações": 40, "Utilities - Água": 35, "Alimentação / Supermercado": 400, "Restaurantes / Café": 150, "Automóvel - Combustível": 130, "Automóvel - Via Verde": 40, "Automóvel - Leasing": 55, "Automóvel - Manutenção": 30, "Educação - Desporto": 65, "Educação - Escola de Línguas": 50, "Educação - ATL / Centro Social": 30, "Seguros": 100, "Saúde": 60, "Lazer": 80, "Compras": 100, "Transporte": 40, "Vinhos - Garrafeira": 50, "Vinhos - Particular": 50, "Outros": 80}, "catOrder": ["Habitação - Prestação", "Habitação - Empregada doméstica", "Habitação - Obras", "Utilities - Eletricidade", "Utilities - Gás", "Utilities - Telecomunicações", "Utilities - Água", "Alimentação / Supermercado", "Restaurantes / Café", "Automóvel - Combustível", "Automóvel - Via Verde", "Automóvel - Leasing", "Automóvel - Manutenção", "Educação - Desporto", "Educação - Escola de Línguas", "Educação - ATL / Centro Social", "Seguros", "Saúde", "Lazer", "Compras", "Transporte", "Vinhos - Garrafeira", "Vinhos - Particular", "Outros"], "transactions": [{"date": "2026-01-01", "desc": "PAG.PRESTACAO EMP. 2022504333", "cat": "Habitação - Prestação", "amount": 305}, {"date": "2026-01-01", "desc": "DD ASSOCIACAO DESPORTIVA MARISTA", "cat": "Educação - Desporto", "amount": 8}, {"date": "2026-01-02", "desc": "DD LISBOAGAS", "cat": "Utilities - Gás", "amount": 39.76}, {"date": "2026-01-02", "desc": "PADARIA PORTUGUESA", "cat": "Alimentação / Supermercado", "amount": 44.86}, {"date": "2026-01-02", "desc": "IKEA LOURES", "cat": "Compras", "amount": 31.05}, {"date": "2026-01-03", "desc": "DD VODAFONE", "cat": "Utilities - Telecomunicações", "amount": 37.56}, {"date": "2026-01-03", "desc": "REPSOL RESTELO", "cat": "Automóvel - Combustível", "amount": 71.53}, {"date": "2026-01-04", "desc": "DD IBERDROLA", "cat": "Utilities - Eletricidade", "amount": 45.63}, {"date": "2026-01-04", "desc": "INTERMARCHE RESTELO", "cat": "Alimentação / Supermercado", "amount": 20.12}, {"date": "2026-01-04", "desc": "TRF MATIAS PEREIRA", "cat": "Outros", "amount": 40.74}, {"date": "2026-01-05", "desc": "DD ASISA VIDA 1849910", "cat": "Seguros", "amount": 10.75}, {"date": "2026-01-06", "desc": "BOZZOLO PIZZA", "cat": "Restaurantes / Café", "amount": 28.32}, {"date": "2026-01-08", "desc": "TRF MB WAY P/ FERNANDA MARIA", "cat": "Habitação - Empregada doméstica", "amount": 76.5}, {"date": "2026-01-08", "desc": "DD MERCEDES BENZ FINANCIAL", "cat": "Automóvel - Leasing", "amount": 53.71}, {"date": "2026-01-08", "desc": "MY AUCHAN ALTO MOINHOS", "cat": "Alimentação / Supermercado", "amount": 79.04}, {"date": "2026-01-08", "desc": "SPORT LISBOA E BENFICA", "cat": "Lazer", "amount": 28.17}, {"date": "2026-01-10", "desc": "PADARIA PORTUGUESA", "cat": "Alimentação / Supermercado", "amount": 55.2}, {"date": "2026-01-11", "desc": "TRF C SOCIAL PAROQUIAL", "cat": "Educação - ATL / Centro Social", "amount": 31.98}, {"date": "2026-01-12", "desc": "DD GENERALI TRANQUILIDADE", "cat": "Seguros", "amount": 28.59}, {"date": "2026-01-12", "desc": "CONTINENTE BOM DIA", "cat": "Alimentação / Supermercado", "amount": 58.56}, {"date": "2026-01-13", "desc": "DD ASISA VIDA 1849912", "cat": "Seguros", "amount": 62.04}, {"date": "2026-01-13", "desc": "MY AUCHAN ALTO MOINHOS", "cat": "Alimentação / Supermercado", "amount": 44.47}, {"date": "2026-01-13", "desc": "IMPOSTO SELO", "cat": "Outros", "amount": 31.16}, {"date": "2026-01-14", "desc": "TICKET LINE", "cat": "Lazer", "amount": 17.77}, {"date": "2026-01-15", "desc": "OCEANARIO DE LISBOA", "cat": "Lazer", "amount": 15.15}, {"date": "2026-01-16", "desc": "FARMACIA TAVARES", "cat": "Saúde", "amount": 40.73}, {"date": "2026-01-17", "desc": "EL CORTE INGLES", "cat": "Compras", "amount": 24.55}, {"date": "2026-01-18", "desc": "LEV ATM", "cat": "Outros", "amount": 37.21}, {"date": "2026-01-19", "desc": "DD ASSOCIACAO DESPORTIVA MARISTA", "cat": "Educação - Desporto", "amount": 32}, {"date": "2026-01-20", "desc": "PAGSERV EPAL", "cat": "Utilities - Água", "amount": 33.49}, {"date": "2026-01-20", "desc": "PADARIA PORTUGUESA", "cat": "Alimentação / Supermercado", "amount": 26.12}, {"date": "2026-01-21", "desc": "PAG.PRESTACAO EMP. 2224419533", "cat": "Habitação - Prestação", "amount": 1505.76}, {"date": "2026-01-21", "desc": "CAFETARIA DO PACO", "cat": "Restaurantes / Café", "amount": 35.95}, {"date": "2026-01-22", "desc": "RESTAURANTE A RODA", "cat": "Restaurantes / Café", "amount": 48.24}, {"date": "2026-01-23", "desc": "DD VIAVERDE", "cat": "Automóvel - Via Verde", "amount": 15.86}, {"date": "2026-01-23", "desc": "PINGO DOCE COLOMBO", "cat": "Alimentação / Supermercado", "amount": 17.98}, {"date": "2026-01-23", "desc": "PADARIA PORTUGUESA", "cat": "Alimentação / Supermercado", "amount": 57.12}, {"date": "2026-01-23", "desc": "FARMACIA TAVARES", "cat": "Saúde", "amount": 15.87}, {"date": "2026-01-25", "desc": "DD GENERALI TRANQUILIDADE", "cat": "Seguros", "amount": 10.75}, {"date": "2026-01-25", "desc": "PASTEIS DE BELEM", "cat": "Restaurantes / Café", "amount": 21.85}, {"date": "2026-01-26", "desc": "CEPSA BELEM", "cat": "Automóvel - Combustível", "amount": 51.05}, {"date": "2026-01-26", "desc": "UBER TRIP", "cat": "Transporte", "amount": 10.56}, {"date": "2026-01-27", "desc": "MY AUCHAN ALTO MOINHOS", "cat": "Alimentação / Supermercado", "amount": 25.57}, {"date": "2026-01-28", "desc": "MY AUCHAN ALTO MOINHOS", "cat": "Alimentação / Supermercado", "amount": 52.53}, {"date": "2026-01-28", "desc": "CONTINENTE BOM DIA", "cat": "Alimentação / Supermercado", "amount": 71.32}, {"date": "2026-02-01", "desc": "PASTEIS DE BELEM", "cat": "Restaurantes / Café", "amount": 42.44}, {"date": "2026-02-02", "desc": "UBER EATS", "cat": "Restaurantes / Café", "amount": 14.9}, {"date": "2026-02-03", "desc": "RESTAURANTE A RODA", "cat": "Restaurantes / Café", "amount": 12.9}, {"date": "2026-02-03", "desc": "IMPOSTO SELO", "cat": "Outros", "amount": 42.32}, {"date": "2026-02-04", "desc": "TICKET LINE", "cat": "Lazer", "amount": 17.57}, {"date": "2026-02-05", "desc": "TICKET LINE", "cat": "Lazer", "amount": 14.56}, {"date": "2026-02-06", "desc": "TRF MB WAY P/ FERNANDA MARIA", "cat": "Habitação - Empregada doméstica", "amount": 76.5}, {"date": "2026-02-06", "desc": "MY AUCHAN ALTO MOINHOS", "cat": "Alimentação / Supermercado", "amount": 49.3}, {"date": "2026-02-08", "desc": "DD ASISA VIDA 1849912", "cat": "Seguros", "amount": 10.75}, {"date": "2026-02-08", "desc": "DD ASISA VIDA 1849912", "cat": "Seguros", "amount": 10.75}, {"date": "2026-02-08", "desc": "CEPSA BELEM", "cat": "Automóvel - Combustível", "amount": 61.76}, {"date": "2026-02-09", "desc": "IMPOSTO SELO", "cat": "Outros", "amount": 19.99}, {"date": "2026-02-10", "desc": "PAG.PRESTACAO EMP. 2022504333", "cat": "Habitação - Prestação", "amount": 305}, {"date": "2026-02-10", "desc": "PAGSERV EPAL", "cat": "Utilities - Água", "amount": 43.06}, {"date": "2026-02-10", "desc": "GARRAFINHAS BELEM", "cat": "Vinhos - Garrafeira", "amount": 175.35}, {"date": "2026-02-11", "desc": "PAG.PRESTACAO EMP. 2224419533", "cat": "Habitação - Prestação", "amount": 1505.76}, {"date": "2026-02-12", "desc": "TRF C SOCIAL PAROQUIAL", "cat": "Educação - ATL / Centro Social", "amount": 26.12}, {"date": "2026-02-13", "desc": "ZIPPY KIDSTORE", "cat": "Compras", "amount": 50.63}, {"date": "2026-02-15", "desc": "ZIPPY KIDSTORE", "cat": "Compras", "amount": 20.69}, {"date": "2026-02-15", "desc": "TRF P/ PISTACHO ARQUITECTURA", "cat": "Habitação - Obras", "amount": 455.65}, {"date": "2026-02-16", "desc": "DD ASSOCIACAO DESPORTIVA MARISTA", "cat": "Educação - Desporto", "amount": 8}, {"date": "2026-02-16", "desc": "DD ASISA VIDA 1849912", "cat": "Seguros", "amount": 61.71}, {"date": "2026-02-16", "desc": "TICKET LINE", "cat": "Lazer", "amount": 13.14}, {"date": "2026-02-17", "desc": "DD VODAFONE", "cat": "Utilities - Telecomunicações", "amount": 37.56}, {"date": "2026-02-17", "desc": "INTERMARCHE RESTELO", "cat": "Alimentação / Supermercado", "amount": 22.87}, {"date": "2026-02-18", "desc": "DD MERCEDES BENZ FINANCIAL", "cat": "Automóvel - Leasing", "amount": 53.71}, {"date": "2026-02-18", "desc": "DD ASISA VIDA 1849910", "cat": "Seguros", "amount": 34.78}, {"date": "2026-02-18", "desc": "PADARIA PORTUGUESA", "cat": "Alimentação / Supermercado", "amount": 59.84}, {"date": "2026-02-18", "desc": "UBER EATS", "cat": "Restaurantes / Café", "amount": 37.3}, {"date": "2026-02-18", "desc": "UBER TRIP", "cat": "Transporte", "amount": 5.54}, {"date": "2026-02-18", "desc": "TRF RUI MANUEL MONTEIRO", "cat": "Vinhos - Particular", "amount": 83.26}, {"date": "2026-02-20", "desc": "DD ASSOCIACAO DESPORTIVA MARISTA", "cat": "Educação - Desporto", "amount": 32}, {"date": "2026-02-20", "desc": "INTERMARCHE RESTELO", "cat": "Alimentação / Supermercado", "amount": 77.68}, {"date": "2026-02-21", "desc": "ZIPPY KIDSTORE", "cat": "Compras", "amount": 25.33}, {"date": "2026-02-22", "desc": "INTERMARCHE RESTELO", "cat": "Alimentação / Supermercado", "amount": 76.55}, {"date": "2026-02-22", "desc": "PADARIA PORTUGUESA", "cat": "Alimentação / Supermercado", "amount": 39.27}, {"date": "2026-02-23", "desc": "MY AUCHAN ALTO MOINHOS", "cat": "Alimentação / Supermercado", "amount": 40.93}, {"date": "2026-02-24", "desc": "DD IBERDROLA", "cat": "Utilities - Eletricidade", "amount": 42.08}, {"date": "2026-02-25", "desc": "DD LISBOAGAS", "cat": "Utilities - Gás", "amount": 49.3}, {"date": "2026-02-25", "desc": "DD VIAVERDE", "cat": "Automóvel - Via Verde", "amount": 10.14}, {"date": "2026-02-28", "desc": "CEPSA BELEM", "cat": "Automóvel - Combustível", "amount": 37.83}, {"date": "2026-02-28", "desc": "IKEA LOURES", "cat": "Compras", "amount": 41.11}, {"date": "2026-03-02", "desc": "TRF MB WAY P/ FERNANDA MARIA", "cat": "Habitação - Empregada doméstica", "amount": 76.5}, {"date": "2026-03-02", "desc": "DD ASSOCIACAO DESPORTIVA MARISTA", "cat": "Educação - Desporto", "amount": 32}, {"date": "2026-03-02", "desc": "DD ASISA VIDA 1849912", "cat": "Seguros", "amount": 10.75}, {"date": "2026-03-03", "desc": "MEU SUPER BELEM", "cat": "Alimentação / Supermercado", "amount": 28.86}, {"date": "2026-03-04", "desc": "NOS CINEMAS COLOMBO", "cat": "Lazer", "amount": 28.05}, {"date": "2026-03-05", "desc": "SPORT LISBOA E BENFICA", "cat": "Lazer", "amount": 15.61}, {"date": "2026-03-05", "desc": "TRF NOS OUTROS ENSINO LINGUAS", "cat": "Educação - Escola de Línguas", "amount": 145.47}, {"date": "2026-03-06", "desc": "DD ASISA VIDA 1849912", "cat": "Seguros", "amount": 10.75}, {"date": "2026-03-07", "desc": "PAG.PRESTACAO EMP. 2022504333", "cat": "Habitação - Prestação", "amount": 305}, {"date": "2026-03-07", "desc": "PADARIA PORTUGUESA", "cat": "Alimentação / Supermercado", "amount": 61.55}, {"date": "2026-03-08", "desc": "MY AUCHAN ALTO MOINHOS", "cat": "Alimentação / Supermercado", "amount": 40.73}, {"date": "2026-03-08", "desc": "RESTAURANTE A RODA", "cat": "Restaurantes / Café", "amount": 24.25}, {"date": "2026-03-09", "desc": "CONTINENTE BOM DIA", "cat": "Alimentação / Supermercado", "amount": 75.66}, {"date": "2026-03-09", "desc": "CENTRO COMERCIAL", "cat": "Outros", "amount": 39.65}, {"date": "2026-03-10", "desc": "PAGSERV EPAL", "cat": "Utilities - Água", "amount": 32.32}, {"date": "2026-03-10", "desc": "PASTELARIA GARCIA", "cat": "Restaurantes / Café", "amount": 54.31}, {"date": "2026-03-11", "desc": "PINGO DOCE COLOMBO", "cat": "Alimentação / Supermercado", "amount": 15.61}, {"date": "2026-03-13", "desc": "DD IBERDROLA", "cat": "Utilities - Eletricidade", "amount": 51.85}, {"date": "2026-03-14", "desc": "DD VODAFONE", "cat": "Utilities - Telecomunicações", "amount": 37.56}, {"date": "2026-03-14", "desc": "PADARIA PORTUGUESA", "cat": "Alimentação / Supermercado", "amount": 52.94}, {"date": "2026-03-14", "desc": "UBER TRIP", "cat": "Transporte", "amount": 4.48}, {"date": "2026-03-15", "desc": "DD LISBOAGAS", "cat": "Utilities - Gás", "amount": 48.16}, {"date": "2026-03-15", "desc": "CONFEITARIA NACIONAL", "cat": "Restaurantes / Café", "amount": 35.36}, {"date": "2026-03-16", "desc": "PAG.PRESTACAO EMP. 2022504333", "cat": "Habitação - Prestação", "amount": 1505.76}, {"date": "2026-03-17", "desc": "TRF C SOCIAL PAROQUIAL", "cat": "Educação - ATL / Centro Social", "amount": 30.03}, {"date": "2026-03-17", "desc": "MY AUCHAN ALTO MOINHOS", "cat": "Alimentação / Supermercado", "amount": 75.76}, {"date": "2026-03-18", "desc": "IMPOSTO SELO", "cat": "Outros", "amount": 32.44}, {"date": "2026-03-19", "desc": "DD VIAVERDE", "cat": "Automóvel - Via Verde", "amount": 21.56}, {"date": "2026-03-19", "desc": "DD ASSOCIACAO DESPORTIVA MARISTA", "cat": "Educação - Desporto", "amount": 8}, {"date": "2026-03-19", "desc": "DD ASISA VIDA 1849910", "cat": "Seguros", "amount": 29.04}, {"date": "2026-03-20", "desc": "PINGO DOCE COLOMBO", "cat": "Alimentação / Supermercado", "amount": 55.26}, {"date": "2026-03-20", "desc": "MEU SUPER BELEM", "cat": "Alimentação / Supermercado", "amount": 79.75}, {"date": "2026-03-20", "desc": "SANTOGAL MOTORES", "cat": "Automóvel - Manutenção", "amount": 183.56}, {"date": "2026-03-21", "desc": "PRIMARK COLOMBO", "cat": "Compras", "amount": 68.07}, {"date": "2026-03-22", "desc": "DD ASISA VIDA 1849910", "cat": "Seguros", "amount": 71.9}, {"date": "2026-03-22", "desc": "PADARIA PORTUGUESA", "cat": "Alimentação / Supermercado", "amount": 34.5}, {"date": "2026-03-22", "desc": "BP ALTO MOINHOS", "cat": "Automóvel - Combustível", "amount": 46.98}, {"date": "2026-03-22", "desc": "REPSOL RESTELO", "cat": "Automóvel - Combustível", "amount": 72.56}, {"date": "2026-03-23", "desc": "PRIMARK COLOMBO", "cat": "Compras", "amount": 36.38}, {"date": "2026-03-24", "desc": "DD MERCEDES BENZ FINANCIAL", "cat": "Automóvel - Leasing", "amount": 53.71}, {"date": "2026-03-25", "desc": "CENTRO COMERCIAL", "cat": "Outros", "amount": 35.48}, {"date": "2026-03-28", "desc": "METROPOLITANO LISB", "cat": "Transporte", "amount": 5.02}, {"date": "2026-04-01", "desc": "DD ASSOCIACAO DESPORTIVA MARISTA", "cat": "Educação - Desporto", "amount": 32}, {"date": "2026-04-02", "desc": "TRF MB WAY P/ FERNANDA MARIA", "cat": "Habitação - Empregada doméstica", "amount": 76.5}, {"date": "2026-04-02", "desc": "DD IBERDROLA", "cat": "Utilities - Eletricidade", "amount": 51.48}, {"date": "2026-04-02", "desc": "DD OCIDENTAL MULTIRRISCOS", "cat": "Seguros", "amount": 67.65}, {"date": "2026-04-04", "desc": "MY AUCHAN ALTO MOINHOS", "cat": "Alimentação / Supermercado", "amount": 26.61}, {"date": "2026-04-04", "desc": "BOZZOLO PIZZA", "cat": "Restaurantes / Café", "amount": 50.68}, {"date": "2026-04-06", "desc": "DD MERCEDES BENZ FINANCIAL", "cat": "Automóvel - Leasing", "amount": 53.71}, {"date": "2026-04-07", "desc": "RESTAURANTE A RODA", "cat": "Restaurantes / Café", "amount": 13.91}, {"date": "2026-04-07", "desc": "EL CORTE INGLES", "cat": "Compras", "amount": 97.5}, {"date": "2026-04-08", "desc": "DD LISBOAGAS", "cat": "Utilities - Gás", "amount": 30.25}, {"date": "2026-04-08", "desc": "DD VIAVERDE", "cat": "Automóvel - Via Verde", "amount": 20.96}, {"date": "2026-04-08", "desc": "CENTRO COMERCIAL", "cat": "Outros", "amount": 15.89}, {"date": "2026-04-09", "desc": "DD ASISA VIDA 1849910", "cat": "Seguros", "amount": 10.75}, {"date": "2026-04-09", "desc": "PINGO DOCE COLOMBO", "cat": "Alimentação / Supermercado", "amount": 77.85}, {"date": "2026-04-09", "desc": "MY AUCHAN ALTO MOINHOS", "cat": "Alimentação / Supermercado", "amount": 56.7}, {"date": "2026-04-09", "desc": "PINGO DOCE COLOMBO", "cat": "Alimentação / Supermercado", "amount": 22.05}, {"date": "2026-04-10", "desc": "WELLS SAUDE", "cat": "Saúde", "amount": 19.44}, {"date": "2026-04-10", "desc": "GARRAFINHAS BELEM", "cat": "Vinhos - Garrafeira", "amount": 66.73}, {"date": "2026-04-11", "desc": "TICKET LINE", "cat": "Lazer", "amount": 26.82}, {"date": "2026-04-12", "desc": "PAG.PRESTACAO EMP. 2224419533", "cat": "Habitação - Prestação", "amount": 1505.76}, {"date": "2026-04-12", "desc": "DD VODAFONE", "cat": "Utilities - Telecomunicações", "amount": 37.56}, {"date": "2026-04-12", "desc": "CAFETARIA DO PACO", "cat": "Restaurantes / Café", "amount": 45.82}, {"date": "2026-04-12", "desc": "CEPSA BELEM", "cat": "Automóvel - Combustível", "amount": 37.8}, {"date": "2026-04-13", "desc": "PADARIA PORTUGUESA", "cat": "Alimentação / Supermercado", "amount": 78.77}, {"date": "2026-04-14", "desc": "PAG.PRESTACAO EMP. 2224419533", "cat": "Habitação - Prestação", "amount": 305}, {"date": "2026-04-14", "desc": "TRF C SOCIAL PAROQUIAL", "cat": "Educação - ATL / Centro Social", "amount": 32.82}, {"date": "2026-04-14", "desc": "PASTELARIA GARCIA", "cat": "Restaurantes / Café", "amount": 54.32}, {"date": "2026-04-14", "desc": "PASTEIS DE BELEM", "cat": "Restaurantes / Café", "amount": 34.36}, {"date": "2026-04-15", "desc": "DD GENERALI TRANQUILIDADE", "cat": "Seguros", "amount": 27.22}, {"date": "2026-04-15", "desc": "METROPOLITANO LISB", "cat": "Transporte", "amount": 9.62}, {"date": "2026-04-17", "desc": "TRF MATIAS PEREIRA", "cat": "Outros", "amount": 13.74}, {"date": "2026-04-18", "desc": "MY AUCHAN ALTO MOINHOS", "cat": "Alimentação / Supermercado", "amount": 76.05}, {"date": "2026-04-18", "desc": "OCEANARIO DE LISBOA", "cat": "Lazer", "amount": 13.18}, {"date": "2026-04-18", "desc": "IKEA LOURES", "cat": "Compras", "amount": 46.91}, {"date": "2026-04-18", "desc": "TRF MANUEL PINA", "cat": "Vinhos - Particular", "amount": 172.25}, {"date": "2026-04-20", "desc": "TOYS R US", "cat": "Compras", "amount": 46.6}, {"date": "2026-04-21", "desc": "UBER TRIP", "cat": "Transporte", "amount": 9.11}, {"date": "2026-04-22", "desc": "CONTINENTE BOM DIA", "cat": "Alimentação / Supermercado", "amount": 40.9}, {"date": "2026-04-22", "desc": "CEPSA BELEM", "cat": "Automóvel - Combustível", "amount": 59.93}, {"date": "2026-04-22", "desc": "ZIPPY KIDSTORE", "cat": "Compras", "amount": 109.79}, {"date": "2026-04-23", "desc": "DD ASISA VIDA 1849912", "cat": "Seguros", "amount": 10.75}, {"date": "2026-04-24", "desc": "PAGSERV EPAL", "cat": "Utilities - Água", "amount": 44.61}, {"date": "2026-04-24", "desc": "DD ASSOCIACAO DESPORTIVA MARISTA", "cat": "Educação - Desporto", "amount": 8}, {"date": "2026-04-25", "desc": "CENTRO COMERCIAL", "cat": "Outros", "amount": 36.91}, {"date": "2026-04-26", "desc": "PASTELARIA GARCIA", "cat": "Restaurantes / Café", "amount": 41.53}, {"date": "2026-04-26", "desc": "METROPOLITANO LISB", "cat": "Transporte", "amount": 11.25}, {"date": "2026-04-27", "desc": "CONTINENTE BOM DIA", "cat": "Alimentação / Supermercado", "amount": 29.49}, {"date": "2026-04-28", "desc": "LUSIADAS CENTRO SA", "cat": "Saúde", "amount": 34.63}, {"date": "2026-05-01", "desc": "CONFEITARIA NACIONAL", "cat": "Restaurantes / Café", "amount": 49.87}, {"date": "2026-05-01", "desc": "TICKET LINE", "cat": "Lazer", "amount": 17.08}, {"date": "2026-05-01", "desc": "IKEA LOURES", "cat": "Compras", "amount": 82.49}, {"date": "2026-05-02", "desc": "DD MERCEDES BENZ FINANCIAL", "cat": "Automóvel - Leasing", "amount": 53.71}, {"date": "2026-05-03", "desc": "CONTINENTE BOM DIA", "cat": "Alimentação / Supermercado", "amount": 24.8}, {"date": "2026-05-03", "desc": "IMPOSTO SELO", "cat": "Outros", "amount": 10.78}, {"date": "2026-05-04", "desc": "DD ASSOCIACAO DESPORTIVA MARISTA", "cat": "Educação - Desporto", "amount": 32}, {"date": "2026-05-05", "desc": "DD LISBOAGAS", "cat": "Utilities - Gás", "amount": 34.99}, {"date": "2026-05-05", "desc": "DD ASSOCIACAO DESPORTIVA MARISTA", "cat": "Educação - Desporto", "amount": 8}, {"date": "2026-05-05", "desc": "TOYS R US", "cat": "Compras", "amount": 71.08}, {"date": "2026-05-05", "desc": "EL CORTE INGLES", "cat": "Compras", "amount": 34.08}, {"date": "2026-05-07", "desc": "PINGO DOCE COLOMBO", "cat": "Alimentação / Supermercado", "amount": 41.97}, {"date": "2026-05-07", "desc": "CONFEITARIA NACIONAL", "cat": "Restaurantes / Café", "amount": 30.07}, {"date": "2026-05-08", "desc": "PAGSERV EPAL", "cat": "Utilities - Água", "amount": 41.68}, {"date": "2026-05-08", "desc": "MY AUCHAN ALTO MOINHOS", "cat": "Alimentação / Supermercado", "amount": 43.59}, {"date": "2026-05-09", "desc": "CONTINENTE BOM DIA", "cat": "Alimentação / Supermercado", "amount": 69.59}, {"date": "2026-05-09", "desc": "MEU SUPER BELEM", "cat": "Alimentação / Supermercado", "amount": 46.5}, {"date": "2026-05-09", "desc": "IMPOSTO SELO", "cat": "Outros", "amount": 20.09}, {"date": "2026-05-10", "desc": "CEPSA BELEM", "cat": "Automóvel - Combustível", "amount": 69.14}, {"date": "2026-05-11", "desc": "MY AUCHAN ALTO MOINHOS", "cat": "Alimentação / Supermercado", "amount": 73.05}, {"date": "2026-05-11", "desc": "MEU SUPER BELEM", "cat": "Alimentação / Supermercado", "amount": 45.29}, {"date": "2026-05-11", "desc": "UBER TRIP", "cat": "Transporte", "amount": 12.37}, {"date": "2026-05-13", "desc": "DD IBERDROLA", "cat": "Utilities - Eletricidade", "amount": 60.68}, {"date": "2026-05-13", "desc": "PADARIA PORTUGUESA", "cat": "Alimentação / Supermercado", "amount": 24.93}, {"date": "2026-05-13", "desc": "TOYS R US", "cat": "Compras", "amount": 74.26}, {"date": "2026-05-13", "desc": "UBER TRIP", "cat": "Transporte", "amount": 6.33}, {"date": "2026-05-15", "desc": "PAG.PRESTACAO EMP. 2022504333", "cat": "Habitação - Prestação", "amount": 305}, {"date": "2026-05-16", "desc": "REPSOL RESTELO", "cat": "Automóvel - Combustível", "amount": 72.71}, {"date": "2026-05-16", "desc": "LUSIADAS CENTRO SA", "cat": "Saúde", "amount": 18.1}, {"date": "2026-05-18", "desc": "TRF C SOCIAL PAROQUIAL", "cat": "Educação - ATL / Centro Social", "amount": 31.68}, {"date": "2026-05-18", "desc": "DD OCIDENTAL MULTIRRISCOS", "cat": "Seguros", "amount": 76.61}, {"date": "2026-05-18", "desc": "WELLS SAUDE", "cat": "Saúde", "amount": 41.22}, {"date": "2026-05-18", "desc": "LEV ATM", "cat": "Outros", "amount": 50.0}, {"date": "2026-05-20", "desc": "DD OCIDENTAL MULTIRRISCOS", "cat": "Seguros", "amount": 10.75}, {"date": "2026-05-21", "desc": "TRF MB WAY P/ FERNANDA MARIA", "cat": "Habitação - Empregada doméstica", "amount": 76.5}, {"date": "2026-05-22", "desc": "TICKET LINE", "cat": "Lazer", "amount": 27.55}, {"date": "2026-05-23", "desc": "DD VIAVERDE", "cat": "Automóvel - Via Verde", "amount": 19.26}, {"date": "2026-05-23", "desc": "MY AUCHAN ALTO MOINHOS", "cat": "Alimentação / Supermercado", "amount": 30.24}, {"date": "2026-05-24", "desc": "DD OCIDENTAL MULTIRRISCOS", "cat": "Seguros", "amount": 33.97}, {"date": "2026-05-25", "desc": "PAG.PRESTACAO EMP. 2224419533", "cat": "Habitação - Prestação", "amount": 1505.76}, {"date": "2026-05-25", "desc": "DD VODAFONE", "cat": "Utilities - Telecomunicações", "amount": 37.56}, {"date": "2026-05-25", "desc": "DD OCIDENTAL MULTIRRISCOS", "cat": "Seguros", "amount": 10.75}, {"date": "2026-05-25", "desc": "PASTELARIA GARCIA", "cat": "Restaurantes / Café", "amount": 52.68}, {"date": "2026-05-27", "desc": "CEPSA BELEM", "cat": "Automóvel - Combustível", "amount": 56.53}, {"date": "2026-06-03", "desc": "DD ASISA VIDA 1849910", "cat": "Seguros", "amount": 10.75}, {"date": "2026-06-03", "desc": "MY AUCHAN ALTO MOINHOS", "cat": "Alimentação / Supermercado", "amount": 72.31}, {"date": "2026-06-03", "desc": "SPORT LISBOA E BENFICA", "cat": "Lazer", "amount": 13.98}, {"date": "2026-06-04", "desc": "PAGSERV EPAL", "cat": "Utilities - Água", "amount": 37.1}, {"date": "2026-06-04", "desc": "INTERMARCHE RESTELO", "cat": "Alimentação / Supermercado", "amount": 77.45}, {"date": "2026-06-05", "desc": "TRF NOS OUTROS ENSINO LINGUAS", "cat": "Educação - Escola de Línguas", "amount": 146.4}, {"date": "2026-06-06", "desc": "DD MERCEDES BENZ FINANCIAL", "cat": "Automóvel - Leasing", "amount": 53.71}, {"date": "2026-06-07", "desc": "UBER TRIP", "cat": "Transporte", "amount": 5.32}, {"date": "2026-06-08", "desc": "DD IBERDROLA", "cat": "Utilities - Eletricidade", "amount": 61.61}, {"date": "2026-06-08", "desc": "DD VODAFONE", "cat": "Utilities - Telecomunicações", "amount": 37.56}, {"date": "2026-06-08", "desc": "WELLS SAUDE", "cat": "Saúde", "amount": 25.62}, {"date": "2026-06-09", "desc": "DD VIAVERDE", "cat": "Automóvel - Via Verde", "amount": 14.51}, {"date": "2026-06-09", "desc": "METROPOLITANO LISB", "cat": "Transporte", "amount": 5.33}, {"date": "2026-06-10", "desc": "DD ASSOCIACAO DESPORTIVA MARISTA", "cat": "Educação - Desporto", "amount": 8}, {"date": "2026-06-10", "desc": "TRF C SOCIAL PAROQUIAL", "cat": "Educação - ATL / Centro Social", "amount": 30.79}, {"date": "2026-06-10", "desc": "GARRAFINHAS BELEM", "cat": "Vinhos - Garrafeira", "amount": 136.2}, {"date": "2026-06-11", "desc": "CONTINENTE BOM DIA", "cat": "Alimentação / Supermercado", "amount": 69.0}, {"date": "2026-06-11", "desc": "CEPSA BELEM", "cat": "Automóvel - Combustível", "amount": 70.21}, {"date": "2026-06-12", "desc": "PAG.PRESTACAO EMP. 2224419533", "cat": "Habitação - Prestação", "amount": 1505.76}, {"date": "2026-06-12", "desc": "ZIPPY KIDSTORE", "cat": "Compras", "amount": 62.64}, {"date": "2026-06-13", "desc": "DD ASISA VIDA 1849910", "cat": "Seguros", "amount": 10.75}, {"date": "2026-06-14", "desc": "PADARIA PORTUGUESA", "cat": "Alimentação / Supermercado", "amount": 39.09}, {"date": "2026-06-14", "desc": "CONTINENTE BOM DIA", "cat": "Alimentação / Supermercado", "amount": 62.7}, {"date": "2026-06-14", "desc": "FARMACIA TAVARES", "cat": "Saúde", "amount": 28.54}, {"date": "2026-06-14", "desc": "ZIPPY KIDSTORE", "cat": "Compras", "amount": 72.79}, {"date": "2026-06-15", "desc": "TRF P/ PISTACHO ARQUITECTURA", "cat": "Habitação - Obras", "amount": 597.39}, {"date": "2026-06-16", "desc": "CONFEITARIA NACIONAL", "cat": "Restaurantes / Café", "amount": 25.98}, {"date": "2026-06-16", "desc": "UBER EATS", "cat": "Restaurantes / Café", "amount": 27.26}, {"date": "2026-06-16", "desc": "TICKET LINE", "cat": "Lazer", "amount": 29.41}, {"date": "2026-06-16", "desc": "TOYS R US", "cat": "Compras", "amount": 70.75}, {"date": "2026-06-17", "desc": "PADARIA PORTUGUESA", "cat": "Alimentação / Supermercado", "amount": 37.18}, {"date": "2026-06-17", "desc": "REPSOL RESTELO", "cat": "Automóvel - Combustível", "amount": 38.42}, {"date": "2026-06-18", "desc": "INTERMARCHE RESTELO", "cat": "Alimentação / Supermercado", "amount": 45.22}, {"date": "2026-06-18", "desc": "TRF RUI MANUEL MONTEIRO", "cat": "Vinhos - Particular", "amount": 104.86}, {"date": "2026-06-19", "desc": "PINGO DOCE COLOMBO", "cat": "Alimentação / Supermercado", "amount": 37.57}, {"date": "2026-06-19", "desc": "TRF MATIAS PEREIRA", "cat": "Outros", "amount": 49.22}, {"date": "2026-06-20", "desc": "DD LISBOAGAS", "cat": "Utilities - Gás", "amount": 45.98}, {"date": "2026-06-20", "desc": "DD ASISA VIDA 1849912", "cat": "Seguros", "amount": 33.5}, {"date": "2026-06-21", "desc": "PAG.PRESTACAO EMP. 2224419533", "cat": "Habitação - Prestação", "amount": 305}, {"date": "2026-06-21", "desc": "INTERMARCHE RESTELO", "cat": "Alimentação / Supermercado", "amount": 60.98}, {"date": "2026-06-21", "desc": "MY AUCHAN ALTO MOINHOS", "cat": "Alimentação / Supermercado", "amount": 55.03}, {"date": "2026-06-22", "desc": "BOZZOLO PIZZA", "cat": "Restaurantes / Café", "amount": 26.47}, {"date": "2026-06-23", "desc": "CEPSA BELEM", "cat": "Automóvel - Combustível", "amount": 57.23}, {"date": "2026-06-23", "desc": "OCEANARIO DE LISBOA", "cat": "Lazer", "amount": 16.27}, {"date": "2026-06-24", "desc": "IMPOSTO SELO", "cat": "Outros", "amount": 21.06}, {"date": "2026-06-25", "desc": "TRF MB WAY P/ FERNANDA MARIA", "cat": "Habitação - Empregada doméstica", "amount": 76.5}, {"date": "2026-06-25", "desc": "DD ASSOCIACAO DESPORTIVA MARISTA", "cat": "Educação - Desporto", "amount": 32}, {"date": "2026-06-25", "desc": "DD GENERALI TRANQUILIDADE", "cat": "Seguros", "amount": 62.04}, {"date": "2026-06-25", "desc": "BOZZOLO PIZZA", "cat": "Restaurantes / Café", "amount": 36.5}, {"date": "2026-06-25", "desc": "CENTRO COMERCIAL", "cat": "Outros", "amount": 17.66}, {"date": "2026-06-27", "desc": "PADARIA PORTUGUESA", "cat": "Alimentação / Supermercado", "amount": 53.51}, {"date": "2026-06-27", "desc": "CENTRO COMERCIAL", "cat": "Outros", "amount": 21.85}, {"date": "2026-06-28", "desc": "INTERMARCHE RESTELO", "cat": "Alimentação / Supermercado", "amount": 68.45}, {"date": "2026-07-01", "desc": "INTERMARCHE RESTELO", "cat": "Alimentação / Supermercado", "amount": 44.28}, {"date": "2026-07-01", "desc": "NOS CINEMAS COLOMBO", "cat": "Lazer", "amount": 14.18}, {"date": "2026-07-02", "desc": "METROPOLITANO LISB", "cat": "Transporte", "amount": 9.18}, {"date": "2026-07-03", "desc": "PAGSERV EPAL", "cat": "Utilities - Água", "amount": 31.71}, {"date": "2026-07-03", "desc": "DD ASSOCIACAO DESPORTIVA MARISTA", "cat": "Educação - Desporto", "amount": 8}, {"date": "2026-07-03", "desc": "WELLS SAUDE", "cat": "Saúde", "amount": 9.47}, {"date": "2026-07-03", "desc": "IMPOSTO SELO", "cat": "Outros", "amount": 23.92}, {"date": "2026-07-04", "desc": "TRF MB WAY P/ FERNANDA MARIA", "cat": "Habitação - Empregada doméstica", "amount": 76.5}, {"date": "2026-07-05", "desc": "DD MERCEDES BENZ FINANCIAL", "cat": "Automóvel - Leasing", "amount": 53.71}, {"date": "2026-07-06", "desc": "DD LISBOAGAS", "cat": "Utilities - Gás", "amount": 36.01}, {"date": "2026-07-06", "desc": "MEU SUPER BELEM", "cat": "Alimentação / Supermercado", "amount": 19.88}, {"date": "2026-07-06", "desc": "CONFEITARIA NACIONAL", "cat": "Restaurantes / Café", "amount": 25.23}, {"date": "2026-07-06", "desc": "UBER TRIP", "cat": "Transporte", "amount": 10.98}, {"date": "2026-07-07", "desc": "PADARIA PORTUGUESA", "cat": "Alimentação / Supermercado", "amount": 28.72}, {"date": "2026-07-08", "desc": "MY AUCHAN ALTO MOINHOS", "cat": "Alimentação / Supermercado", "amount": 60.95}, {"date": "2026-07-08", "desc": "MY AUCHAN ALTO MOINHOS", "cat": "Alimentação / Supermercado", "amount": 66.21}, {"date": "2026-07-09", "desc": "DD VODAFONE", "cat": "Utilities - Telecomunicações", "amount": 37.56}, {"date": "2026-07-09", "desc": "BP ALTO MOINHOS", "cat": "Automóvel - Combustível", "amount": 56.6}, {"date": "2026-07-10", "desc": "BP ALTO MOINHOS", "cat": "Automóvel - Combustível", "amount": 51.1}, {"date": "2026-07-11", "desc": "TRF MATIAS PEREIRA", "cat": "Outros", "amount": 36.81}, {"date": "2026-07-14", "desc": "DD GENERALI TRANQUILIDADE", "cat": "Seguros", "amount": 33.6}, {"date": "2026-07-14", "desc": "PASTEIS DE BELEM", "cat": "Restaurantes / Café", "amount": 35.42}, {"date": "2026-07-15", "desc": "DD GENERALI TRANQUILIDADE", "cat": "Seguros", "amount": 69.01}, {"date": "2026-07-15", "desc": "REPSOL RESTELO", "cat": "Automóvel - Combustível", "amount": 53.75}, {"date": "2026-07-16", "desc": "DD IBERDROLA", "cat": "Utilities - Eletricidade", "amount": 56.93}, {"date": "2026-07-19", "desc": "DD VIAVERDE", "cat": "Automóvel - Via Verde", "amount": 14.88}, {"date": "2026-07-19", "desc": "DD ASSOCIACAO DESPORTIVA MARISTA", "cat": "Educação - Desporto", "amount": 32}, {"date": "2026-07-20", "desc": "DD ASISA VIDA 1849910", "cat": "Seguros", "amount": 10.75}, {"date": "2026-07-20", "desc": "PINGO DOCE COLOMBO", "cat": "Alimentação / Supermercado", "amount": 54.63}, {"date": "2026-07-20", "desc": "INTERMARCHE RESTELO", "cat": "Alimentação / Supermercado", "amount": 33.93}, {"date": "2026-07-21", "desc": "PAG.PRESTACAO EMP. 2022504333", "cat": "Habitação - Prestação", "amount": 305}, {"date": "2026-07-21", "desc": "UBER EATS", "cat": "Restaurantes / Café", "amount": 51.06}, {"date": "2026-07-21", "desc": "UBER TRIP", "cat": "Transporte", "amount": 14.08}, {"date": "2026-07-22", "desc": "PINGO DOCE COLOMBO", "cat": "Alimentação / Supermercado", "amount": 25.21}, {"date": "2026-07-23", "desc": "PAG.PRESTACAO EMP. 2224419533", "cat": "Habitação - Prestação", "amount": 1505.76}, {"date": "2026-07-23", "desc": "INTERMARCHE RESTELO", "cat": "Alimentação / Supermercado", "amount": 19.63}, {"date": "2026-07-24", "desc": "PINGO DOCE COLOMBO", "cat": "Alimentação / Supermercado", "amount": 76.59}, {"date": "2026-07-24", "desc": "SPORT LISBOA E BENFICA", "cat": "Lazer", "amount": 24.3}, {"date": "2026-07-25", "desc": "TRF C SOCIAL PAROQUIAL", "cat": "Educação - ATL / Centro Social", "amount": 26.18}, {"date": "2026-07-25", "desc": "DD OCIDENTAL MULTIRRISCOS", "cat": "Seguros", "amount": 10.75}, {"date": "2026-07-25", "desc": "ZIPPY KIDSTORE", "cat": "Compras", "amount": 101.25}, {"date": "2026-07-27", "desc": "UBER EATS", "cat": "Restaurantes / Café", "amount": 15.07}, {"date": "2026-07-28", "desc": "CENTRO COMERCIAL", "cat": "Outros", "amount": 23.19}, {"date": "2026-08-01", "desc": "ZIPPY KIDSTORE", "cat": "Compras", "amount": 30.14}, {"date": "2026-08-02", "desc": "LEV ATM", "cat": "Outros", "amount": 19.39}, {"date": "2026-08-03", "desc": "EL CORTE INGLES", "cat": "Compras", "amount": 97.06}, {"date": "2026-08-04", "desc": "PADARIA PORTUGUESA", "cat": "Alimentação / Supermercado", "amount": 69.09}, {"date": "2026-08-05", "desc": "PINGO DOCE COLOMBO", "cat": "Alimentação / Supermercado", "amount": 32.96}, {"date": "2026-08-05", "desc": "TICKET LINE", "cat": "Lazer", "amount": 34.05}, {"date": "2026-08-05", "desc": "SPORT LISBOA E BENFICA", "cat": "Lazer", "amount": 31.48}, {"date": "2026-08-07", "desc": "DD VIAVERDE", "cat": "Automóvel - Via Verde", "amount": 13.79}, {"date": "2026-08-08", "desc": "CEPSA BELEM", "cat": "Automóvel - Combustível", "amount": 36.75}, {"date": "2026-08-09", "desc": "PRIMARK COLOMBO", "cat": "Compras", "amount": 80.44}, {"date": "2026-08-10", "desc": "PAG.PRESTACAO EMP. 2022504333", "cat": "Habitação - Prestação", "amount": 305}, {"date": "2026-08-10", "desc": "DD OCIDENTAL MULTIRRISCOS", "cat": "Seguros", "amount": 10.75}, {"date": "2026-08-10", "desc": "DD ASISA VIDA 1849912", "cat": "Seguros", "amount": 32.1}, {"date": "2026-08-10", "desc": "CONFEITARIA NACIONAL", "cat": "Restaurantes / Café", "amount": 37.24}, {"date": "2026-08-10", "desc": "GARRAFINHAS BELEM", "cat": "Vinhos - Garrafeira", "amount": 144.06}, {"date": "2026-08-11", "desc": "DD IBERDROLA", "cat": "Utilities - Eletricidade", "amount": 53.83}, {"date": "2026-08-11", "desc": "PASTELARIA GARCIA", "cat": "Restaurantes / Café", "amount": 44.8}, {"date": "2026-08-13", "desc": "FARMACIA TAVARES", "cat": "Saúde", "amount": 44.57}, {"date": "2026-08-14", "desc": "PINGO DOCE COLOMBO", "cat": "Alimentação / Supermercado", "amount": 29.61}, {"date": "2026-08-15", "desc": "PASTELARIA GARCIA", "cat": "Restaurantes / Café", "amount": 32.83}, {"date": "2026-08-15", "desc": "CEPSA BELEM", "cat": "Automóvel - Combustível", "amount": 69.78}, {"date": "2026-08-16", "desc": "PADARIA PORTUGUESA", "cat": "Alimentação / Supermercado", "amount": 33.97}, {"date": "2026-08-16", "desc": "INTERMARCHE RESTELO", "cat": "Alimentação / Supermercado", "amount": 30.84}, {"date": "2026-08-16", "desc": "WELLS SAUDE", "cat": "Saúde", "amount": 41.8}, {"date": "2026-08-17", "desc": "DD VODAFONE", "cat": "Utilities - Telecomunicações", "amount": 37.56}, {"date": "2026-08-18", "desc": "PAGSERV EPAL", "cat": "Utilities - Água", "amount": 39.86}, {"date": "2026-08-18", "desc": "TRF C SOCIAL PAROQUIAL", "cat": "Educação - ATL / Centro Social", "amount": 27.04}, {"date": "2026-08-18", "desc": "CONTINENTE BOM DIA", "cat": "Alimentação / Supermercado", "amount": 39.93}, {"date": "2026-08-18", "desc": "TRF RUI MANUEL MONTEIRO", "cat": "Vinhos - Particular", "amount": 138.74}, {"date": "2026-08-20", "desc": "DD MERCEDES BENZ FINANCIAL", "cat": "Automóvel - Leasing", "amount": 53.71}, {"date": "2026-08-20", "desc": "MEU SUPER BELEM", "cat": "Alimentação / Supermercado", "amount": 63.51}, {"date": "2026-08-21", "desc": "DD ASSOCIACAO DESPORTIVA MARISTA", "cat": "Educação - Desporto", "amount": 32}, {"date": "2026-08-21", "desc": "DD ASISA VIDA 1849910", "cat": "Seguros", "amount": 62.43}, {"date": "2026-08-21", "desc": "METROPOLITANO LISB", "cat": "Transporte", "amount": 13.37}, {"date": "2026-08-22", "desc": "BOZZOLO PIZZA", "cat": "Restaurantes / Café", "amount": 49.21}, {"date": "2026-08-22", "desc": "TRF MATIAS PEREIRA", "cat": "Outros", "amount": 49.9}, {"date": "2026-08-23", "desc": "PAG.PRESTACAO EMP. 2022504333", "cat": "Habitação - Prestação", "amount": 1505.76}, {"date": "2026-08-23", "desc": "DD OCIDENTAL MULTIRRISCOS", "cat": "Seguros", "amount": 10.75}, {"date": "2026-08-23", "desc": "MY AUCHAN ALTO MOINHOS", "cat": "Alimentação / Supermercado", "amount": 42.01}, {"date": "2026-08-23", "desc": "REPSOL RESTELO", "cat": "Automóvel - Combustível", "amount": 57.87}, {"date": "2026-08-23", "desc": "IMPOSTO SELO", "cat": "Outros", "amount": 44.9}, {"date": "2026-08-24", "desc": "LEV ATM", "cat": "Outros", "amount": 27.36}, {"date": "2026-08-25", "desc": "TRF MB WAY P/ FERNANDA MARIA", "cat": "Habitação - Empregada doméstica", "amount": 76.5}, {"date": "2026-08-25", "desc": "DD LISBOAGAS", "cat": "Utilities - Gás", "amount": 33.08}, {"date": "2026-08-25", "desc": "DD ASSOCIACAO DESPORTIVA MARISTA", "cat": "Educação - Desporto", "amount": 8}, {"date": "2026-08-26", "desc": "INTERMARCHE RESTELO", "cat": "Alimentação / Supermercado", "amount": 37.09}, {"date": "2026-08-27", "desc": "PINGO DOCE COLOMBO", "cat": "Alimentação / Supermercado", "amount": 44.99}, {"date": "2026-08-27", "desc": "PASTEIS DE BELEM", "cat": "Restaurantes / Café", "amount": 24.16}, {"date": "2026-08-28", "desc": "TICKET LINE", "cat": "Lazer", "amount": 10.69}, {"date": "2026-08-28", "desc": "ZIPPY KIDSTORE", "cat": "Compras", "amount": 116.85}, {"date": "2026-08-28", "desc": "UBER TRIP", "cat": "Transporte", "amount": 14.5}], "recurring": [{"name": "Prestação principal", "monthly": 1505.76}, {"name": "Prestação secundária", "monthly": 305}, {"name": "Empregada", "monthly": 76.5}, {"name": "Iberdrola", "monthly": 55}, {"name": "Lisboagás", "monthly": 36}, {"name": "Vodafone", "monthly": 38}, {"name": "EPAL", "monthly": 37}, {"name": "Asisa (x2)", "monthly": 21.5}, {"name": "Generali", "monthly": 70}, {"name": "Ocidental", "monthly": 30}, {"name": "Mercedes", "monthly": 53.71}, {"name": "Via Verde", "monthly": 13}, {"name": "Assoc. Desportiva", "monthly": 40}]};

const CATEGORY_COLORS = {
  "Alimentação / Supermercado":"#6E9B5A",
  "Automóvel":"#7A8E3D","Automóvel - Combustível":"#8BA04A","Automóvel - Leasing":"#6B8030","Automóvel - Manutenção":"#5D7228","Automóvel - Via Verde":"#9AAF58",
  "Compras":"#A64B4B",
  "Educação":"#7C5B9A","Educação - ATL / Centro Social":"#8C6BAA","Educação - Desporto":"#9C7BBA","Educação - Escola de Línguas":"#6C4B8A",
  "Habitação":"#1A4E3E","Habitação - Empregada doméstica":"#3A6E5E","Habitação - Obras":"#2A5E4E","Habitação - Prestação":"#4A7E6E",
  "Lazer":"#B0563C","Outros":"#8A8578","Restaurantes / Café":"#BE6E4A","Saúde":"#C08A3E","Seguros":"#5B7A8C",
  "Transporte":"#8AA36B",
  "Utilities":"#4A7C6F","Utilities - Eletricidade":"#5A8C7F","Utilities - Gás":"#3A6C5F","Utilities - Telecomunicações":"#6A9C8F","Utilities - Água":"#2A5C4F",
  "Vinhos":"#7A3040","Vinhos - Garrafeira":"#8A4050","Vinhos - Particular":"#6A2030"
};
const ML={"01":"Jan","02":"Fev","03":"Mar","04":"Abr","05":"Mai","06":"Jun","07":"Jul","08":"Ago","09":"Set","10":"Out","11":"Nov","12":"Dez"};
const eur=n=>new Intl.NumberFormat("pt-PT",{style:"currency",currency:"EUR"}).format(n||0);
const eur0=n=>new Intl.NumberFormat("pt-PT",{style:"currency",currency:"EUR",maximumFractionDigits:0}).format(n||0);
const shortCat=c=>(c||"").replace(/ \(.*\)/,"");
const shortDesc=d=>(d||"").replace(/^COMPRA \d+ /,"").replace(/^DD /,"").replace(/ CONTACTLESS$/,"").replace(/\s{2,}.*$/,"").trim();

function getMainCat(cat){return cat.includes(" - ")?cat.split(" - ")[0].trim():cat;}
function getSubCat(cat){return cat.includes(" - ")?cat.split(" - ")[1].trim():null;}

export default function Dashboard(){
  const months=useMemo(()=>[...new Set(DATA.transactions.map(t=>t.date.slice(0,7)))].sort(),[]);
  const[month,setMonth]=useState(months[months.length-1]); // null = annual view
  const[expandedCat,setExpandedCat]=useState(null);
  const[filterCat,setFilterCat]=useState(null);
  const[searchText,setSearchText]=useState("");
  const[hoveredPie,setHoveredPie]=useState(null);

  const budgetTotal=useMemo(()=>Object.values(DATA.budget).reduce((a,b)=>a+b,0),[]);
  const recurringMonthly=useMemo(()=>DATA.recurring.reduce((a,r)=>a+(r.monthly||0),0),[]);
  const monthTx=useMemo(()=>month?DATA.transactions.filter(t=>t.date.startsWith(month)):DATA.transactions,[month]);
  const monthTotal=useMemo(()=>monthTx.reduce((a,t)=>a+t.amount,0),[monthTx]);
  const nMonths=month?1:12;
  const viewBudget=budgetTotal*nMonths;

  // Build grouped structure: mainCat -> {budget, spent, subs: [{key, subLabel, budget, spent}]}
  const grouped=useMemo(()=>{
    const map={};
    for(const key of DATA.catOrder){
      const main=getMainCat(key);
      const sub=getSubCat(key);
      if(!map[main]) map[main]={budget:0,spent:0,subs:[]};
      const spent=monthTx.filter(t=>t.cat===key).reduce((a,t)=>a+t.amount,0);
      map[main].budget+=DATA.budget[key]*nMonths;
      map[main].spent+=spent;
      if(sub) map[main].subs.push({key,subLabel:sub,budget:DATA.budget[key]*nMonths,spent});
    }
    return Object.entries(map).map(([main,v])=>({main,...v})).sort((a,b)=>b.spent-a.spent);
  },[monthTx]);

  const trend=useMemo(()=>{
    const fc=filterCat, ec=expandedCat;
    return months.map(m=>{
      let txm=DATA.transactions.filter(t=>t.date.startsWith(m));
      let orc=budgetTotal;
      if(fc){
        txm=txm.filter(t=>t.cat===fc);
        orc=DATA.budget[fc]||0;
      } else if(ec){
        txm=txm.filter(t=>getMainCat(t.cat)===ec);
        orc=DATA.catOrder.filter(k=>getMainCat(k)===ec).reduce((a,k)=>a+(DATA.budget[k]||0),0);
      }
      return{m,label:ML[m.slice(5,7)]||m,gasto:txm.reduce((a,t)=>a+t.amount,0),orc};
    });
  },[months,budgetTotal,filterCat,expandedCat]);

  const vis=useMemo(()=>{
    let l=monthTx.slice();
    if(filterCat) l=l.filter(t=>t.cat===filterCat);
    else if(expandedCat) l=l.filter(t=>getMainCat(t.cat)===expandedCat);
    if(searchText){const q=searchText.toLowerCase();l=l.filter(t=>t.desc.toLowerCase().includes(q)||t.cat.toLowerCase().includes(q));}
    return l.sort((a,b)=>a.date<b.date?1:-1);
  },[monthTx,filterCat,expandedCat,searchText]);
  const visTotal=vis.reduce((a,t)=>a+t.amount,0);
  const diff=viewBudget-monthTotal;

  const handleMainClick=(main,hasSubs)=>{
    if(hasSubs){
      setExpandedCat(prev=>prev===main?null:main);
      setFilterCat(null);
    } else {
      setExpandedCat(null);
      setFilterCat(prev=>prev===main?null:main);
    }
  };
  const handleSubClick=(key)=>{
    setFilterCat(prev=>prev===key?null:key);
  };
  const clearFilter=()=>{setFilterCat(null);setExpandedCat(null);};

  const activeLabel=filterCat?shortCat(filterCat):expandedCat?expandedCat:null;

  // Trend SVG
  const trendSVG=useMemo(()=>{
    const W=600,H=180,pad=40;const xs=trend.map((_,i)=>trend.length>1?pad+i*(W-pad-12)/(trend.length-1):W/2);
    const maxV=Math.max(...trend.map(t=>Math.max(t.gasto,t.orc)),1);
    const y=v=>H-pad-(v/maxV)*(H-pad-14);
    const orcPts=trend.map((t,i)=>`${xs[i]},${y(t.orc)}`).join(" ");
    const gastoPts=trend.map((t,i)=>`${xs[i]},${y(t.gasto)}`).join(" ");
    const dots=trend.map((t,i)=><circle key={i} cx={xs[i]} cy={y(t.gasto)} r="4" fill="#1F6E5A"/>);
    const labels=trend.map((t,i)=><text key={i} x={xs[i]} y={H-12} textAnchor="middle" style={{fontFamily:"monospace",fontSize:11,fill:"#5C6B66"}}>{t.label}</text>);
    const grid=[0,.5,1].map(f=><g key={f}><line x1={pad} y1={y(maxV*f)} x2={W-8} y2={y(maxV*f)} stroke="#E4E9E6"/><text x={pad-6} y={y(maxV*f)+4} textAnchor="end" style={{fontFamily:"monospace",fontSize:10,fill:"#8B968F"}}>{Math.round(maxV*f/1000)}k</text></g>);
    return <svg viewBox={`0 0 ${W} ${H}`} style={{width:"100%",height:200}}>{grid}<polyline points={orcPts} fill="none" stroke="#B0BAB5" strokeWidth="1.5" strokeDasharray="4 4"/><polyline points={gastoPts} fill="none" stroke="#1F6E5A" strokeWidth="2.5"/>{dots}{labels}</svg>;
  },[trend]);

  // Pie chart — expense breakdown by main category for current period
  const pieData=useMemo(()=>{
    const map={};
    monthTx.forEach(t=>{const main=getMainCat(t.cat);map[main]=(map[main]||0)+t.amount;});
    return Object.entries(map).filter(([,v])=>v>0).sort((a,b)=>b[1]-a[1]).map(([name,value])=>({name,value}));
  },[monthTx]);

  const pieTotal=useMemo(()=>pieData.reduce((a,d)=>a+d.value,0),[pieData]);

  const pieSegs=useMemo(()=>{
    if(pieData.length===0) return [];
    const R=80,r=50,cx=100,cy=100;
    let a0=-Math.PI/2;
    return pieData.map((d,i)=>{
      const frac=d.value/pieTotal;const a1=a0+frac*2*Math.PI;
      const x0=cx+R*Math.cos(a0),y0=cy+R*Math.sin(a0);
      const x1=cx+R*Math.cos(a1),y1=cy+R*Math.sin(a1);
      const xi1=cx+r*Math.cos(a1),yi1=cy+r*Math.sin(a1);
      const xi0=cx+r*Math.cos(a0),yi0=cy+r*Math.sin(a0);
      const large=(a1-a0)>Math.PI?1:0;
      const path=`M${x0} ${y0} A${R} ${R} 0 ${large} 1 ${x1} ${y1} L${xi1} ${yi1} A${r} ${r} 0 ${large} 0 ${xi0} ${yi0} Z`;
      const color=CATEGORY_COLORS[d.name]||"#888";
      a0=a1;
      return{path,color,name:d.name,value:d.value,pct:Math.round(frac*100)};
    });
  },[pieData,pieTotal]);

  const pieLegend=useMemo(()=>{
    const total=pieData.reduce((a,d)=>a+d.value,0);
    return pieData.slice(0,8).map(d=>({name:d.name,pct:Math.round(d.value/total*100),value:d.value,color:CATEGORY_COLORS[d.name]||"#888"}));
  },[pieData]);

  const S={
    root:{fontFamily:"'Inter',system-ui,sans-serif",background:"#E7EBE9",color:"#17211E",minHeight:"100vh",padding:"24px clamp(14px,4vw,40px)"},
    head:{display:"flex",justifyContent:"space-between",alignItems:"flex-end",gap:16,flexWrap:"wrap",marginBottom:20,borderBottom:"1.5px solid #17211E",paddingBottom:14},
    eyebrow:{fontSize:11,letterSpacing:".18em",textTransform:"uppercase",color:"#5C6B66",fontWeight:600,marginBottom:8},
    title:{fontSize:"clamp(24px,4vw,36px)",fontWeight:600,lineHeight:1,letterSpacing:"-.01em",fontFamily:"Georgia,serif"},
    monthBar:{display:"flex",gap:3,background:"#FBFCFB",border:"1px solid #D3DAD7",borderRadius:999,padding:4},
    mBtn:(on)=>({border:"none",background:on?"#17211E":"transparent",color:on?"#fff":"#5C6B66",fontFamily:"monospace",fontSize:13,fontWeight:500,padding:"6px 12px",borderRadius:999,cursor:"pointer"}),
    kpis:{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:12,marginBottom:20},
    kpi:(hero)=>({background:hero?"#17211E":"#FBFCFB",border:`1px solid ${hero?"#17211E":"#D3DAD7"}`,borderRadius:14,padding:"16px 16px",position:"relative",overflow:"hidden"}),
    rail:(color)=>({position:"absolute",left:0,top:0,bottom:0,width:4,background:color}),
    lab:(hero)=>({fontSize:10.5,letterSpacing:".1em",textTransform:"uppercase",fontWeight:600,color:hero?"#AEB9B4":"#5C6B66",marginBottom:8}),
    val:{fontSize:24,fontWeight:600,letterSpacing:"-.02em",fontFamily:"monospace"},
    sub:{fontSize:12,color:"#8B968F",marginTop:3},
    grid:{display:"grid",gridTemplateColumns:"1.35fr 1fr",gap:16,marginBottom:16},
    panel:{background:"#FBFCFB",border:"1px solid #D3DAD7",borderRadius:16,padding:20},
    panelH:{display:"flex",justifyContent:"space-between",alignItems:"baseline",marginBottom:16},
    panelT:{fontSize:17,fontWeight:600,fontFamily:"Georgia,serif"},
    panelN:{fontSize:12,color:"#5C6B66"},
    track:{height:9,background:"#E4E9E6",borderRadius:6,position:"relative",overflow:"hidden",marginTop:6},
    trackSub:{height:6,background:"#E4E9E6",borderRadius:4,position:"relative",overflow:"hidden",marginTop:4},
    fill:(w,color)=>({position:"absolute",left:0,top:0,bottom:0,borderRadius:6,width:w+"%",background:color,transition:"width .5s cubic-bezier(.2,.7,.3,1)"}),
    dot:(color)=>({width:9,height:9,borderRadius:3,flexShrink:0,background:color}),
    dotSm:(color)=>({width:6,height:6,borderRadius:2,flexShrink:0,background:color}),
    clearBtn:{display:"inline-block",background:"#17211E",color:"#fff",fontSize:11,padding:"3px 10px",borderRadius:999,cursor:"pointer",marginLeft:8,border:"none",fontFamily:"inherit"},
    chevron:(open)=>({display:"inline-block",fontSize:10,color:"#8B968F",marginLeft:4,transition:"transform .2s",transform:open?"rotate(90deg)":"rotate(0deg)"}),
  };

  return <div style={S.root}>
    <header style={S.head}>
      <div>
        <div style={S.eyebrow}>Orçamento pessoal · 2026</div>
        <div style={S.title}>O teu mês, ao cêntimo</div>
      </div>
      <div style={S.monthBar}>
        {months.map(m=><button key={m} style={S.mBtn(m===month)} onClick={()=>{setMonth(m);setExpandedCat(null);setFilterCat(null);}}>{ML[m.slice(5,7)]||m}</button>)}
        <button style={{...S.mBtn(!month),fontFamily:"inherit",fontWeight:600,fontSize:12}} onClick={()=>{setMonth(null);setExpandedCat(null);setFilterCat(null);}}>Anual</button>
      </div>
    </header>

    <div style={S.kpis}>
      <div style={S.kpi(true)}><div style={S.rail("#3F7E6B")}/><div style={S.lab(true)}>{month?"Gasto no mês":"Gasto anual"}</div><div style={{...S.val,color:"#fff"}}>{eur0(monthTotal)}</div><div style={S.sub}>{monthTx.length} movimentos</div></div>
      <div style={S.kpi(false)}><div style={S.rail("#8B968F")}/><div style={S.lab(false)}>{month?"Orçamento":"Orçamento anual"}</div><div style={S.val}>{eur0(viewBudget)}</div></div>
      <div style={S.kpi(false)}><div style={S.rail(diff>=0?"#1F6E5A":"#B5533A")}/><div style={S.lab(false)}>{diff>=0?"Folga":"Excesso"}</div><div style={{...S.val,color:diff>=0?"#1F6E5A":"#B5533A"}}>{eur0(Math.abs(diff))}</div></div>
      <div style={S.kpi(false)}><div style={S.rail("#B98A3C")}/><div style={S.lab(false)}>Despesas fixas</div><div style={S.val}>{eur0(recurringMonthly)}</div><div style={S.sub}>{DATA.recurring.length} débitos/mês</div></div>
    </div>

    <div style={S.grid}>
      {/* LEFT: Budget bars with accordion */}
      <div style={S.panel}>
        <div style={S.panelH}><div style={S.panelT}>Orçamento vs. real</div><div style={S.panelN}>clica para expandir →</div></div>
        {grouped.map(g=>{
          const hasSubs=g.subs.length>0;
          const isExpanded=expandedCat===g.main;
          const pct=g.budget>0?g.spent/g.budget:(g.spent>0?2:0);
          const over=g.spent>g.budget&&g.budget>0;
          const color=CATEGORY_COLORS[g.main]||"#888";
          const fillW=Math.min(pct,1)*100;
          const isActive=activeLabel===g.main||(filterCat&&getMainCat(filterCat)===g.main);
          const dim=activeLabel&&!isActive?.35:1;

          return <div key={g.main} style={{marginBottom:hasSubs&&isExpanded?4:14,opacity:dim}}>
            <div style={{cursor:"pointer"}} onClick={()=>handleMainClick(g.main,hasSubs)}>
              <div style={{display:"flex",justifyContent:"space-between",alignItems:"baseline",marginBottom:5,gap:10}}>
                <span style={{fontSize:13,fontWeight:600,display:"flex",alignItems:"center",gap:8}}>
                  <span style={S.dot(color)}/>
                  {g.main}
                  {hasSubs?<span style={S.chevron(isExpanded)}>▶</span>:null}
                </span>
                <span style={{fontSize:12,color:"#5C6B66",whiteSpace:"nowrap",fontFamily:"monospace"}}>
                  <b style={{color:"#17211E"}}>{eur0(g.spent)}</b> / {eur0(g.budget)}
                  {over?<span style={{color:"#B5533A",fontWeight:600,marginLeft:4}}>+{eur0(g.spent-g.budget)}</span>:null}
                </span>
              </div>
              <div style={S.track}><div style={S.fill(fillW,over?"#B5533A":color)}/></div>
            </div>

            {hasSubs&&isExpanded?<div style={{paddingLeft:20,marginTop:8,marginBottom:10,borderLeft:"2px solid #E4E9E6"}}>
              {g.subs.filter(s=>s.spent>0||s.budget>0).map(sub=>{
                const sp=sub.budget>0?sub.spent/sub.budget:(sub.spent>0?2:0);
                const so=sub.spent>sub.budget&&sub.budget>0;
                const sc=CATEGORY_COLORS[sub.key]||color;
                const sf=Math.min(sp,1)*100;
                const subActive=filterCat===sub.key;
                return <div key={sub.key} style={{marginBottom:10,cursor:"pointer",opacity:filterCat&&!subActive?.4:1}} onClick={(e)=>{e.stopPropagation();handleSubClick(sub.key);}}>
                  <div style={{display:"flex",justifyContent:"space-between",alignItems:"baseline",marginBottom:3,gap:8}}>
                    <span style={{fontSize:12,fontWeight:subActive?600:400,display:"flex",alignItems:"center",gap:6,color:subActive?"#17211E":"#5C6B66"}}>
                      <span style={S.dotSm(sc)}/>{sub.subLabel}
                    </span>
                    <span style={{fontSize:11,color:"#8B968F",whiteSpace:"nowrap",fontFamily:"monospace"}}>
                      <b style={{color:"#5C6B66"}}>{eur0(sub.spent)}</b> / {eur0(sub.budget)}
                      {so?<span style={{color:"#B5533A",fontWeight:600,marginLeft:3}}>+{eur0(sub.spent-sub.budget)}</span>:null}
                    </span>
                  </div>
                  <div style={S.trackSub}><div style={S.fill(sf,so?"#B5533A":sc)}/></div>
                </div>;
              })}
            </div>:null}
          </div>;
        })}
      </div>

      {/* RIGHT: Transactions */}
      <div style={S.panel}>
        <div style={S.panelH}>
          <div style={S.panelT}>{activeLabel||"Movimentos"}</div>
          <div style={{...S.panelN,display:"flex",alignItems:"center"}}>
            {vis.length} mov.{activeLabel?" · "+eur0(visTotal):""}
            {activeLabel?<button style={S.clearBtn} onClick={clearFilter}>✕</button>:null}
          </div>
        </div>
        <div style={{marginBottom:12}}>
          <input type="text" placeholder="Pesquisar movimentos..." value={searchText}
            onChange={e=>setSearchText(e.target.value)}
            style={{width:"100%",padding:"8px 12px",border:"1px solid #D3DAD7",borderRadius:8,fontSize:13,fontFamily:"inherit",background:"#FBFCFB",color:"#17211E",outline:"none"}}
            onFocus={e=>{e.target.style.borderColor="#1F6E5A";}}
            onBlur={e=>{e.target.style.borderColor="#D3DAD7";}}
          />
        </div>
        {vis.length===0?<p style={{color:"#8B968F",textAlign:"center",padding:"32px 0",fontSize:14}}>Sem movimentos{activeLabel?" nesta categoria":""} neste mês.</p>:
        <div style={{maxHeight:480,overflowY:"auto"}}>
          <table style={{width:"100%",borderCollapse:"collapse",fontSize:13}}>
            <thead><tr>
              {["Data","Descrição","Valor"].map((h,i)=><th key={h} style={{textAlign:i===2?"right":"left",fontSize:10.5,letterSpacing:".09em",textTransform:"uppercase",color:"#8B968F",fontWeight:600,padding:"0 10px 8px",borderBottom:"1px solid #D3DAD7"}}>{h}</th>)}
            </tr></thead>
            <tbody>{vis.map((t,i)=><tr key={i}>
              <td style={{padding:"8px 10px",color:"#8B968F",fontSize:12,fontFamily:"monospace",borderBottom:"1px solid #EAEEEC"}}>{t.date.slice(8,10)}/{t.date.slice(5,7)}{!month?"/"+t.date.slice(2,4):""}</td>
              <td style={{padding:"8px 10px",borderBottom:"1px solid #EAEEEC"}}>{shortDesc(t.desc)}</td>
              <td style={{padding:"8px 10px",textAlign:"right",fontWeight:500,fontFamily:"monospace",borderBottom:"1px solid #EAEEEC"}}>{eur(t.amount)}</td>
            </tr>)}</tbody>
          </table>
        </div>}
      </div>
    </div>

    <div style={S.grid}>
      <div style={S.panel}>
        <div style={S.panelH}><div style={S.panelT}>Tendência{activeLabel?" · "+activeLabel:""}</div><div style={S.panelN}>{activeLabel?"vs. orçamento da categoria":"vs. orçamento total"}</div></div>
        {trendSVG}
      </div>
      <div style={S.panel}>
        <div style={S.panelH}><div style={S.panelT}>Repartição</div><div style={S.panelN}>{month?ML[month.slice(5,7)]:"Anual"} · por categoria</div></div>
        {pieSegs.length>0?<svg viewBox="0 0 200 200" style={{width:180,height:180,display:"block",margin:"0 auto"}}>
          {pieSegs.map((s,i)=><path key={i} d={s.path} fill={s.color}
            style={{cursor:"pointer",opacity:hoveredPie!==null&&hoveredPie!==i?.5:1,transition:"opacity .15s, transform .15s",transform:hoveredPie===i?"scale(1.04)":"scale(1)",transformOrigin:"100px 100px"}}
            onMouseEnter={()=>setHoveredPie(i)} onMouseLeave={()=>setHoveredPie(null)}/>)}
          <text x="100" y={hoveredPie!==null?88:95} textAnchor="middle" style={{fontFamily:"monospace",fontSize:hoveredPie!==null?10:11,fill:"#8B968F",transition:"all .15s"}}>
            {hoveredPie!==null?pieSegs[hoveredPie].name:"Total"}</text>
          <text x="100" y={hoveredPie!==null?104:112} textAnchor="middle" style={{fontFamily:"monospace",fontSize:15,fontWeight:600,fill:"#17211E"}}>
            {hoveredPie!==null?eur0(pieSegs[hoveredPie].value):eur0(pieTotal)}</text>
          {hoveredPie!==null?<text x="100" y="118" textAnchor="middle" style={{fontFamily:"monospace",fontSize:11,fill:"#8B968F"}}>
            {pieSegs[hoveredPie].pct}%</text>:null}
        </svg>:null}
        <div style={{display:"flex",flexDirection:"column",gap:7,marginTop:14}}>
          {pieLegend.map((d,i)=><div key={d.name}
            style={{display:"flex",justifyContent:"space-between",alignItems:"center",fontSize:12,cursor:"pointer",opacity:hoveredPie!==null&&pieSegs[hoveredPie]?.name!==d.name?.5:1,transition:"opacity .15s"}}
            onMouseEnter={()=>{const idx=pieSegs.findIndex(s=>s.name===d.name);if(idx>=0)setHoveredPie(idx);}}
            onMouseLeave={()=>setHoveredPie(null)}>
            <span style={{display:"flex",alignItems:"center",gap:7,color:"#5C6B66"}}><span style={{width:8,height:8,borderRadius:3,background:d.color,flexShrink:0,display:"inline-block"}}/>{d.name}</span>
            <span style={{fontFamily:"monospace",color:"#8B968F"}}>{eur0(d.value)} · {d.pct}%</span>
          </div>)}
        </div>
      </div>
    </div>
  </div>;
}
