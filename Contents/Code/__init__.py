# -*- coding: utf-8 -*-
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *
import time
import datetime
import base64

####################################################################################################
# Author 		: GuinuX
####################################################################################################

####################################################################################################

PLUGIN_PREFIX = "/video/W9Replay"
PLUGIN_ID               = "com.plexapp.plugins.W9Replay"
PLUGIN_REVISION         = 0.1
PLUGIN_UPDATES_ENABLED  = True

NAME 		= L('W9 Replay')
ART         = 'art-default.jpg'
ICON        = 'icon-default.png'

CATALOG_KEY = "ElFsg.Ot"
CATALOG_XML = ""
IMAGES_SERVER = ""
CONFIGURATION_URL = "http://www.w9replay.fr/files/w9configuration_lv3.xml?t=1"

####################################################################################################

def Start():

	Plugin.AddPrefixHandler(PLUGIN_PREFIX, VideoMainMenu, NAME, ICON, ART)
	Plugin.AddViewGroup("Coverflow", viewMode="Coverflow", mediaType="items")
	Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
	
	MediaContainer.art = R(ART)
	MediaContainer.title1 = NAME
	DirectoryItem.thumb = R(ICON)
	HTTP.SetcacheTime = CACHE_1HOUR


def VideoMainMenu():

	global CATALOG_XML
	global IMAGES_SERVER
	
	dir = MediaContainer(viewGroup="Coverflow")
	try:
		xml = HTTP.Request(CONFIGURATION_URL)
	except Ex.HTTPError, e:
		Log(NAME + " Plugin : " + str(e))
		return MessageContainer(NAME, "Erreur lors de la récupération de la configuration.")	
	except Exception, e :
		Log(NAME + " Plugin : " + str(e))
		return MessageContainer(NAME, "Erreur lors de la récupération de la configuration.")

	IMAGES_SERVER = XML.ElementFromString( xml ).xpath("/config/path/image")[0].text
	CatalogueURL = XML.ElementFromString( xml ).xpath("/config/services/service[@name='GetCatalogueService']/url")[0].text
	CatalogueURL = CatalogueURL.replace("-9.xml","-w9.xml")
	
	try:
		CATALOG_XML = HTTP.Request(CatalogueURL,cacheTime=CACHE_1HOUR)	
	except Ex.HTTPError, e:
		Log(NAME + " Plugin : " + str(e))
		return MessageContainer(NAME, "Erreur lors de la récupération du Catalogue.")		
	except Exception, e :
		Log(NAME + " Plugin : " + str(e))
		return MessageContainer(NAME, "Erreur lors de la récupération du Catalogue.")
		
		
	if CATALOG_XML.find( "<template_exchange_WEB>" ) == -1: return MessageContainer(NAME, "Flux XML non valide.")
	
	finXML = CATALOG_XML.find( "</template_exchange_WEB>" ) + len( "</template_exchange_WEB>" )
	CATALOG_XML = CATALOG_XML[ : finXML ]
	
	for category in XML.ElementFromString(CATALOG_XML).xpath("//template_exchange_WEB/categorie"):
		nom = category.xpath("./nom")[0].text
		image = IMAGES_SERVER + category.get('big_img_url')
		idCategorie = category.get('id')
		dir.Append(Function(DirectoryItem(ListShows, title = nom, thumb = image), idCategorie = idCategorie, nomCategorie = nom))
	
	return dir


def ListShows(sender, idCategorie, nomCategorie):

	global CATALOG_XML
	global IMAGES_SERVER
	
	dir = MediaContainer(viewGroup="Coverflow", title1 = NAME, title2 = nomCategorie)
	search = "/template_exchange_WEB/categorie[@id='" + idCategorie + "']/categorie"

	for item in XML.ElementFromString(CATALOG_XML).xpath(search):
		nom = item.xpath("nom")[0].text
		image = IMAGES_SERVER + item.get('big_img_url')
		idCategorie = item.get('id')

		dir.Append(Function(DirectoryItem(ListEpisodes, title = nom, thumb = image), idCategorie = idCategorie, nomCategorie = nom))
	
	return dir


def ListEpisodes(sender, idCategorie, nomCategorie):

	global CATALOG_XML
	global IMAGES_SERVER
		
	dir = MediaContainer(viewGroup="InfoList", title1 = NAME, title2 = nomCategorie)
	search = "//template_exchange_WEB/categorie/categorie[@id=" + idCategorie + "]/produit"
	
	for episode in XML.ElementFromString(CATALOG_XML).xpath(search):
		idProduit = episode.get('id')
		nom = episode.xpath("./nom")[0].text
		description = episode.xpath("./resume")[0].text
		image = IMAGES_SERVER + episode.get('big_img_url')
		video = episode.xpath("./fichemedia")[0].get('video_url')[:-4]
		date_diffusion = datetime.datetime(*(time.strptime(episode.xpath("./diffusion")[0].get('date'), "%Y-%m-%d %H:%M:%S")[0:6])).strftime("%d/%m/%Y à %Hh%M")
		str_duree = episode.xpath("./fichemedia")[0].get('duree')
		duree = long(str_duree) / 60
		dureevideo = long(str_duree)*1000
		description = description + '\n\nDiffusé le ' + date_diffusion + '\n' + 'Durée : ' + str(duree) + ' mn'
		lienValide = "rtmp://m6dev.fcod.llnwd.net:443/a3100/d1/"
		dir.Append(RTMPVideoItem(url = lienValide, clip = video, title = nom, subtitle = nomCategorie, summary = description, duration = dureevideo , thumb = image))
	return dir
	
	
