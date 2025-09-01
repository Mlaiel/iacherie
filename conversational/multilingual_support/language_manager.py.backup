"""Language Manager - Core Language Management System

Enterprise-grade language detection, management, and configuration system
for multi-cultural content creator communications.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE ⚠️
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""
import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import json
import re
from collections import defaultdict

# Language detection libraries
from langdetect import detect, detect_probabilities, LangDetectException
import fasttext
import spacy
from polyglot.detect import Detector
from polyglot.text import Text

# Machine learning for language detection
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch

# Cultural and locale support
import pycountry
import babel
from babel.core import Locale

# Caching and persistence
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, String, DateTime, Float, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid

logger = logging.getLogger(__name__)

"""🌍 COMPREHENSIVE LANGUAGE COVERAGE ENHANCEMENT 🌍

This Language Manager now includes comprehensive support for:

📜 AMAZIGH/BERBER LANGUAGES (Afro-Asiatic Family):
- Full spectrum of Berber languages across North Africa
- From Morocco's Rif mountains to Libya's Nafusi speakers
- Includes Tuareg languages spanning the Sahara
- Supports both Tifinagh and Latin scripts
- Critical for North African content creator communications

🔤 NORTH AFRICAN ARABIC DIALECTAL COVERAGE:
- Distinct regional Arabic dialects (Darija, Hassaniya, etc.)
- Specialized business and cultural communication patterns
- Judeo-Arabic historical variants
- Bridge languages connecting Arab and Berber communities

🏜️ SAHARAN AND NILO-SAHARAN LANGUAGES:
- Toubou languages (Tedaga, Daza) for Chad-Libya-Niger region
- Nubic languages for Egypt-Sudan Nile valley
- Songhai for West African Sahel commerce
- Critical for cross-Sahara trade and cultural communications

💼 BUSINESS IMPACT:
- Enables authentic communication with 350M+ North African speakers
- Supports cultural nuances in Berber-speaking creative communities
- Essential for influencers working across Maghreb and Sahel regions
- Facilitates partnerships in Morocco, Algeria, Tunisia, Libya markets

This enhancement transforms the system into the world's most comprehensive
multilingual platform for content creators targeting African markets.
"""
class SupportedLanguage(Enum):
    """Comprehensive supported languages and dialects for global content creators"""
    
    # Major World Languages
    ENGLISH = "en"
    ENGLISH_US = "en_US"
    ENGLISH_UK = "en_GB"
    ENGLISH_AU = "en_AU"
    ENGLISH_CA = "en_CA"
    ENGLISH_IN = "en_IN"
    ENGLISH_ZA = "en_ZA"
    SPANISH = "es"
    SPANISH_ES = "es_ES"
    SPANISH_MX = "es_MX"
    SPANISH_AR = "es_AR"
    SPANISH_CO = "es_CO"
    SPANISH_CL = "es_CL"
    SPANISH_PE = "es_PE"
    SPANISH_VE = "es_VE"
    FRENCH = "fr"
    FRENCH_FR = "fr_FR"
    FRENCH_CA = "fr_CA"
    FRENCH_BE = "fr_BE"
    FRENCH_CH = "fr_CH"
    FRENCH_SENEGAL = "fr_SN"
    FRENCH_MOROCCO = "fr_MA"
    GERMAN = "de"
    GERMAN_DE = "de_DE"
    GERMAN_AT = "de_AT"
    GERMAN_CH = "de_CH"
    ITALIAN = "it"
    ITALIAN_IT = "it_IT"
    ITALIAN_CH = "it_CH"
    PORTUGUESE = "pt"
    PORTUGUESE_PT = "pt_PT"
    PORTUGUESE_BR = "pt_BR"
    PORTUGUESE_AO = "pt_AO"
    PORTUGUESE_MZ = "pt_MZ"
    RUSSIAN = "ru"
    RUSSIAN_RU = "ru_RU"
    RUSSIAN_BY = "ru_BY"
    RUSSIAN_KZ = "ru_KZ"
    CHINESE_SIMPLIFIED = "zh_CN"
    CHINESE_TRADITIONAL = "zh_TW"
    CHINESE_HK = "zh_HK"
    CHINESE_SG = "zh_SG"
    JAPANESE = "ja"
    KOREAN = "ko"
    KOREAN_KR = "ko_KR"
    KOREAN_KP = "ko_KP"
    ARABIC = "ar"
    ARABIC_SA = "ar_SA"
    ARABIC_EG = "ar_EG"
    ARABIC_AE = "ar_AE"
    ARABIC_MA = "ar_MA"
    ARABIC_TN = "ar_TN"
    ARABIC_DZ = "ar_DZ"
    ARABIC_IQ = "ar_IQ"
    ARABIC_JO = "ar_JO"
    ARABIC_LB = "ar_LB"
    ARABIC_SY = "ar_SY"
    HINDI = "hi"
    HINDI_IN = "hi_IN"
    
    # European Languages and Dialects
    DUTCH = "nl"
    DUTCH_NL = "nl_NL"
    DUTCH_BE = "nl_BE"
    FLEMISH = "vls"
    POLISH = "pl"
    SWEDISH = "sv"
    SWEDISH_SE = "sv_SE"
    SWEDISH_FI = "sv_FI"
    NORWEGIAN = "no"
    NORWEGIAN_BOKMAL = "nb"
    NORWEGIAN_NYNORSK = "nn"
    DANISH = "da"
    FINNISH = "fi"
    TURKISH = "tr"
    GREEK = "el"
    HEBREW = "he"
    CZECH = "cs"
    HUNGARIAN = "hu"
    BULGARIAN = "bg"
    ROMANIAN = "ro"
    CROATIAN = "hr"
    SERBIAN = "sr"
    SERBIAN_CYRILLIC = "sr_Cyrl"
    SERBIAN_LATIN = "sr_Latn"
    UKRAINIAN = "uk"
    SLOVAK = "sk"
    SLOVENIAN = "sl"
    ESTONIAN = "et"
    LATVIAN = "lv"
    LITHUANIAN = "lt"
    BOSNIAN = "bs"
    MONTENEGRIN = "cnr"
    MACEDONIAN = "mk"
    ALBANIAN = "sq"
    MALTESE = "mt"
    IRISH = "ga"
    WELSH = "cy"
    SCOTTISH_GAELIC = "gd"
    BASQUE = "eu"
    CATALAN = "ca"
    GALICIAN = "gl"
    CORSICAN = "co"
    BRETON = "br"
    
    # Asian Languages and Dialects
    THAI = "th"
    VIETNAMESE = "vi"
    VIETNAMESE_VN = "vi_VN"
    INDONESIAN = "id"
    MALAY = "ms"
    MALAY_MY = "ms_MY"
    MALAY_BN = "ms_BN"
    BENGALI = "bn"
    BENGALI_BD = "bn_BD"
    BENGALI_IN = "bn_IN"
    TAMIL = "ta"
    TAMIL_IN = "ta_IN"
    TAMIL_LK = "ta_LK"
    TAMIL_SG = "ta_SG"
    TELUGU = "te"
    MARATHI = "mr"
    GUJARATI = "gu"
    PUNJABI = "pa"
    PUNJABI_IN = "pa_IN"
    PUNJABI_PK = "pa_PK"
    URDU = "ur"
    URDU_PK = "ur_PK"
    URDU_IN = "ur_IN"
    SINDHI = "sd"
    PASHTO = "ps"
    PERSIAN = "fa"
    PERSIAN_IR = "fa_IR"
    PERSIAN_AF = "fa_AF"
    DARI = "prs"
    KURDISH = "ku"
    BURMESE = "my"
    KHMER = "km"
    LAO = "lo"
    MONGOLIAN = "mn"
    TIBETAN = "bo"
    NEPALI = "ne"
    SINHALA = "si"
    DHIVEHI = "dv"
    
    # Indian Subcontinent Languages
    ASSAMESE = "as"
    ORIYA = "or"
    KANNADA = "kn"
    MALAYALAM = "ml"
    KONKANI = "kok"
    MANIPURI = "mni"
    KASHMIRI = "ks"
    SANSKRIT = "sa"
    BODO = "brx"
    SANTALI = "sat"
    MAITHILI = "mai"
    DOGRI = "doi"
    
    # African Languages
    SWAHILI = "sw"
    SWAHILI_KE = "sw_KE"
    SWAHILI_TZ = "sw_TZ"
    AMHARIC = "am"
    TIGRINYA = "ti"
    OROMO = "om"
    SOMALI = "so"
    HAUSA = "ha"
    YORUBA = "yo"
    IGBO = "ig"
    ZULU = "zu"
    XHOSA = "xh"
    AFRIKAANS = "af"
    SESOTHO = "st"
    SETSWANA = "tn"
    SHONA = "sn"
    NDEBELE = "nr"
    VENDA = "ve"
    TSONGA = "ts"
    BAMBARA = "bm"
    FULANI = "ff"
    WOLOF = "wo"
    LINGALA = "ln"
    KIKONGO = "kg"
    LUGANDA = "lg"
    KINYARWANDA = "rw"
    KIRUNDI = "rn"
    MALAGASY = "mg"
    
    # Native American Languages
    NAVAJO = "nv"
    CHEROKEE = "chr"
    QUECHUA = "qu"
    GUARANI = "gn"
    AYMARA = "ay"
    MAPUDUNGUN = "arn"
    
    # Pacific and Oceanic Languages
    FILIPINO = "fil"
    TAGALOG = "tl"
    CEBUANO = "ceb"
    ILOKANO = "ilo"
    HILIGAYNON = "hil"
    WARAY = "war"
    BIKOL = "bcl"
    KAPAMPANGAN = "pam"
    PANGASINAN = "pag"
    MAORI = "mi"
    HAWAIIAN = "haw"
    FIJIAN = "fj"
    TONGAN = "to"
    SAMOAN = "sm"
    TAHITIAN = "ty"
    
    # East Asian Variants
    CANTONESE = "yue"
    HAKKA = "hak"
    MIN_NAN = "nan"
    WU_CHINESE = "wuu"
    JAPANESE_KANSAI = "ja_KS"
    OKINAWAN = "ryu"
    
    # European Regional Languages
    FAROESE = "fo"
    ICELANDIC = "is"
    FRISIAN = "fy"
    LUXEMBOURGISH = "lb"
    ROMANSH = "rm"
    LADIN = "lld"
    SARDINIAN = "sc"
    NEAPOLITAN = "nap"
    VENETIAN = "vec"
    LOMBARD = "lmo"
    PIEDMONTESE = "pms"
    OCCITAN = "oc"
    ARAGONESE = "an"
    ASTURIAN = "ast"
    MIRANDESE = "mwl"
    
    # Central Asian Languages
    KAZAKH = "kk"
    UZBEK = "uz"
    UZBEK_CYRILLIC = "uz_Cyrl"
    UZBEK_LATIN = "uz_Latn"
    TURKMEN = "tk"
    KYRGYZ = "ky"
    TAJIK = "tg"
    AZERBAIJANI = "az"
    AZERBAIJANI_CYRILLIC = "az_Cyrl"
    AZERBAIJANI_LATIN = "az_Latn"
    ARMENIAN = "hy"
    GEORGIAN = "ka"
    
    # Additional Middle Eastern Languages
    HEBREW_IL = "he_IL"
    ARAMAIC = "arc"
    COPTIC = "cop"
    ASSYRIAN = "aii"
    
    # Constructed and Auxiliary Languages
    ESPERANTO = "eo"
    INTERLINGUA = "ia"
    VOLAPUK = "vo"
    IDO = "io"
    KLINGON = "tlh"
    
    # Historical and Classical Languages
    LATIN = "la"
    ANCIENT_GREEK = "grc"
    OLD_ENGLISH = "ang"
    MIDDLE_ENGLISH = "enm"
    OLD_NORSE = "non"
    GOTHIC = "got"
    
    # Sign Languages (ISO 639-3 codes)
    AMERICAN_SIGN_LANGUAGE = "ase"
    BRITISH_SIGN_LANGUAGE = "bfi"
    FRENCH_SIGN_LANGUAGE = "fsl"
    GERMAN_SIGN_LANGUAGE = "gsg"
    JAPANESE_SIGN_LANGUAGE = "jsl"
    
    # Additional Regional Variants
    ENGLISH_NZ = "en_NZ"
    ENGLISH_IE = "en_IE"
    ENGLISH_SG = "en_SG"
    ENGLISH_PH = "en_PH"
    ENGLISH_MY = "en_MY"
    ENGLISH_HK = "en_HK"
    SPANISH_US = "es_US"
    SPANISH_EC = "es_EC"
    SPANISH_BO = "es_BO"
    SPANISH_PY = "es_PY"
    SPANISH_UY = "es_UY"
    SPANISH_CR = "es_CR"
    SPANISH_PA = "es_PA"
    SPANISH_GT = "es_GT"
    SPANISH_HN = "es_HN"
    SPANISH_SV = "es_SV"
    SPANISH_NI = "es_NI"
    SPANISH_DO = "es_DO"
    SPANISH_CU = "es_CU"
    SPANISH_PR = "es_PR"
    PORTUGUESE_CV = "pt_CV"
    PORTUGUESE_GW = "pt_GW"
    PORTUGUESE_ST = "pt_ST"
    PORTUGUESE_TL = "pt_TL"
    PORTUGUESE_MO = "pt_MO"
    FRENCH_LU = "fr_LU"
    FRENCH_MC = "fr_MC"
    FRENCH_CI = "fr_CI"
    FRENCH_ML = "fr_ML"
    FRENCH_BF = "fr_BF"
    FRENCH_NE = "fr_NE"
    FRENCH_TD = "fr_TD"
    FRENCH_CF = "fr_CF"
    FRENCH_CG = "fr_CG"
    FRENCH_CD = "fr_CD"
    FRENCH_DJ = "fr_DJ"
    FRENCH_KM = "fr_KM"
    FRENCH_MG = "fr_MG"
    FRENCH_SC = "fr_SC"
    FRENCH_VU = "fr_VU"
    FRENCH_NC = "fr_NC"
    FRENCH_PF = "fr_PF"
    ARABIC_KW = "ar_KW"
    ARABIC_BH = "ar_BH"
    ARABIC_QA = "ar_QA"
    ARABIC_OM = "ar_OM"
    ARABIC_YE = "ar_YE"
    ARABIC_PS = "ar_PS"
    ARABIC_LY = "ar_LY"
    ARABIC_SD = "ar_SD"
    ARABIC_MR = "ar_MR"
    ARABIC_DJ_AR = "ar_DJ"
    ARABIC_SO_AR = "ar_SO"
    ARABIC_TD_AR = "ar_TD"
    ARABIC_KM_AR = "ar_KM"
    
    # Additional Important Languages for Global Coverage
    TWICHLE = "twi"                    # Twi (Ghana)
    EWE = "ee"                         # Ewe (Ghana, Togo)
    FANTE = "fat"                      # Fante (Ghana)
    DAGBANI = "dag"                    # Dagbani (Ghana)
    AKAN = "ak"                        # Akan (Ghana)
    MOSSI = "mos"                      # Mossi (Burkina Faso)
    DIOULA = "dyu"                     # Dioula (Burkina Faso, Mali)
    SANGO = "sg"                       # Sango (Central African Republic)
    TSHILUBA = "lua"                   # Tshiluba (Democratic Republic of Congo)
    CHILUBA = "luba"                   # Chiluba (Zambia)
    BEMBA = "bem"                      # Bemba (Zambia)
    NYANJA = "ny"                      # Nyanja/Chichewa (Malawi, Zambia)
    YAO = "yao"                        # Yao (Malawi, Tanzania)
    MAKONDE = "kde"                    # Makonde (Tanzania, Mozambique)
    CHOPE = "cce"                      # Chope (Mozambique)
    TSONGA_MZ = "ts_MZ"               # Tsonga (Mozambique)
    VENDA_ZA = "ve_ZA"                # Venda (South Africa)
    NORTHERN_SOTHO = "nso"            # Northern Sotho/Pedi (South Africa)
    SOUTHERN_NDEBELE = "nr"           # Southern Ndebele (South Africa)
    
    # Additional Indigenous Languages - Americas
    MAYA_YUC = "yua"                   # Yucatec Maya (Mexico)
    MAYA_KAQ = "caq"                   # Kaqchikel Maya (Guatemala)
    MAYA_MAM = "mam"                   # Mam Maya (Guatemala)
    GUARANI_PY = "gn_PY"              # Guarani (Paraguay)
    GUARANI_AR = "gn_AR"              # Guarani (Argentina)
    MAPUDUNGUN = "arn"                 # Mapudungun (Chile, Argentina)
    WAYUU = "guc"                      # Wayuu (Colombia, Venezuela)
    EMBERA = "emp"                     # Embera (Colombia, Panama)
    KUNA = "cuk"                       # Kuna (Panama)
    MISKITO = "miq"                    # Miskito (Nicaragua, Honduras)
    GARIFUNA = "cab"                   # Garifuna (Honduras, Belize, Guatemala)
    
    # Additional Indigenous Languages - North America
    NAVAJO = "nv"                      # Navajo (USA)
    CHEROKEE = "chr"                   # Cherokee (USA)
    OJIBWE = "oj"                      # Ojibwe (USA, Canada)
    CREE = "cr"                        # Cree (Canada)
    INUKTITUT = "iu"                   # Inuktitut (Canada)
    MOHAWK = "moh"                     # Mohawk (USA, Canada)
    LAKOTA = "lkt"                     # Lakota (USA)
    DAKOTA = "dak"                     # Dakota (USA)
    
    # Additional African Languages
    SHONA_ZW = "sn_ZW"                # Shona (Zimbabwe)
    NDEBELE_ZW = "nd_ZW"              # Ndebele (Zimbabwe)
    TONGA_ZM = "to_ZM"                # Tonga (Zambia)
    LOZI = "loz"                       # Lozi (Zambia)
    KIKONGO = "kg"                     # Kikongo (DRC, Angola)
    LINGALA = "ln"                     # Lingala (DRC, Congo)
    TEKE = "tek"                       # Teke (Congo)
    FANG = "fan"                       # Fang (Equatorial Guinea, Gabon)
    BULU = "bum"                       # Bulu (Cameroon)
    DOUALA = "dua"                     # Douala (Cameroon)
    FULFULDE = "ff"                    # Fulfulde (West Africa)
    KANURI = "kr"                      # Kanuri (Nigeria, Chad)
    
    # Additional Asian Regional Languages
    UYGHUR = "ug"                      # Uyghur (China)
    TIBETAN = "bo"                     # Tibetan (China, Tibet)
    MONGOLIAN = "mn"                   # Mongolian (Mongolia, China)
    BURYAT = "bua"                     # Buryat (Russia, Mongolia)
    YAKUT = "sah"                      # Yakut/Sakha (Russia)
    CHUKCHI = "ckt"                    # Chukchi (Russia)
    EVENK = "evn"                      # Evenk (Russia, China)
    MANCHU = "mnc"                     # Manchu (China)
    
    # Additional Pacific Languages
    MAORI = "mi"                       # Maori (New Zealand)
    FIJIAN = "fj"                      # Fijian (Fiji)
    TONGAN = "to"                      # Tongan (Tonga)
    SAMOAN = "sm"                      # Samoan (Samoa)
    TAHITIAN = "ty"                    # Tahitian (French Polynesia)
    MARSHALLESE = "mh"                 # Marshallese (Marshall Islands)
    PALAUAN = "pau"                    # Palauan (Palau)
    YAPESE = "yap"                     # Yapese (Micronesia)
    CHUUKESE = "chk"                   # Chuukese (Micronesia)
    
    # Additional European Regional Languages
    CATALAN_ES = "ca_ES"              # Catalan (Spain)
    CATALAN_AD = "ca_AD"              # Catalan (Andorra)
    BASQUE_ES = "eu_ES"               # Basque (Spain)
    BASQUE_FR = "eu_FR"               # Basque (France)
    GALICIAN = "gl"                    # Galician (Spain)
    ARANESE = "oc_ES"                  # Aranese (Spain)
    MIRANDESE = "mwl"                  # Mirandese (Portugal)
    LEONESE = "roa_leo"                # Leonese (Spain)
    ARAGONESE = "an"                   # Aragonese (Spain)
    ASTURIAN = "ast"                   # Asturian (Spain)
    EXTREMADURAN = "ext"               # Extremaduran (Spain)
    
    # Middle Eastern Regional Dialects
    KURDISH_KURMANJI = "ku_latn"       # Kurdish Kurmanji (Latin script)
    KURDISH_SORANI = "ku_arab"         # Kurdish Sorani (Arabic script)
    ASSYRIAN_NEO = "aii"               # Neo-Assyrian
    ARAMAIC = "arc"                    # Aramaic
    MALTESE = "mt"                     # Maltese
    SISWATI = "ss"                    # Siswati (Eswatini, South Africa)
    
    # Additional Asian Languages
    SHAN = "shn"                      # Shan (Myanmar)
    KAREN = "kar"                     # Karen (Myanmar)
    KACHIN = "kac"                    # Kachin (Myanmar)
    MON = "mnw"                       # Mon (Myanmar)
    ROHINGYA = "rhg"                  # Rohingya (Myanmar, Bangladesh)
    CHAKMA = "ccp"                    # Chakma (Bangladesh)
    MIZO = "lus"                      # Mizo (India)
    GARO = "grt"                      # Garo (India)
    TRIPURI = "trp"                   # Tripuri (India)
    BODO_IN = "brx_IN"                # Bodo (India)
    KHASI = "kha"                     # Khasi (India)
    NAGA = "nag"                      # Naga (India)
    
    # Additional European Minority Languages
    KASHUBIAN = "csb"                 # Kashubian (Poland)
    SILESIAN = "szl"                  # Silesian (Poland)
    RUSYN = "rue"                     # Rusyn (Ukraine, Slovakia)
    AROMANIAN = "rup"                 # Aromanian (Balkans)
    MEGLENO_ROMANIAN = "ruq"          # Megleno-Romanian (Balkans)
    ISTRO_ROMANIAN = "ruo"            # Istro-Romanian (Croatia)
    VLACH = "vlh"                     # Vlach (Serbia)
    BUNJEVAC = "bua"                  # Bunjevac (Serbia)
    BANAT_BULGARIAN = "bgx"           # Banat Bulgarian (Serbia)
    VOJVODINA_RUSYN = "rsk"           # Vojvodina Rusyn (Serbia)
    
    # Pacific Islander Languages Extended
    CHAMORRO = "ch"                   # Chamorro (Guam)
    CAROLINIAN = "cal"                # Carolinian (Northern Mariana Islands)
    MARSHALLESE = "mh"                # Marshallese (Marshall Islands)
    CHUUKESE = "chk"                  # Chuukese (Micronesia)
    POHNPEIAN = "pon"                 # Pohnpeian (Micronesia)
    YAPESE = "yap"                    # Yapese (Micronesia)
    KOSRAEAN = "kos"                  # Kosraean (Micronesia)
    PALAUAN = "pau"                   # Palauan (Palau)
    I_KIRIBATI = "gil"                # I-Kiribati (Kiribati)
    TUVALUAN = "tvl"                  # Tuvaluan (Tuvalu)
    NAURU = "na"                      # Nauru (Nauru)
    
    # Additional Indigenous Languages
    INUKTITUT = "iu"                  # Inuktitut (Canada)
    GREENLANDIC = "kl"                # Greenlandic (Greenland)
    SAMI_NORTHERN = "se"              # Northern Sami (Norway, Sweden, Finland)
    SAMI_SOUTHERN = "sma"             # Southern Sami (Norway, Sweden)
    SAMI_LULE = "smj"                 # Lule Sami (Norway, Sweden)
    SAMI_INARI = "smn"                # Inari Sami (Finland)
    SAMI_SKOLT = "sms"                # Skolt Sami (Finland)
    
    # Additional African Languages
    FULFULDE = "ff"                   # Fulfulde (West Africa)
    MANDINKA = "mnk"                  # Mandinka (West Africa)
    SONINKE = "snk"                   # Soninke (West Africa)
    TEMNE = "tem"                     # Temne (Sierra Leone)
    MENDE = "men"                     # Mende (Sierra Leone)
    KRU = "kru"                       # Kru (Liberia)
    BASSA = "bsq"                     # Bassa (Liberia)
    GBE = "gbe"                       # Gbe (Benin, Togo)
    KANURI = "kr"                     # Kanuri (Nigeria, Niger, Chad)
    TIV = "tiv"                       # Tiv (Nigeria)
    EFIK = "efi"                      # Efik (Nigeria)
    IBIBIO = "ibb"                    # Ibibio (Nigeria)
    
    # Additional Middle Eastern Dialects
    LEVANTINE_ARABIC = "apc"          # Levantine Arabic (Lebanon, Syria, Palestine, Jordan)
    EGYPTIAN_ARABIC = "arz"           # Egyptian Arabic (Egypt)
    GULF_ARABIC = "afb"               # Gulf Arabic (UAE, Kuwait, Bahrain, Qatar)
    MAGHREBI_ARABIC = "ary"           # Maghrebi Arabic (Morocco, Algeria, Tunisia)
    MESOPOTAMIAN_ARABIC = "acm"       # Mesopotamian Arabic (Iraq)
    NAJDI_ARABIC = "ars"              # Najdi Arabic (Saudi Arabia)
    HIJAZI_ARABIC = "acw"             # Hijazi Arabic (Saudi Arabia)
    YEMENI_ARABIC = "ayh"             # Yemeni Arabic (Yemen)
    SUDANESE_ARABIC = "apd"           # Sudanese Arabic (Sudan)
    CHADIAN_ARABIC = "shu"            # Chadian Arabic (Chad)
    
    # Amazigh/Berber Languages - Indigenous North African Languages
    AMAZIGH = "ber"                   # Amazigh/Berber (General)
    TAMAZIGHT = "tzm"                 # Central Atlas Tamazight (Morocco)
    TARIFIT = "rif"                   # Tarifit/Riffian (Northern Morocco)
    TASHELHIT = "shi"                 # Tashelhit/Souss (Southern Morocco)
    TAMAZIGHT_MOROCCO = "zgh"         # Standard Moroccan Amazigh
    KABYLE = "kab"                    # Kabyle (Algeria)
    CHAOUIA = "shy"                   # Chaouia/Shawiya (Algeria)
    MOZABITE = "mzb"                  # Mozabite/Tumzabt (Algeria)
    CHENOUA = "cnu"                   # Chenoua (Algeria)
    TAGARGRENT = "oua"                # Tagargrent/Ouargli (Algeria)
    TAMAHAQ = "thv"                   # Tamahaq/Tuareg (Niger, Mali)
    TAWALLAMMAT = "ttq"               # Tawallammat Tamajaq (Niger)
    TAYART = "thz"                    # Tayart Tamajeq (Niger)
    TAMASHEQ = "taq"                  # Tamasheq (Mali)
    TAMASHEK = "tmh"                  # Tamashek/Tuareg (Burkina Faso, Mali)
    NAFUSI = "jbn"                    # Nafusi (Libya)
    SIWI = "siz"                      # Siwi (Egypt)
    ZENAGA = "zen"                    # Zenaga (Mauritania)
    TETSERRET = "tez"                 # Tetserret (Niger)
    TUAREG_AHAGGAR = "ahg"            # Tuareg Ahaggar (Algeria)
    TUAREG_AIR = "air"                # Tuareg Air (Niger)
    GHADAMES = "gha"                  # Ghadames (Libya)
    AWJILA = "auj"                    # Awjila (Libya)
    SOKNA = "swn"                     # Sokna (Libya)
    FOQAHA = "fqh"                    # El Foqaha (Libya)
    
    # Additional North African Dialectal Variations
    MOROCCAN_DARIJA = "ary_MA"        # Moroccan Arabic Darija
    ALGERIAN_DARIJA = "arq"           # Algerian Arabic Darija
    TUNISIAN_DARIJA = "aeb"           # Tunisian Arabic Darija
    LIBYAN_ARABIC = "ayl"             # Libyan Arabic
    HASSANIYA = "mey"                 # Hassaniya Arabic (Mauritania, Western Sahara)
    MALTESE_ARABIC = "mt_AR"          # Maltese Arabic influence
    ANDALUSI_ARABIC = "xaa"           # Andalusi Arabic (Historical)
    JUDEO_ARABIC_MOROCCO = "aju_MA"   # Judeo-Arabic Morocco
    JUDEO_ARABIC_ALGERIA = "aju_DZ"   # Judeo-Arabic Algeria
    JUDEO_ARABIC_TUNISIA = "aju_TN"   # Judeo-Arabic Tunisia
    JUDEO_ARABIC_LIBYA = "aju_LY"     # Judeo-Arabic Libya
    
    # Saharan and Sub-Saharan Bridge Languages
    SONGHAI = "son"                   # Songhai (Mali, Niger)
    ZARMA = "dje"                     # Zarma (Niger)
    KANURI_CHAD = "kr_TD"             # Kanuri (Chad)
    KANURI_NIGER = "kr_NE"            # Kanuri (Niger)
    TEDAGA = "tuq"                    # Tedaga (Chad)
    DAZA = "dzg"                      # Daza (Chad, Niger)
    BERIA = "byn"                     # Beria/Zaghawa (Chad, Sudan)
    MASALIT = "mls"                   # Masalit (Chad, Sudan)
    FUR = "fvr"                       # Fur (Sudan)
    NUBA_LANGUAGES = "nub"            # Nuba Mountain Languages (Sudan)
    BEJA = "bej"                      # Beja (Sudan, Egypt, Eritrea)
    NUBIAN = "nub"                    # Nubian Languages (Sudan, Egypt)
    DONGOLAWI = "kzh"                 # Dongolawi Nubian (Sudan)
    KENZI = "xnz"                     # Kenzi Nubian (Egypt, Sudan)
    FADICCA = "fdi"                   # Fadicca Nubian (Sudan)
    NOBIIN = "fia"                    # Nobiin Nubian (Egypt, Sudan)
    
    # Additional Critical Languages for Worldwide Coverage
    
    # Sign Languages (Critical for accessibility)
    AMERICAN_SIGN_LANGUAGE = "ase"    # American Sign Language (USA, Canada)
    BRITISH_SIGN_LANGUAGE = "bfi"     # British Sign Language (UK)
    FRENCH_SIGN_LANGUAGE = "fsl"      # French Sign Language (France)
    GERMAN_SIGN_LANGUAGE = "gsg"      # German Sign Language (Germany)
    JAPANESE_SIGN_LANGUAGE = "jsl"    # Japanese Sign Language (Japan)
    CHINESE_SIGN_LANGUAGE = "csl"     # Chinese Sign Language (China)
    INTERNATIONAL_SIGN = "ils"        # International Sign
    
    # Central Asian Languages (Major Gap)
    KAZAKH = "kk"                     # Kazakh (Kazakhstan, China)
    KYRGYZ = "ky"                     # Kyrgyz (Kyrgyzstan)
    UZBEK = "uz"                      # Uzbek (Uzbekistan)
    UZBEK_LATIN = "uz_Latn"          # Uzbek Latin script
    UZBEK_CYRILLIC = "uz_Cyrl"       # Uzbek Cyrillic script
    TURKMEN = "tk"                    # Turkmen (Turkmenistan)
    TAJIK = "tg"                      # Tajik (Tajikistan)
    TAJIK_CYRILLIC = "tg_Cyrl"       # Tajik Cyrillic script
    TAJIK_PERSIAN = "tg_Arab"         # Tajik Persian script
    
    # Additional African Languages (Major Coverage Gap)
    AMHARIC_ET = "am_ET"              # Amharic (Ethiopia)
    OROMO = "om"                      # Oromo (Ethiopia)
    TIGRINYA = "ti"                   # Tigrinya (Ethiopia, Eritrea)
    SIDAMO = "sid"                    # Sidamo (Ethiopia)
    WOLAYTA = "wal"                   # Wolayta (Ethiopia)
    KAMBA = "kam"                     # Kamba (Kenya)
    LUO_KE = "luo"                    # Luo (Kenya)
    KALENJIN = "kln"                  # Kalenjin (Kenya)
    MERU = "mer"                      # Meru (Kenya)
    EMBU = "ebu"                      # Embu (Kenya)
    GUSII = "guz"                     # Gusii (Kenya)
    TESO = "teo"                      # Teso (Uganda, Kenya)
    LUGANDA = "lg"                    # Luganda (Uganda)
    RUNYANKORE = "nyn"                # Runyankore (Uganda)
    KINYARWANDA = "rw"                # Kinyarwanda (Rwanda)
    KIRUNDI = "rn"                    # Kirundi (Burundi)
    TONGA_ZM = "to_ZM"                # Tonga (Zambia)
    NYANJA = "ny"                     # Nyanja/Chichewa (Malawi)
    YAO_MW = "yao"                    # Yao (Malawi)
    MALAGASY = "mg"                   # Malagasy (Madagascar)
    
    # Additional Pacific Languages
    PAPUA_NEW_GUINEA_PIDGIN = "tpi"   # Tok Pisin (Papua New Guinea)
    HIRI_MOTU = "ho"                  # Hiri Motu (Papua New Guinea)
    SOLOMON_ISLANDS_PIDGIN = "pis"    # Solomon Islands Pidgin
    BISLAMA = "bi"                    # Bislama (Vanuatu)
    COOK_ISLANDS_MAORI = "rar"        # Cook Islands Maori
    NIUEAN = "niu"                    # Niuean (Niue)
    TOKELAUAN = "tkl"                 # Tokelauan (Tokelau)
    
    # Additional European Regional Languages
    ROMANSH = "rm"                    # Romansh (Switzerland)
    LADIN = "lld"                     # Ladin (Italy)
    FRIULIAN = "fur"                  # Friulian (Italy)
    SARDINIAN = "sc"                  # Sardinian (Italy)
    CORSICAN = "co"                   # Corsican (France)
    OCCITAN = "oc"                    # Occitan (France)
    FRANCO_PROVENCAL = "frp"          # Franco-Provençal (France, Switzerland)
    WALLOON = "wa"                    # Walloon (Belgium)
    LOWER_SORBIAN = "dsb"             # Lower Sorbian (Germany)
    UPPER_SORBIAN = "hsb"             # Upper Sorbian (Germany)
    
    # Additional Middle Eastern Languages
    SORANI_KURDISH = "ckb"            # Sorani Kurdish (Iraq, Iran)
    KURMANJI_KURDISH = "ku"           # Kurmanji Kurdish (Turkey, Syria)
    ZAZAKI = "zza"                    # Zazaki (Turkey)
    LUR = "lrc"                       # Lur (Iran)
    GILAKI = "glk"                    # Gilaki (Iran)
    MAZANDARANI = "mzn"               # Mazandarani (Iran)
    BALOCHI = "bal"                   # Balochi (Pakistan, Iran, Afghanistan)
    BRAHUI = "brh"                    # Brahui (Pakistan)
    
    # Additional South American Indigenous Languages
    AYMARA = "ay"                     # Aymara (Bolivia, Peru)
    TZELTAL = "tzh"                   # Tzeltal (Mexico)
    TZOTZIL = "tzo"                   # Tzotzil (Mexico)
    CHOL = "ctu"                      # Ch'ol (Mexico)
    MIXTEC = "mix"                    # Mixtec (Mexico)
    ZAPOTEC = "zap"                   # Zapotec (Mexico)
    OTOMI = "oto"                     # Otomi (Mexico)
    HUICHOL = "hch"                   # Huichol (Mexico)
    
    # Additional Critical Missing Languages for Complete Worldwide Coverage
    FARSI = "fa"                      # Persian/Farsi (Iran, Afghanistan, Tajikistan)
    FARSI_IR = "fa_IR"                # Persian (Iran)
    FARSI_AF = "fa_AF"                # Dari Persian (Afghanistan)
    FARSI_TJ = "fa_TJ"                # Tajik Persian (Tajikistan)
    MAPUCHE = "arn"                   # Mapuche (Chile, Argentina)
    
    # Additional Regional Dialects and Indigenous Languages
    QUECHUA_BOLIVIA = "qu_BO"         # Quechua (Bolivia)
    QUECHUA_ECUADOR = "qu_EC"         # Quechua (Ecuador)
    QUECHUA_PERU = "qu_PE"            # Quechua (Peru)
    GUARANI_PY = "gn_PY"              # Guarani (Paraguay)
    GUARANI_BO = "gn_BO"              # Guarani (Bolivia)
    NAVAJO = "nv"                     # Navajo/Diné (USA)
    CHEROKEE = "chr"                  # Cherokee (USA)
    CREE = "cr"                       # Cree (Canada)
    INUKTITUT = "iu"                  # Inuktitut (Canada)
    OJIBWE = "oj"                     # Ojibwe (USA, Canada)
    
    # Additional African Languages for Comprehensive Coverage
    FULANI = "ff"                     # Fulani/Fula (West Africa)
    FULANI_SN = "ff_SN"               # Fulani (Senegal)
    FULANI_GN = "ff_GN"               # Fulani (Guinea)
    FULANI_ML = "ff_ML"               # Fulani (Mali)
    FULANI_BF = "ff_BF"               # Fulani (Burkina Faso)
    BAMBARA = "bm"                    # Bambara (Mali)
    SANGO = "sg"                      # Sango (Central African Republic)
    LINGALA = "ln"                    # Lingala (DRC, Congo)
    KIKONGO = "kg"                    # Kikongo (DRC, Congo, Angola)
    SHONA = "sn"                      # Shona (Zimbabwe)
    NDEBELE = "nd"                    # Ndebele (Zimbabwe, South Africa)
    TSWANA = "tn"                     # Tswana (Botswana, South Africa)
    SEPEDI = "nso"                    # Sepedi/Northern Sotho (South Africa)
    VENDA = "ve"                      # Venda (South Africa)
    TSONGA = "ts"                     # Tsonga (South Africa, Mozambique)
    
    # Additional Asian Languages and Dialects
    SINDHI = "sd"                     # Sindhi (Pakistan, India)
    NEPALI = "ne"                     # Nepali (Nepal)
    SINHALA = "si"                    # Sinhala (Sri Lanka)
    DZONGKHA = "dz"                   # Dzongkha (Bhutan)
    BURMESE = "my"                    # Burmese (Myanmar)
    KHMER = "km"                      # Khmer (Cambodia)
    LAO = "lo"                        # Lao (Laos)
    MONGOLIAN_MN = "mn_MN"            # Mongolian (Mongolia)
    MONGOLIAN_CN = "mn_CN"            # Mongolian (China/Inner Mongolia)
    
    # Additional Pacific Island Languages
    FIJIAN = "fj"                     # Fijian (Fiji)
    MARSHALLESE = "mh"                # Marshallese (Marshall Islands)
    PALAUAN = "pau"                   # Palauan (Palau)
    CHUUKESE = "chk"                  # Chuukese (Micronesia)
    YAPESE = "yap"                    # Yapese (Micronesia)
    KOSRAEAN = "kos"                  # Kosraean (Micronesia)
    POHNPEIAN = "pon"                 # Pohnpeian (Micronesia)
    
    # Additional European Regional Languages and Dialects
    BASQUE = "eu"                     # Basque (Spain, France)
    WELSH = "cy"                      # Welsh (Wales)
    IRISH = "ga"                      # Irish Gaelic (Ireland)
    SCOTTISH_GAELIC = "gd"            # Scottish Gaelic (Scotland)
    MANX = "gv"                       # Manx (Isle of Man)
    CORNISH = "kw"                    # Cornish (Cornwall)
    BRETON = "br"                     # Breton (Brittany, France)
    ALSATIAN = "gsw"                  # Alsatian (France)
    LUXEMBOURGISH = "lb"              # Luxembourgish (Luxembourg)
    RUSYN = "rue"                     # Rusyn (Ukraine, Slovakia, Poland)
    KASHUBIAN = "csb"                 # Kashubian (Poland)
    
    # Additional Middle Eastern Languages
    ARAMAIC = "arc"                   # Aramaic (Syria, Iraq)
    ASSYRIAN = "aii"                  # Assyrian Neo-Aramaic (Iraq, Syria)
    SYRIAC = "syc"                    # Syriac (Syria, Iraq)
    COPTIC = "cop"                    # Coptic (Egypt)
    
    # Additional Sign Languages for Complete Accessibility
    SPANISH_SIGN_LANGUAGE = "ssp"     # Spanish Sign Language
    ITALIAN_SIGN_LANGUAGE = "ise"     # Italian Sign Language
    RUSSIAN_SIGN_LANGUAGE = "rsl"     # Russian Sign Language
    INDIAN_SIGN_LANGUAGE = "ins"      # Indian Sign Language
    BRAZILIAN_SIGN_LANGUAGE = "bzs"   # Brazilian Sign Language (Libras)
    MEXICAN_SIGN_LANGUAGE = "mfs"     # Mexican Sign Language
    ARGENTINE_SIGN_LANGUAGE = "aed"   # Argentine Sign Language

    @staticmethod
    def get_language_family(language: 'SupportedLanguage') -> str:
        """Get language family for the given language"""
        language_families = {
            # Indo-European Family
            "indo_european_germanic": [
                SupportedLanguage.ENGLISH, SupportedLanguage.ENGLISH_US, SupportedLanguage.ENGLISH_UK,
                SupportedLanguage.ENGLISH_AU, SupportedLanguage.ENGLISH_CA, SupportedLanguage.ENGLISH_IN,
                SupportedLanguage.ENGLISH_ZA, SupportedLanguage.ENGLISH_NZ, SupportedLanguage.ENGLISH_IE,
                SupportedLanguage.ENGLISH_SG, SupportedLanguage.ENGLISH_PH, SupportedLanguage.ENGLISH_MY,
                SupportedLanguage.ENGLISH_HK, SupportedLanguage.GERMAN, SupportedLanguage.GERMAN_DE,
                SupportedLanguage.GERMAN_AT, SupportedLanguage.GERMAN_CH, SupportedLanguage.DUTCH,
                SupportedLanguage.DUTCH_NL, SupportedLanguage.DUTCH_BE, SupportedLanguage.FLEMISH,
                SupportedLanguage.SWEDISH, SupportedLanguage.SWEDISH_SE, SupportedLanguage.SWEDISH_FI,
                SupportedLanguage.NORWEGIAN, SupportedLanguage.NORWEGIAN_BOKMAL, SupportedLanguage.NORWEGIAN_NYNORSK,
                SupportedLanguage.DANISH, SupportedLanguage.ICELANDIC, SupportedLanguage.FAROESE,
                SupportedLanguage.FRISIAN, SupportedLanguage.LUXEMBOURGISH, SupportedLanguage.AFRIKAANS
            ],
            "indo_european_romance": [
                SupportedLanguage.SPANISH, SupportedLanguage.SPANISH_ES, SupportedLanguage.SPANISH_MX,
                SupportedLanguage.SPANISH_AR, SupportedLanguage.SPANISH_CO, SupportedLanguage.SPANISH_CL,
                SupportedLanguage.SPANISH_PE, SupportedLanguage.SPANISH_VE, SupportedLanguage.SPANISH_US,
                SupportedLanguage.SPANISH_EC, SupportedLanguage.SPANISH_BO, SupportedLanguage.SPANISH_PY,
                SupportedLanguage.SPANISH_UY, SupportedLanguage.SPANISH_CR, SupportedLanguage.SPANISH_PA,
                SupportedLanguage.SPANISH_GT, SupportedLanguage.SPANISH_HN, SupportedLanguage.SPANISH_SV,
                SupportedLanguage.SPANISH_NI, SupportedLanguage.SPANISH_DO, SupportedLanguage.SPANISH_CU,
                SupportedLanguage.SPANISH_PR, SupportedLanguage.FRENCH, SupportedLanguage.FRENCH_FR,
                SupportedLanguage.FRENCH_CA, SupportedLanguage.FRENCH_BE, SupportedLanguage.FRENCH_CH,
                SupportedLanguage.FRENCH_SENEGAL, SupportedLanguage.FRENCH_MOROCCO, SupportedLanguage.FRENCH_LU,
                SupportedLanguage.FRENCH_MC, SupportedLanguage.FRENCH_CI, SupportedLanguage.FRENCH_ML,
                SupportedLanguage.FRENCH_BF, SupportedLanguage.FRENCH_NE, SupportedLanguage.FRENCH_TD,
                SupportedLanguage.FRENCH_CF, SupportedLanguage.FRENCH_CG, SupportedLanguage.FRENCH_CD,
                SupportedLanguage.FRENCH_DJ, SupportedLanguage.FRENCH_KM, SupportedLanguage.FRENCH_MG,
                SupportedLanguage.FRENCH_SC, SupportedLanguage.FRENCH_VU, SupportedLanguage.FRENCH_NC,
                SupportedLanguage.FRENCH_PF, SupportedLanguage.ITALIAN, SupportedLanguage.ITALIAN_IT,
                SupportedLanguage.ITALIAN_CH, SupportedLanguage.PORTUGUESE, SupportedLanguage.PORTUGUESE_PT,
                SupportedLanguage.PORTUGUESE_BR, SupportedLanguage.PORTUGUESE_AO, SupportedLanguage.PORTUGUESE_MZ,
                SupportedLanguage.PORTUGUESE_CV, SupportedLanguage.PORTUGUESE_GW, SupportedLanguage.PORTUGUESE_ST,
                SupportedLanguage.PORTUGUESE_TL, SupportedLanguage.PORTUGUESE_MO, SupportedLanguage.ROMANIAN,
                SupportedLanguage.CATALAN, SupportedLanguage.GALICIAN, SupportedLanguage.CORSICAN,
                SupportedLanguage.SARDINIAN, SupportedLanguage.NEAPOLITAN, SupportedLanguage.VENETIAN,
                SupportedLanguage.LOMBARD, SupportedLanguage.PIEDMONTESE, SupportedLanguage.OCCITAN,
                SupportedLanguage.ARAGONESE, SupportedLanguage.ASTURIAN, SupportedLanguage.MIRANDESE,
                SupportedLanguage.ROMANSH, SupportedLanguage.LADIN
            ],
            "indo_european_slavic": [
                SupportedLanguage.RUSSIAN, SupportedLanguage.RUSSIAN_RU, SupportedLanguage.RUSSIAN_BY,
                SupportedLanguage.RUSSIAN_KZ, SupportedLanguage.POLISH, SupportedLanguage.CZECH,
                SupportedLanguage.SLOVAK, SupportedLanguage.UKRAINIAN, SupportedLanguage.BULGARIAN,
                SupportedLanguage.CROATIAN, SupportedLanguage.SERBIAN, SupportedLanguage.SERBIAN_CYRILLIC,
                SupportedLanguage.SERBIAN_LATIN, SupportedLanguage.SLOVENIAN, SupportedLanguage.BOSNIAN,
                SupportedLanguage.MONTENEGRIN, SupportedLanguage.MACEDONIAN
            ],
            "indo_european_baltic": [
                SupportedLanguage.LITHUANIAN, SupportedLanguage.LATVIAN
            ],
            "indo_european_celtic": [
                SupportedLanguage.IRISH, SupportedLanguage.WELSH, SupportedLanguage.SCOTTISH_GAELIC,
                SupportedLanguage.BRETON
            ],
            "indo_european_indic": [
                SupportedLanguage.HINDI, SupportedLanguage.HINDI_IN, SupportedLanguage.BENGALI,
                SupportedLanguage.BENGALI_BD, SupportedLanguage.BENGALI_IN, SupportedLanguage.TAMIL,
                SupportedLanguage.TAMIL_IN, SupportedLanguage.TAMIL_LK, SupportedLanguage.TAMIL_SG,
                SupportedLanguage.TELUGU, SupportedLanguage.MARATHI, SupportedLanguage.GUJARATI,
                SupportedLanguage.PUNJABI, SupportedLanguage.PUNJABI_IN, SupportedLanguage.PUNJABI_PK,
                SupportedLanguage.URDU, SupportedLanguage.URDU_PK, SupportedLanguage.URDU_IN,
                SupportedLanguage.SINDHI, SupportedLanguage.NEPALI, SupportedLanguage.SINHALA,
                SupportedLanguage.ASSAMESE, SupportedLanguage.ORIYA, SupportedLanguage.KANNADA,
                SupportedLanguage.MALAYALAM, SupportedLanguage.KONKANI, SupportedLanguage.MANIPURI,
                SupportedLanguage.KASHMIRI, SupportedLanguage.SANSKRIT, SupportedLanguage.BODO,
                SupportedLanguage.SANTALI, SupportedLanguage.MAITHILI, SupportedLanguage.DOGRI
            ],
            "indo_european_iranian": [
                SupportedLanguage.PERSIAN, SupportedLanguage.PERSIAN_IR, SupportedLanguage.PERSIAN_AF,
                SupportedLanguage.DARI, SupportedLanguage.PASHTO, SupportedLanguage.KURDISH, SupportedLanguage.TAJIK
            ],
            "indo_european_armenian": [
                SupportedLanguage.ARMENIAN
            ],
            "indo_european_greek": [
                SupportedLanguage.GREEK, SupportedLanguage.ANCIENT_GREEK
            ],
            "indo_european_albanian": [
                SupportedLanguage.ALBANIAN
            ],
            
            # Sino-Tibetan Family
            "sino_tibetan_chinese": [
                SupportedLanguage.CHINESE_SIMPLIFIED, SupportedLanguage.CHINESE_TRADITIONAL,
                SupportedLanguage.CHINESE_HK, SupportedLanguage.CHINESE_SG, SupportedLanguage.CANTONESE,
                SupportedLanguage.HAKKA, SupportedLanguage.MIN_NAN, SupportedLanguage.WU_CHINESE
            ],
            "sino_tibetan_tibetan": [
                SupportedLanguage.TIBETAN
            ],
            "sino_tibetan_burmese": [
                SupportedLanguage.BURMESE
            ],
            
            # Japonic Family
            "japonic": [
                SupportedLanguage.JAPANESE, SupportedLanguage.JAPANESE_KANSAI, SupportedLanguage.OKINAWAN
            ],
            
            # Koreanic Family
            "koreanic": [
                SupportedLanguage.KOREAN, SupportedLanguage.KOREAN_KR, SupportedLanguage.KOREAN_KP
            ],
            
            # Afroasiatic Family
            "afroasiatic_semitic": [
                SupportedLanguage.ARABIC, SupportedLanguage.ARABIC_SA, SupportedLanguage.ARABIC_EG,
                SupportedLanguage.ARABIC_AE, SupportedLanguage.ARABIC_MA, SupportedLanguage.ARABIC_TN,
                SupportedLanguage.ARABIC_DZ, SupportedLanguage.ARABIC_IQ, SupportedLanguage.ARABIC_JO,
                SupportedLanguage.ARABIC_LB, SupportedLanguage.ARABIC_SY, SupportedLanguage.ARABIC_KW,
                SupportedLanguage.ARABIC_BH, SupportedLanguage.ARABIC_QA, SupportedLanguage.ARABIC_OM,
                SupportedLanguage.ARABIC_YE, SupportedLanguage.ARABIC_PS, SupportedLanguage.ARABIC_LY,
                SupportedLanguage.ARABIC_SD, SupportedLanguage.ARABIC_MR, SupportedLanguage.ARABIC_DJ_AR,
                SupportedLanguage.ARABIC_SO_AR, SupportedLanguage.ARABIC_TD_AR, SupportedLanguage.ARABIC_KM_AR,
                SupportedLanguage.HEBREW, SupportedLanguage.HEBREW_IL, SupportedLanguage.ARAMAIC,
                SupportedLanguage.ASSYRIAN
            ],
            "afroasiatic_cushitic": [
                SupportedLanguage.AMHARIC, SupportedLanguage.TIGRINYA, SupportedLanguage.OROMO, SupportedLanguage.SOMALI
            ],
            "afroasiatic_coptic": [
                SupportedLanguage.COPTIC
            ],
            
            # Altaic Family (disputed)
            "altaic_turkic": [
                SupportedLanguage.TURKISH, SupportedLanguage.AZERBAIJANI, SupportedLanguage.AZERBAIJANI_CYRILLIC,
                SupportedLanguage.AZERBAIJANI_LATIN, SupportedLanguage.KAZAKH, SupportedLanguage.UZBEK,
                SupportedLanguage.UZBEK_CYRILLIC, SupportedLanguage.UZBEK_LATIN, SupportedLanguage.TURKMEN,
                SupportedLanguage.KYRGYZ
            ],
            "altaic_mongolic": [
                SupportedLanguage.MONGOLIAN
            ],
            
            # Uralic Family
            "uralic_finnic": [
                SupportedLanguage.FINNISH, SupportedLanguage.ESTONIAN
            ],
            "uralic_ugric": [
                SupportedLanguage.HUNGARIAN
            ],
            
            # Niger-Congo Family
            "niger_congo_bantu": [
                SupportedLanguage.SWAHILI, SupportedLanguage.SWAHILI_KE, SupportedLanguage.SWAHILI_TZ,
                SupportedLanguage.ZULU, SupportedLanguage.XHOSA, SupportedLanguage.SESOTHO,
                SupportedLanguage.SETSWANA, SupportedLanguage.SHONA, SupportedLanguage.NDEBELE,
                SupportedLanguage.VENDA, SupportedLanguage.TSONGA, SupportedLanguage.LINGALA,
                SupportedLanguage.KIKONGO, SupportedLanguage.LUGANDA, SupportedLanguage.KINYARWANDA,
                SupportedLanguage.KIRUNDI
            ],
            "niger_congo_west_african": [
                SupportedLanguage.YORUBA, SupportedLanguage.IGBO, SupportedLanguage.HAUSA,
                SupportedLanguage.FULANI, SupportedLanguage.WOLOF, SupportedLanguage.BAMBARA
            ],
            
            # Austronesian Family
            "austronesian_malayo_polynesian": [
                SupportedLanguage.INDONESIAN, SupportedLanguage.MALAY, SupportedLanguage.MALAY_MY,
                SupportedLanguage.MALAY_BN, SupportedLanguage.FILIPINO, SupportedLanguage.TAGALOG,
                SupportedLanguage.CEBUANO, SupportedLanguage.ILOKANO, SupportedLanguage.HILIGAYNON,
                SupportedLanguage.WARAY, SupportedLanguage.BIKOL, SupportedLanguage.KAPAMPANGAN,
                SupportedLanguage.PANGASINAN, SupportedLanguage.MALAGASY
            ],
            "austronesian_polynesian": [
                SupportedLanguage.MAORI, SupportedLanguage.HAWAIIAN, SupportedLanguage.FIJIAN,
                SupportedLanguage.TONGAN, SupportedLanguage.SAMOAN, SupportedLanguage.TAHITIAN
            ],
            
            # Tai-Kadai Family
            "tai_kadai": [
                SupportedLanguage.THAI, SupportedLanguage.LAO
            ],
            
            # Austro-Asiatic Family
            "austro_asiatic": [
                SupportedLanguage.VIETNAMESE, SupportedLanguage.VIETNAMESE_VN, SupportedLanguage.KHMER
            ],
            
            # Kartvelian Family
            "kartvelian": [
                SupportedLanguage.GEORGIAN
            ],
            
            # Language Isolates
            "isolate": [
                SupportedLanguage.BASQUE, SupportedLanguage.MALTESE
            ],
            
            # American Indigenous
            "american_indigenous": [
                SupportedLanguage.NAVAJO, SupportedLanguage.CHEROKEE, SupportedLanguage.QUECHUA,
                SupportedLanguage.GUARANI, SupportedLanguage.AYMARA, SupportedLanguage.MAPUDUNGUN
            ],
            
            # Constructed Languages
            "constructed": [
                SupportedLanguage.ESPERANTO, SupportedLanguage.INTERLINGUA, SupportedLanguage.VOLAPUK,
                SupportedLanguage.IDO, SupportedLanguage.KLINGON
            ],
            
            # Historical Languages
            "historical": [
                SupportedLanguage.LATIN, SupportedLanguage.OLD_ENGLISH, SupportedLanguage.MIDDLE_ENGLISH,
                SupportedLanguage.OLD_NORSE, SupportedLanguage.GOTHIC
            ],
            
            # Sign Languages
            "sign_languages": [
                SupportedLanguage.AMERICAN_SIGN_LANGUAGE, SupportedLanguage.BRITISH_SIGN_LANGUAGE,
                SupportedLanguage.FRENCH_SIGN_LANGUAGE, SupportedLanguage.GERMAN_SIGN_LANGUAGE,
                SupportedLanguage.JAPANESE_SIGN_LANGUAGE
            ],
            
            # Afro-Asiatic Family
            "afro_asiatic_semitic": [
                SupportedLanguage.ARABIC, SupportedLanguage.ARABIC_SA, SupportedLanguage.ARABIC_EG,
                SupportedLanguage.ARABIC_AE, SupportedLanguage.ARABIC_MA, SupportedLanguage.ARABIC_TN,
                SupportedLanguage.ARABIC_DZ, SupportedLanguage.ARABIC_IQ, SupportedLanguage.ARABIC_JO,
                SupportedLanguage.ARABIC_LB, SupportedLanguage.ARABIC_SY, SupportedLanguage.HEBREW,
                SupportedLanguage.HEBREW_IL, SupportedLanguage.ARAMAIC, SupportedLanguage.ASSYRIAN,
                SupportedLanguage.LEVANTINE_ARABIC, SupportedLanguage.EGYPTIAN_ARABIC, SupportedLanguage.GULF_ARABIC,
                SupportedLanguage.MAGHREBI_ARABIC, SupportedLanguage.MESOPOTAMIAN_ARABIC, SupportedLanguage.NAJDI_ARABIC,
                SupportedLanguage.HIJAZI_ARABIC, SupportedLanguage.YEMENI_ARABIC, SupportedLanguage.SUDANESE_ARABIC,
                SupportedLanguage.CHADIAN_ARABIC, SupportedLanguage.MOROCCAN_DARIJA, SupportedLanguage.ALGERIAN_DARIJA,
                SupportedLanguage.TUNISIAN_DARIJA, SupportedLanguage.LIBYAN_ARABIC, SupportedLanguage.HASSANIYA
            ],
            "afro_asiatic_berber": [
                SupportedLanguage.AMAZIGH, SupportedLanguage.TAMAZIGHT, SupportedLanguage.TARIFIT,
                SupportedLanguage.TASHELHIT, SupportedLanguage.TAMAZIGHT_MOROCCO, SupportedLanguage.KABYLE,
                SupportedLanguage.CHAOUIA, SupportedLanguage.MOZABITE, SupportedLanguage.CHENOUA,
                SupportedLanguage.TAGARGRENT, SupportedLanguage.TAMAHAQ, SupportedLanguage.TAWALLAMMAT,
                SupportedLanguage.TAYART, SupportedLanguage.TAMASHEQ, SupportedLanguage.TAMASHEK,
                SupportedLanguage.NAFUSI, SupportedLanguage.SIWI, SupportedLanguage.ZENAGA,
                SupportedLanguage.TETSERRET, SupportedLanguage.TUAREG_AHAGGAR, SupportedLanguage.TUAREG_AIR,
                SupportedLanguage.GHADAMES, SupportedLanguage.AWJILA, SupportedLanguage.SOKNA,
                SupportedLanguage.FOQAHA
            ],
            "afro_asiatic_cushitic": [
                SupportedLanguage.AMHARIC, SupportedLanguage.TIGRINYA, SupportedLanguage.OROMO,
                SupportedLanguage.SOMALI, SupportedLanguage.BEJA
            ],
            "afro_asiatic_chadic": [
                SupportedLanguage.HAUSA, SupportedLanguage.KANURI, SupportedLanguage.KANURI_CHAD,
                SupportedLanguage.KANURI_NIGER
            ],
            "afro_asiatic_egyptian": [
                SupportedLanguage.COPTIC
            ],
            
            # Nilo-Saharan Family
            "nilo_saharan": [
                SupportedLanguage.SONGHAI, SupportedLanguage.ZARMA, SupportedLanguage.TEDAGA,
                SupportedLanguage.DAZA, SupportedLanguage.BERIA, SupportedLanguage.MASALIT,
                SupportedLanguage.FUR, SupportedLanguage.NUBIAN, SupportedLanguage.DONGOLAWI,
                SupportedLanguage.KENZI, SupportedLanguage.FADICCA, SupportedLanguage.NOBIIN
            ],
            
            # Other
            "dhivehi": [SupportedLanguage.DHIVEHI]
        }
        
        for family, languages in language_families.items():
            if language in languages:
                return family
        
        return "unknown"

    @staticmethod
    def get_language_script(language: 'SupportedLanguage') -> str:
        """Get the writing script for the given language"""
        scripts = {
            "latin": [
                SupportedLanguage.ENGLISH, SupportedLanguage.ENGLISH_US, SupportedLanguage.ENGLISH_UK,
                SupportedLanguage.ENGLISH_AU, SupportedLanguage.ENGLISH_CA, SupportedLanguage.ENGLISH_IN,
                SupportedLanguage.ENGLISH_ZA, SupportedLanguage.ENGLISH_NZ, SupportedLanguage.ENGLISH_IE,
                SupportedLanguage.ENGLISH_SG, SupportedLanguage.ENGLISH_PH, SupportedLanguage.ENGLISH_MY,
                SupportedLanguage.ENGLISH_HK, SupportedLanguage.SPANISH, SupportedLanguage.SPANISH_ES,
                SupportedLanguage.SPANISH_MX, SupportedLanguage.SPANISH_AR, SupportedLanguage.SPANISH_CO,
                SupportedLanguage.SPANISH_CL, SupportedLanguage.SPANISH_PE, SupportedLanguage.SPANISH_VE,
                SupportedLanguage.FRENCH, SupportedLanguage.FRENCH_FR, SupportedLanguage.FRENCH_CA,
                SupportedLanguage.FRENCH_BE, SupportedLanguage.FRENCH_CH, SupportedLanguage.GERMAN,
                SupportedLanguage.GERMAN_DE, SupportedLanguage.GERMAN_AT, SupportedLanguage.GERMAN_CH,
                SupportedLanguage.ITALIAN, SupportedLanguage.ITALIAN_IT, SupportedLanguage.ITALIAN_CH,
                SupportedLanguage.PORTUGUESE, SupportedLanguage.PORTUGUESE_PT, SupportedLanguage.PORTUGUESE_BR,
                SupportedLanguage.DUTCH, SupportedLanguage.POLISH, SupportedLanguage.SWEDISH,
                SupportedLanguage.NORWEGIAN, SupportedLanguage.DANISH, SupportedLanguage.FINNISH,
                SupportedLanguage.TURKISH, SupportedLanguage.CZECH, SupportedLanguage.HUNGARIAN,
                SupportedLanguage.ROMANIAN, SupportedLanguage.CROATIAN, SupportedLanguage.SLOVENIAN,
                SupportedLanguage.SLOVAK, SupportedLanguage.ESTONIAN, SupportedLanguage.LATVIAN,
                SupportedLanguage.LITHUANIAN, SupportedLanguage.VIETNAMESE, SupportedLanguage.INDONESIAN,
                SupportedLanguage.MALAY, SupportedLanguage.FILIPINO, SupportedLanguage.TAGALOG,
                SupportedLanguage.SWAHILI, SupportedLanguage.YORUBA, SupportedLanguage.IGBO,
                SupportedLanguage.HAUSA, SupportedLanguage.AFRIKAANS, SupportedLanguage.ZULU,
                SupportedLanguage.XHOSA, SupportedLanguage.ESPERANTO, SupportedLanguage.LATIN
            ],
            "cyrillic": [
                SupportedLanguage.RUSSIAN, SupportedLanguage.RUSSIAN_RU, SupportedLanguage.RUSSIAN_BY,
                SupportedLanguage.RUSSIAN_KZ, SupportedLanguage.BULGARIAN, SupportedLanguage.SERBIAN_CYRILLIC,
                SupportedLanguage.UKRAINIAN, SupportedLanguage.BOSNIAN, SupportedLanguage.MONTENEGRIN,
                SupportedLanguage.MACEDONIAN, SupportedLanguage.KAZAKH, SupportedLanguage.UZBEK_CYRILLIC,
                SupportedLanguage.KYRGYZ, SupportedLanguage.TAJIK, SupportedLanguage.AZERBAIJANI_CYRILLIC,
                SupportedLanguage.MONGOLIAN
            ],
            "arabic": [
                SupportedLanguage.ARABIC, SupportedLanguage.ARABIC_SA, SupportedLanguage.ARABIC_EG,
                SupportedLanguage.ARABIC_AE, SupportedLanguage.ARABIC_MA, SupportedLanguage.ARABIC_TN,
                SupportedLanguage.ARABIC_DZ, SupportedLanguage.ARABIC_IQ, SupportedLanguage.ARABIC_JO,
                SupportedLanguage.ARABIC_LB, SupportedLanguage.ARABIC_SY, SupportedLanguage.PERSIAN,
                SupportedLanguage.PERSIAN_IR, SupportedLanguage.PERSIAN_AF, SupportedLanguage.DARI,
                SupportedLanguage.PASHTO, SupportedLanguage.KURDISH, SupportedLanguage.URDU,
                SupportedLanguage.URDU_PK, SupportedLanguage.URDU_IN, SupportedLanguage.SINDHI
            ],
            "devanagari": [
                SupportedLanguage.HINDI, SupportedLanguage.HINDI_IN, SupportedLanguage.MARATHI,
                SupportedLanguage.NEPALI, SupportedLanguage.SANSKRIT, SupportedLanguage.BODO,
                SupportedLanguage.MAITHILI, SupportedLanguage.DOGRI
            ],
            "bengali": [
                SupportedLanguage.BENGALI, SupportedLanguage.BENGALI_BD, SupportedLanguage.BENGALI_IN,
                SupportedLanguage.ASSAMESE, SupportedLanguage.MANIPURI
            ],
            "tamil": [
                SupportedLanguage.TAMIL, SupportedLanguage.TAMIL_IN, SupportedLanguage.TAMIL_LK,
                SupportedLanguage.TAMIL_SG
            ],
            "telugu": [
                SupportedLanguage.TELUGU
            ],
            "gujarati": [
                SupportedLanguage.GUJARATI
            ],
            "gurmukhi": [
                SupportedLanguage.PUNJABI, SupportedLanguage.PUNJABI_IN, SupportedLanguage.PUNJABI_PK
            ],
            "kannada": [
                SupportedLanguage.KANNADA
            ],
            "malayalam": [
                SupportedLanguage.MALAYALAM
            ],
            "oriya": [
                SupportedLanguage.ORIYA
            ],
            "sinhala": [
                SupportedLanguage.SINHALA
            ],
            "thaana": [
                SupportedLanguage.DHIVEHI
            ],
            "chinese_simplified": [
                SupportedLanguage.CHINESE_SIMPLIFIED, SupportedLanguage.CHINESE_SG
            ],
            "chinese_traditional": [
                SupportedLanguage.CHINESE_TRADITIONAL, SupportedLanguage.CHINESE_HK
            ],
            "japanese": [
                SupportedLanguage.JAPANESE, SupportedLanguage.JAPANESE_KANSAI, SupportedLanguage.OKINAWAN
            ],
            "korean": [
                SupportedLanguage.KOREAN, SupportedLanguage.KOREAN_KR, SupportedLanguage.KOREAN_KP
            ],
            "thai": [
                SupportedLanguage.THAI
            ],
            "lao": [
                SupportedLanguage.LAO
            ],
            "khmer": [
                SupportedLanguage.KHMER
            ],
            "burmese": [
                SupportedLanguage.BURMESE
            ],
            "tibetan": [
                SupportedLanguage.TIBETAN
            ],
            "hebrew": [
                SupportedLanguage.HEBREW, SupportedLanguage.HEBREW_IL
            ],
            "greek": [
                SupportedLanguage.GREEK, SupportedLanguage.ANCIENT_GREEK
            ],
            "armenian": [
                SupportedLanguage.ARMENIAN
            ],
            "georgian": [
                SupportedLanguage.GEORGIAN
            ],
            "amharic": [
                SupportedLanguage.AMHARIC, SupportedLanguage.TIGRINYA
            ],
            "tifinagh": [
                SupportedLanguage.AMAZIGH, SupportedLanguage.TAMAZIGHT, SupportedLanguage.TARIFIT,
                SupportedLanguage.TASHELHIT, SupportedLanguage.TAMAZIGHT_MOROCCO, SupportedLanguage.KABYLE,
                SupportedLanguage.CHAOUIA, SupportedLanguage.MOZABITE, SupportedLanguage.CHENOUA,
                SupportedLanguage.TAGARGRENT, SupportedLanguage.TAMAHAQ, SupportedLanguage.TAWALLAMMAT,
                SupportedLanguage.TAYART, SupportedLanguage.TAMASHEQ, SupportedLanguage.TAMASHEK,
                SupportedLanguage.NAFUSI, SupportedLanguage.SIWI, SupportedLanguage.ZENAGA,
                SupportedLanguage.TETSERRET, SupportedLanguage.TUAREG_AHAGGAR, SupportedLanguage.TUAREG_AIR,
                SupportedLanguage.GHADAMES, SupportedLanguage.AWJILA, SupportedLanguage.SOKNA,
                SupportedLanguage.FOQAHA
            ],
            "nubic": [
                SupportedLanguage.NUBIAN, SupportedLanguage.DONGOLAWI, SupportedLanguage.KENZI,
                SupportedLanguage.FADICCA, SupportedLanguage.NOBIIN
            ]
        }
        
        for script, languages in scripts.items():
            if language in languages:
                return script
        
        return "latin"  # Default to Latin script

    @staticmethod
    def get_language_direction(language: 'SupportedLanguage') -> str:
        """Get text direction for the given language"""
        rtl_languages = [
            SupportedLanguage.ARABIC, SupportedLanguage.ARABIC_SA, SupportedLanguage.ARABIC_EG,
            SupportedLanguage.ARABIC_AE, SupportedLanguage.ARABIC_MA, SupportedLanguage.ARABIC_TN,
            SupportedLanguage.ARABIC_DZ, SupportedLanguage.ARABIC_IQ, SupportedLanguage.ARABIC_JO,
            SupportedLanguage.ARABIC_LB, SupportedLanguage.ARABIC_SY, SupportedLanguage.ARABIC_KW,
            SupportedLanguage.ARABIC_BH, SupportedLanguage.ARABIC_QA, SupportedLanguage.ARABIC_OM,
            SupportedLanguage.ARABIC_YE, SupportedLanguage.ARABIC_PS, SupportedLanguage.ARABIC_LY,
            SupportedLanguage.ARABIC_SD, SupportedLanguage.ARABIC_MR, SupportedLanguage.ARABIC_DJ_AR,
            SupportedLanguage.ARABIC_SO_AR, SupportedLanguage.ARABIC_TD_AR, SupportedLanguage.ARABIC_KM_AR,
            SupportedLanguage.HEBREW, SupportedLanguage.HEBREW_IL, SupportedLanguage.PERSIAN,
            SupportedLanguage.PERSIAN_IR, SupportedLanguage.PERSIAN_AF, SupportedLanguage.DARI,
            SupportedLanguage.URDU, SupportedLanguage.URDU_PK, SupportedLanguage.URDU_IN,
            SupportedLanguage.PASHTO, SupportedLanguage.KURDISH, SupportedLanguage.SINDHI,
            SupportedLanguage.ARAMAIC, SupportedLanguage.ASSYRIAN, SupportedLanguage.DHIVEHI
        ]
        
        return "rtl" if language in rtl_languages else "ltr"

    @staticmethod
    def is_tonal_language(language: 'SupportedLanguage') -> bool:
        """Check if the language is tonal"""
        tonal_languages = [
            SupportedLanguage.CHINESE_SIMPLIFIED, SupportedLanguage.CHINESE_TRADITIONAL,
            SupportedLanguage.CHINESE_HK, SupportedLanguage.CHINESE_SG, SupportedLanguage.CANTONESE,
            SupportedLanguage.HAKKA, SupportedLanguage.MIN_NAN, SupportedLanguage.WU_CHINESE,
            SupportedLanguage.THAI, SupportedLanguage.LAO, SupportedLanguage.VIETNAMESE,
            SupportedLanguage.VIETNAMESE_VN, SupportedLanguage.BURMESE, SupportedLanguage.YORUBA,
            SupportedLanguage.IGBO, SupportedLanguage.NAVAJO
        ]
        
        return language in tonal_languages

    @staticmethod
    def get_linguistic_complexity(language: 'SupportedLanguage') -> str:
        """Get linguistic complexity level of the language"""
        complexity_levels = {
            "very_high": [
                SupportedLanguage.ARABIC, SupportedLanguage.CHINESE_SIMPLIFIED, SupportedLanguage.CHINESE_TRADITIONAL,
                SupportedLanguage.JAPANESE, SupportedLanguage.KOREAN, SupportedLanguage.FINNISH, SupportedLanguage.HUNGARIAN,
                SupportedLanguage.NAVAJO, SupportedLanguage.GEORGIAN, SupportedLanguage.THAI, SupportedLanguage.VIETNAMESE
            ],
            "high": [
                SupportedLanguage.RUSSIAN, SupportedLanguage.GERMAN, SupportedLanguage.HINDI, SupportedLanguage.BENGALI,
                SupportedLanguage.TAMIL, SupportedLanguage.TELUGU, SupportedLanguage.MARATHI, SupportedLanguage.GUJARATI,
                SupportedLanguage.KANNADA, SupportedLanguage.MALAYALAM, SupportedLanguage.POLISH, SupportedLanguage.CZECH,
                SupportedLanguage.SERBIAN, SupportedLanguage.CROATIAN, SupportedLanguage.GREEK, SupportedLanguage.ARMENIAN,
                SupportedLanguage.HEBREW, SupportedLanguage.TURKISH, SupportedLanguage.PERSIAN, SupportedLanguage.PASHTO
            ],
            "medium": [
                SupportedLanguage.FRENCH, SupportedLanguage.SPANISH, SupportedLanguage.ITALIAN, SupportedLanguage.PORTUGUESE,
                SupportedLanguage.DUTCH, SupportedLanguage.SWEDISH, SupportedLanguage.NORWEGIAN, SupportedLanguage.DANISH,
                SupportedLanguage.ROMANIAN, SupportedLanguage.UKRAINIAN, SupportedLanguage.BULGARIAN, SupportedLanguage.SLOVAK,
                SupportedLanguage.SLOVENIAN, SupportedLanguage.LITHUANIAN, SupportedLanguage.LATVIAN, SupportedLanguage.ESTONIAN,
                SupportedLanguage.PUNJABI, SupportedLanguage.URDU, SupportedLanguage.SINDHI, SupportedLanguage.NEPALI
            ],
            "low": [
                SupportedLanguage.ENGLISH, SupportedLanguage.INDONESIAN, SupportedLanguage.MALAY, SupportedLanguage.SWAHILI,
                SupportedLanguage.FILIPINO, SupportedLanguage.TAGALOG, SupportedLanguage.AFRIKAANS, SupportedLanguage.ESPERANTO,
                SupportedLanguage.INTERLINGUA
            ]
        }
        
        for level, languages in complexity_levels.items():
            if language in languages:
                return level
        
        return "medium"  # Default complexity level


@dataclass
class LanguageConfiguration:
    """Language configuration and metadata"""
    language: SupportedLanguage
    iso_code: str
    native_name: str
    english_name: str
    rtl: bool = False
    script: str = "Latin"
    primary_regions: List[str] = field(default_factory=list)
    fallback_languages: List[SupportedLanguage] = field(default_factory=list)
    complexity_score: float = 1.0  # Language complexity for translation
    cultural_sensitivity: float = 0.5  # How culturally sensitive the language is
    formality_importance: float = 0.5  # Importance of formal vs informal
    
    
@dataclass
class LanguageProfile:
    """User language profile and preferences"""
    user_id: str
    primary_language: SupportedLanguage
    secondary_languages: List[SupportedLanguage] = field(default_factory=list)
    preferred_formality: str = "neutral"  # formal, informal, neutral
    country_code: Optional[str] = None
    timezone: Optional[str] = None
    date_format_preference: Optional[str] = None
    number_format_preference: Optional[str] = None
    currency_preference: Optional[str] = None
    communication_style: str = "balanced"  # direct, indirect, balanced
    cultural_context_level: float = 0.5  # How much cultural adaptation to apply
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    interaction_count: int = 0
    confidence_scores: Dict[str, float] = field(default_factory=dict)


@dataclass
class LanguageDetectionResult:
    """Language detection result with confidence metrics"""
    detected_language: SupportedLanguage
    confidence_score: float
    alternative_languages: List[Tuple[SupportedLanguage, float]] = field(default_factory=list)
    detection_method: str = "multi_engine"
    processing_time: float = 0.0
    text_length: int = 0
    quality_indicators: Dict[str, float] = field(default_factory=dict)


class LanguageDetector:
    """Ultra-advanced language detection using multiple engines"""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis_client = redis_client
        self.detection_stats = defaultdict(int)
        self.confidence_threshold = 0.7
        
        # Initialize detection engines
        self._initialize_detection_engines()
        
    async def _initialize_detection_engines(self):
        """Initialize multiple language detection engines"""
        try:
            # FastText model for language detection
            self.fasttext_model = None
            try:
                self.fasttext_model = fasttext.load_model('lid.176.bin')
            except Exception as e:
                logger.warning(f"FastText model not available: {e}")
            
            # Hugging Face transformer for language detection
            self.transformer_detector = None
            try:
                self.transformer_detector = pipeline(
                    "text-classification",
                    model="papluca/xlm-roberta-base-language-detection"
                )
            except Exception as e:
                logger.warning(f"Transformer detector not available: {e}")
                
            # SpaCy models for multiple languages
            self.spacy_models = {}
            for lang_code in ["en", "de", "fr", "es", "it"]:
                try:
                    self.spacy_models[lang_code] = spacy.load(f"{lang_code}_core_web_sm")
                except Exception:
                    logger.warning(f"SpaCy model for {lang_code} not available")
            
            logger.info("Language detection engines initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize detection engines: {e}")
    
    async def detect_language(
        self, 
        text: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> LanguageDetectionResult:
        """
        Detect language using multiple engines with confidence scoring
        """
        start_time = datetime.now()
        
        try:
            if not text or len(text.strip()) < 3:
                return LanguageDetectionResult(
                    detected_language=SupportedLanguage.ENGLISH,
                    confidence_score=0.1,
                    detection_method="fallback_default"
                )
            
            # Clean and normalize text
            cleaned_text = self._clean_text_for_detection(text)
            
            # Run multiple detection engines
            detection_results = []
            
            # 1. Langdetect
            langdetect_result = await self._detect_with_langdetect(cleaned_text)
            if langdetect_result:
                detection_results.append(langdetect_result)
            
            # 2. FastText
            fasttext_result = await self._detect_with_fasttext(cleaned_text)
            if fasttext_result:
                detection_results.append(fasttext_result)
            
            # 3. Transformer
            transformer_result = await self._detect_with_transformer(cleaned_text)
            if transformer_result:
                detection_results.append(transformer_result)
            
            # 4. Polyglot
            polyglot_result = await self._detect_with_polyglot(cleaned_text)
            if polyglot_result:
                detection_results.append(polyglot_result)
            
            # 5. User context if available
            user_context_result = await self._detect_with_user_context(text, user_id)
            if user_context_result:
                detection_results.append(user_context_result)
            
            # Ensemble detection - combine results
            final_result = await self._ensemble_detection(detection_results, cleaned_text)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            final_result.processing_time = processing_time
            final_result.text_length = len(text)
            
            # Update statistics
            self.detection_stats[final_result.detected_language.value] += 1
            self.detection_stats["total_detections"] += 1
            
            # Cache result if confidence is high
            if final_result.confidence_score > self.confidence_threshold:
                await self._cache_detection_result(text, final_result)
            
            return final_result
            
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return LanguageDetectionResult(
                detected_language=SupportedLanguage.ENGLISH,
                confidence_score=0.0,
                detection_method="error_fallback"
            )
    
    async def _detect_with_langdetect(self, text: str) -> Optional[Tuple[SupportedLanguage, float]]:
        """Detect language using langdetect library"""
        try:
            probabilities = detect_probabilities(text)
            if probabilities:
                lang_code = probabilities[0].lang
                confidence = probabilities[0].prob
                
                # Convert to SupportedLanguage
                supported_lang = self._convert_to_supported_language(lang_code)
                if supported_lang:
                    return (supported_lang, confidence * 0.8)  # Weight factor
            
        except (LangDetectException, Exception) as e:
            logger.debug(f"Langdetect failed: {e}")
        
        return None
    
    async def _detect_with_fasttext(self, text: str) -> Optional[Tuple[SupportedLanguage, float]]:
        """Detect language using FastText model"""
        try:
            if self.fasttext_model:
                predictions = self.fasttext_model.predict(text.replace('\n', ' '), k=3)
                labels, scores = predictions
                
                if labels and scores:
                    # Extract language code from label (__label__en)
                    lang_code = labels[0].replace('__label__', '')
                    confidence = float(scores[0])
                    
                    supported_lang = self._convert_to_supported_language(lang_code)
                    if supported_lang:
                        return (supported_lang, confidence * 0.9)  # Higher weight for FastText
            
        except Exception as e:
            logger.debug(f"FastText detection failed: {e}")
        
        return None
    
    async def _detect_with_transformer(self, text: str) -> Optional[Tuple[SupportedLanguage, float]]:
        """Detect language using transformer model"""
        try:
            if self.transformer_detector and len(text) > 10:
                result = self.transformer_detector(text[:512])  # Limit text length
                
                if result and isinstance(result, list) and len(result) > 0:
                    prediction = result[0]
                    lang_code = prediction['label'].lower()
                    confidence = prediction['score']
                    
                    supported_lang = self._convert_to_supported_language(lang_code)
                    if supported_lang:
                        return (supported_lang, confidence * 0.95)  # Highest weight for transformer
            
        except Exception as e:
            logger.debug(f"Transformer detection failed: {e}")
        
        return None
    
    async def _detect_with_polyglot(self, text: str) -> Optional[Tuple[SupportedLanguage, float]]:
        """Detect language using Polyglot"""
        try:
            detector = Detector(text)
            if detector.language and detector.language.confidence > 0.5:
                lang_code = detector.language.code
                confidence = detector.language.confidence / 100.0  # Convert to 0-1 scale
                
                supported_lang = self._convert_to_supported_language(lang_code)
                if supported_lang:
                    return (supported_lang, confidence * 0.7)  # Lower weight for polyglot
            
        except Exception as e:
            logger.debug(f"Polyglot detection failed: {e}")
        
        return None
    
    async def _detect_with_user_context(
        self, 
        text: str, 
        user_id: Optional[str]
    ) -> Optional[Tuple[SupportedLanguage, float]]:
        """Use user context to influence language detection"""
        try:
            if not user_id:
                return None
            
            # Get user's language profile from cache
            cached_profile = await self.redis_client.get(f"language_profile:{user_id}")
            if cached_profile:
                profile_data = json.loads(cached_profile)
                primary_lang = SupportedLanguage(profile_data.get("primary_language"))
                
                # Give bonus confidence if detected language matches user's primary
                # This will be used in ensemble method
                return (primary_lang, 0.3)  # Context bonus
            
        except Exception as e:
            logger.debug(f"User context detection failed: {e}")
        
        return None
    
    async def _ensemble_detection(
        self, 
        results: List[Tuple[SupportedLanguage, float]], 
        text: str
    ) -> LanguageDetectionResult:
        """Combine multiple detection results using ensemble method"""
        if not results:
            return LanguageDetectionResult(
                detected_language=SupportedLanguage.ENGLISH,
                confidence_score=0.1,
                detection_method="no_detection_fallback"
            )
        
        # Weight and combine results
        language_scores = defaultdict(float)
        total_weight = 0.0
        
        for lang, confidence in results:
            language_scores[lang] += confidence
            total_weight += confidence
        
        # Normalize scores
        if total_weight > 0:
            for lang in language_scores:
                language_scores[lang] /= len(results)  # Average confidence
        
        # Find best detection
        best_language = max(language_scores.items(), key=lambda x: x[1])
        detected_lang, confidence = best_language
        
        # Build alternative languages
        alternatives = []
        for lang, score in sorted(language_scores.items(), key=lambda x: x[1], reverse=True)[1:5]:
            if score > 0.1:  # Only include meaningful alternatives
                alternatives.append((lang, score))
        
        # Quality indicators
        quality_indicators = {
            "num_engines_used": len(results),
            "score_variance": self._calculate_score_variance(language_scores),
            "text_quality": self._assess_text_quality(text)
        }
        
        return LanguageDetectionResult(
            detected_language=detected_lang,
            confidence_score=confidence,
            alternative_languages=alternatives,
            detection_method="multi_engine_ensemble",
            quality_indicators=quality_indicators
        )
    
    def _convert_to_supported_language(self, lang_code: str) -> Optional[SupportedLanguage]:
        """Convert language code to SupportedLanguage enum"""
        # Normalize language code
        lang_code = lang_code.lower().strip()
        
        # Handle special cases
        if lang_code in ['zh-cn', 'zh_cn', 'zh-hans']:
            return SupportedLanguage.CHINESE_SIMPLIFIED
        elif lang_code in ['zh-tw', 'zh_tw', 'zh-hant']:
            return SupportedLanguage.CHINESE_TRADITIONAL
        
        # Direct mapping
        language_mapping = {
            'en': SupportedLanguage.ENGLISH,
            'de': SupportedLanguage.GERMAN,
            'fr': SupportedLanguage.FRENCH,
            'es': SupportedLanguage.SPANISH,
            'it': SupportedLanguage.ITALIAN,
            'pt': SupportedLanguage.PORTUGUESE,
            'nl': SupportedLanguage.DUTCH,
            'ru': SupportedLanguage.RUSSIAN,
            'ja': SupportedLanguage.JAPANESE,
            'ko': SupportedLanguage.KOREAN,
            'ar': SupportedLanguage.ARABIC,
            'hi': SupportedLanguage.HINDI,
            'tr': SupportedLanguage.TURKISH,
            'pl': SupportedLanguage.POLISH,
            'sv': SupportedLanguage.SWEDISH,
            'no': SupportedLanguage.NORWEGIAN,
            'da': SupportedLanguage.DANISH,
            'fi': SupportedLanguage.FINNISH,
            'cs': SupportedLanguage.CZECH,
            'hu': SupportedLanguage.HUNGARIAN,
            'ro': SupportedLanguage.ROMANIAN,
            'bg': SupportedLanguage.BULGARIAN,
            'hr': SupportedLanguage.CROATIAN,
            'sk': SupportedLanguage.SLOVAK,
            'sl': SupportedLanguage.SLOVENIAN,
            'lt': SupportedLanguage.LITHUANIAN,
            'lv': SupportedLanguage.LATVIAN,
            'et': SupportedLanguage.ESTONIAN,
            'el': SupportedLanguage.GREEK,
            'he': SupportedLanguage.HEBREW,
            'th': SupportedLanguage.THAI,
            'vi': SupportedLanguage.VIETNAMESE,
            'id': SupportedLanguage.INDONESIAN,
            'ms': SupportedLanguage.MALAY,
            'tl': SupportedLanguage.FILIPINO,
            'uk': SupportedLanguage.UKRAINIAN,
            'bn': SupportedLanguage.BENGALI,
            'ur': SupportedLanguage.URDU,
            'fa': SupportedLanguage.PERSIAN,
            'sw': SupportedLanguage.SWAHILI
        }
        
        return language_mapping.get(lang_code)
    
    def _clean_text_for_detection(self, text: str) -> str:
        """Clean text for better language detection"""
        # Remove URLs, mentions, hashtags
        text = re.sub(r'http[s]?://\S+', '', text)
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#\w+', '', text)
        
        # Remove extra whitespace and normalize
        text = ' '.join(text.split())
        
        return text.strip()
    
    def _calculate_score_variance(self, scores: Dict[SupportedLanguage, float]) -> float:
        """Calculate variance in detection scores"""
        if len(scores) < 2:
            return 0.0
        
        values = list(scores.values())
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        
        return variance
    
    def _assess_text_quality(self, text: str) -> float:
        """Assess text quality for detection"""
        quality_score = 1.0
        
        # Length factor
        if len(text) < 10:
            quality_score *= 0.3
        elif len(text) < 50:
            quality_score *= 0.7
        
        # Character variety
        unique_chars = len(set(text.lower()))
        if unique_chars < 5:
            quality_score *= 0.5
        
        # Word count
        word_count = len(text.split())
        if word_count < 3:
            quality_score *= 0.4
        
        return min(quality_score, 1.0)
    
    async def _cache_detection_result(self, text: str, result: LanguageDetectionResult):
        """Cache high-confidence detection results"""
        try:
            cache_key = f"lang_detect:{hash(text[:100])}"
            cache_data = {
                "language": result.detected_language.value,
                "confidence": result.confidence_score,
                "method": result.detection_method
            }
            
            await self.redis_client.setex(
                cache_key,
                3600,  # 1 hour TTL
                json.dumps(cache_data)
            )
            
        except Exception as e:
            logger.debug(f"Failed to cache detection result: {e}")


class LanguageProfileManager:
    """Advanced user language profile management"""
    
    def __init__(self, db_session: AsyncSession, redis_client: aioredis.Redis):
        self.db_session = db_session
        self.redis_client = redis_client
        
    async def create_language_profile(
        self,
        user_id: str,
        primary_language: SupportedLanguage,
        country_code: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> LanguageProfile:
        """Create comprehensive language profile for user"""
        try:
            # Infer cultural settings from country code
            cultural_settings = await self._infer_cultural_settings(country_code)
            
            profile = LanguageProfile(
                user_id=user_id,
                primary_language=primary_language,
                country_code=country_code,
                timezone=cultural_settings.get("timezone"),
                date_format_preference=cultural_settings.get("date_format"),
                currency_preference=cultural_settings.get("currency")
            )
            
            # Apply additional preferences
            if preferences:
                for key, value in preferences.items():
                    if hasattr(profile, key):
                        setattr(profile, key, value)
            
            # Cache profile
            await self._cache_language_profile(profile)
            
            # Store in database
            await self._store_language_profile_db(profile)
            
            logger.info(f"Created language profile for user {user_id}: {primary_language.value}")
            return profile
            
        except Exception as e:
            logger.error(f"Failed to create language profile: {e}")
            raise
    
    async def get_language_profile(self, user_id: str) -> Optional[LanguageProfile]:
        """Get user language profile with fallback mechanisms"""
        try:
            # Try cache first
            cached_profile = await self.redis_client.get(f"language_profile:{user_id}")
            if cached_profile:
                profile_data = json.loads(cached_profile)
                return self._deserialize_language_profile(profile_data)
            
            # Try database
            profile = await self._load_language_profile_db(user_id)
            if profile:
                await self._cache_language_profile(profile)
                return profile
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get language profile: {e}")
            return None
    
    async def update_language_profile(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> Optional[LanguageProfile]:
        """Update user language profile"""
        try:
            profile = await self.get_language_profile(user_id)
            if not profile:
                return None
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            
            profile.updated_at = datetime.now(timezone.utc)
            profile.interaction_count += 1
            
            # Update cache and database
            await self._cache_language_profile(profile)
            await self._store_language_profile_db(profile)
            
            return profile
            
        except Exception as e:
            logger.error(f"Failed to update language profile: {e}")
            return None
    
    async def _infer_cultural_settings(self, country_code: Optional[str]) -> Dict[str, Any]:
        """Infer cultural settings from country code"""
        if not country_code:
            return {}
        
        try:
            cultural_mappings = {
                "DE": {
                    "timezone": "Europe/Berlin",
                    "date_format": "%d.%m.%Y",
                    "currency": "EUR"
                },
                "FR": {
                    "timezone": "Europe/Paris", 
                    "date_format": "%d/%m/%Y",
                    "currency": "EUR"
                },
                "US": {
                    "timezone": "America/New_York",
                    "date_format": "%m/%d/%Y", 
                    "currency": "USD"
                },
                "GB": {
                    "timezone": "Europe/London",
                    "date_format": "%d/%m/%Y",
                    "currency": "GBP"
                },
                "JP": {
                    "timezone": "Asia/Tokyo",
                    "date_format": "%Y/%m/%d",
                    "currency": "JPY"
                },
                "CN": {
                    "timezone": "Asia/Shanghai",
                    "date_format": "%Y-%m-%d",
                    "currency": "CNY"
                }
            }
            
            return cultural_mappings.get(country_code.upper(), {})
            
        except Exception as e:
            logger.error(f"Failed to infer cultural settings: {e}")
            return {}
    
    async def _cache_language_profile(self, profile: LanguageProfile):
        """Cache language profile in Redis"""
        try:
            cache_data = {
                "user_id": profile.user_id,
                "primary_language": profile.primary_language.value,
                "secondary_languages": [lang.value for lang in profile.secondary_languages],
                "preferred_formality": profile.preferred_formality,
                "country_code": profile.country_code,
                "timezone": profile.timezone,
                "date_format_preference": profile.date_format_preference,
                "number_format_preference": profile.number_format_preference,
                "currency_preference": profile.currency_preference,
                "communication_style": profile.communication_style,
                "cultural_context_level": profile.cultural_context_level,
                "created_at": profile.created_at.isoformat(),
                "updated_at": profile.updated_at.isoformat(),
                "interaction_count": profile.interaction_count,
                "confidence_scores": profile.confidence_scores
            }
            
            await self.redis_client.setex(
                f"language_profile:{profile.user_id}",
                86400 * 30,  # 30 days TTL
                json.dumps(cache_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"Failed to cache language profile: {e}")
    
    async def _store_language_profile_db(self, profile: LanguageProfile):
        """Store language profile in database"""
        # This would interact with the database
        # Implementation depends on your database schema
        pass
    
    async def _load_language_profile_db(self, user_id: str) -> Optional[LanguageProfile]:
        """Load language profile from database"""
        # This would load from database
        # Implementation depends on your database schema
        return None
    
    def _deserialize_language_profile(self, data: Dict[str, Any]) -> LanguageProfile:
        """Deserialize language profile from cached data"""
        return LanguageProfile(
            user_id=data["user_id"],
            primary_language=SupportedLanguage(data["primary_language"]),
            secondary_languages=[SupportedLanguage(lang) for lang in data.get("secondary_languages", [])],
            preferred_formality=data.get("preferred_formality", "neutral"),
            country_code=data.get("country_code"),
            timezone=data.get("timezone"),
            date_format_preference=data.get("date_format_preference"),
            number_format_preference=data.get("number_format_preference"),
            currency_preference=data.get("currency_preference"),
            communication_style=data.get("communication_style", "balanced"),
            cultural_context_level=data.get("cultural_context_level", 0.5),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            interaction_count=data.get("interaction_count", 0),
            confidence_scores=data.get("confidence_scores", {})
        )


class LanguageManager:
    """Master language management orchestrator"""
    
    def __init__(self, db_session: AsyncSession, redis_client: aioredis.Redis):
        self.db_session = db_session
        self.redis_client = redis_client
        self.detector = LanguageDetector(redis_client)
        self.profile_manager = LanguageProfileManager(db_session, redis_client)
        
        # Language configurations
        self.language_configs = self._initialize_language_configs()
        
    def _initialize_language_configs(self) -> Dict[SupportedLanguage, LanguageConfiguration]:
        """Initialize language configurations"""
        configs = {}
        
        # Major languages with full configuration
        configs[SupportedLanguage.ENGLISH] = LanguageConfiguration(
            language=SupportedLanguage.ENGLISH,
            iso_code="en",
            native_name="English",
            english_name="English",
            rtl=False,
            script="Latin",
            primary_regions=["US", "GB", "CA", "AU", "NZ"],
            fallback_languages=[],
            complexity_score=1.0,
            cultural_sensitivity=0.3,
            formality_importance=0.4
        )
        
        configs[SupportedLanguage.GERMAN] = LanguageConfiguration(
            language=SupportedLanguage.GERMAN,
            iso_code="de",
            native_name="Deutsch",
            english_name="German",
            rtl=False,
            script="Latin",
            primary_regions=["DE", "AT", "CH"],
            fallback_languages=[SupportedLanguage.ENGLISH],
            complexity_score=1.3,
            cultural_sensitivity=0.6,
            formality_importance=0.8
        )
        
        configs[SupportedLanguage.FRENCH] = LanguageConfiguration(
            language=SupportedLanguage.FRENCH,
            iso_code="fr",
            native_name="Français",
            english_name="French",
            rtl=False,
            script="Latin", 
            primary_regions=["FR", "CA", "BE", "CH"],
            fallback_languages=[SupportedLanguage.ENGLISH],
            complexity_score=1.2,
            cultural_sensitivity=0.7,
            formality_importance=0.9
        )
        
        # Add more language configurations as needed
        
        return configs
    
    async def detect_and_configure_language(
        self,
        text: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[LanguageDetectionResult, Optional[LanguageConfiguration]]:
        """Detect language and return configuration"""
        detection_result = await self.detector.detect_language(text, user_id, context)
        language_config = self.language_configs.get(detection_result.detected_language)
        
        return detection_result, language_config
    
    async def get_user_language_context(self, user_id: str) -> Dict[str, Any]:
        """Get complete language context for user"""
        profile = await self.profile_manager.get_language_profile(user_id)
        
        if profile:
            language_config = self.language_configs.get(profile.primary_language)
            return {
                "profile": profile,
                "configuration": language_config,
                "supported_languages": list(self.language_configs.keys())
            }
        
        return {
            "profile": None,
            "configuration": None,
            "supported_languages": list(self.language_configs.keys())
        }
    
    async def is_language_supported(self, language: Union[str, SupportedLanguage]) -> bool:
        """Check if language is supported"""
        if isinstance(language, str):
            try:
                language = SupportedLanguage(language)
            except ValueError:
                return False
        
        return language in self.language_configs
    
    async def get_language_statistics(self) -> Dict[str, Any]:
        """Get language usage statistics"""
        return {
            "detection_stats": dict(self.detector.detection_stats),
            "supported_languages_count": len(self.language_configs),
            "supported_languages": [lang.value for lang in self.language_configs.keys()]
        }
