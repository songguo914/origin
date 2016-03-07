#encoding=utf-8
import time
import json
import sys
import re
from Queue import Queue
from threading import Thread

import bs4
import requests
from lxml import etree
from bs4 import BeautifulSoup
from configobj import ConfigObj 


def Config(webserviceurl):
	# f = open(dir)
	# s = json.load(f,encoding='utf-8')
	# f.close()
	# return s
	import suds
	import os

	client = suds.client.Client(webserviceurl)
	
	resulttask =  client.service.getTask()
	print('webservice resulttask is %s,len(resulttask)=%s')%(resulttask,len(resulttask))
	#print ('taskid=%s')%resulttask[0][1]
	taskid = []
	type = []
	configversion = []
	configid = []
	taskparams = []
	#[fileLink]⊥http://web2.chinagrain.gov.cn/n16/n1122/n2082/n4683307.files/n4683275.rar∧[link]⊥/n16/n1122/n2082/4683307.html
	try:
		for i in xrange(len(resulttask)):
			taskid.append(resulttask[i][7])
			type.append(resulttask[i][8])
			configversion.append(resulttask[i][0])
			configid.append(resulttask[i][1])
			if len(resulttask[i]) > 9:
				taskparams.append(resulttask[i][8])
			else:
				taskparams.append('')
	except IndexError:
		return ['0']
	dir1 = []
	for i in xrange(len(resulttask)):
		dirstr = (r'.\%s.txt') % configid[i]
		dir1.append(dirstr)
	#print('dir = %s') % dir
	s_config = []
	fp = []
	list = []
	for i in xrange(len(resulttask)):
		list.append('')
		if os.path.exists(dir1[i]):
			fp.append(open(dir1[i]))
			s_config.append(json.load(fp[i],encoding='utf-8'))
			fp[i].close()
			
			if s_config[i]['version'] == str(configversion[i]):
				list[i] = (s_config[i],taskid[i],client,configversion[i],configid[i],type[i],taskparams[i])
				# return list
			else:
			#说明配置文件有更新
				result =  client.service.getTaskConf(configid[i],'page')
				#print ('------result.confContent = %s') %result.confContent
				#print ('getTaskConf[0]=%s') %result[0]
				#print client.last_received()
				s_config = json.loads(result.confContent,encoding='utf-8')
				
				with open(dir1[i],'w') as f:
					f.write(result.confContent)
				list[i] = (s_config,taskid[i],client,configversion[i],configid[i],type[i],taskparams[i])
				# return list
		else:
			#说明是第一次取到该任务写入配置文件
			result =  client.service.getTaskConf(configid[i],'page')
			#print ('------result.confContent = %s') %result.confContent
			#print ('getTaskConf[0]=%s') %result[0]
			#print client.last_received()
			s_config = json.loads(result.confContent,encoding='utf-8')
			
			with open(dir1[i],'w') as f:
				f.write(result.confContent)
			list[i] = (s_config,taskid[i],client,configversion[i],configid[i],type[i],taskparams[i])
			# return s,taskid[i],client,configversion[i],configid[i],type[i]
	return list
#datastr按照配置文件抓取的需要内容
#content抓取的网页源码
def backwebservice(client,dict_config,taskid,flag,datastr,content,pagename,type,taskparam,configid):
	#import suds
	GUID = dict_config['GUID']
	#webserviceurl = 'http://10.0.0.121:8080/GrepServer/ws/grepService?wsdl'
	#client = suds.client.Client(webserviceurl)
	#print ('taskid=%s flag=%s') %(taskid,flag)
	if 1 == type :
		result =  client.service.infoReturn(taskid,flag,datastr,content,pagename,'','',type)
	elif 3 == type:
	#[fileLink]⊥http://web2.chinagrain.gov.cn/n16/n1122/n2082/n4683307.files/n4683275.rar∧[link]⊥/n16/n1122/n2082/4683307.html
		filelink = taskparam.split('∧')[0].split('⊥')
		filename,filetype = download(filelink,configid)
		result =  client.service.infoReturn(taskid,flag,datastr,content,pagename,filename,filetype,type)
# s = requests.Session()
# s.headers.update(headers)
	#print result

def Crawl(dirhtml,dict):
	#print dict['Url'],dict['Allowautoredirect'],dict['Timeout'],dict['headers']
	if dict['Method'] == 'get':
		r = requests.get(dict['Url'],allow_redirects=dict['Allowautoredirect'],timeout=dict['Timeout'],headers=dict['headers'])
	elif dict['Method'] == 'post':
		r = requests.post(dict['Url'],allow_redirects=dict['Allowautoredirect'],timeout=dict['Timeout'],headers=dict['headers'],data=dict['payload'])
	#print('r.encoding=%s')%r.encoding
	charset = re.compile(r'content="text/html;.?charset=(.*?)"').findall(r.text)
	
	r.encoding = (charset)
	content = r.text
	#print ('r.content = %s')%r.content
	
	with open(dirhtml,'w') as f:
		f.write(content)
	return content
def formatstr(xpathstring):
	return xpathstring[:xpathstring.index('[{0}]')]+xpathstring[len('[{0}]')+xpathstring.index('[{0}]'):]
	
def leng(forstart1,tree):
	# global tree
	nodes = tree.xpath(formatstr(forstart1))
	# for node in nodes:
		# print (node.text.strip())
	return len(nodes)

def xunhuan(xpathstring,n):
	return xpathstring[:xpathstring.index('[{0}]')] + '[' + str(n) + ']' + xpathstring[xpathstring.index('[{0}]') + len('[{0}]'):]
	
	
	
def Tree(content,nodelist,listname,dict,data):
	
	# soup = BeautifulSoup(content,'lxml')
	# with open(r'.\sourceHtml_beautifulsoup.html','w') as fb:
		# fb.write(soup.prettify())
	#tree = etree.HTML(soup.prettify())
	tree = etree.HTML(content)
	nodes = tree.xpath(dict['_Totalpage'])
	#print 'nodes',nodes
	for node in nodes:
		try:
			if 'true' == dict['_TotalpageIsAttributeValue'] and '' != dict['_TotalpageFilter']:
				dict_tmp = {}
				#print ('node = %s')%node.text.strip()
				dict_tmp[dict['Totalpage']] = (re.search(dict['_TotalpageFilter'],node.text.strip())).group()
				listname.append(dict_tmp)
				#print 'totalpage',dict_tmp
			elif 'true' == dict['_TotalpageIsAttributeValue'] and '' == dict['_TotalpageFilter']:
				dict_tmp = {}
				dict_tmp[dict['Totalpage']] = node
				listname.append(dict_tmp)
			elif 'false' == dict['_TotalpageIsAttributeValue'] and '' == dict['_TotalpageFilter']:
				dict_tmp = {}
				dict_tmp[dict['Totalpage']] = node.text.strip()
				listname.append(dict_tmp)
			elif 'false' == dict['_TotalpageIsAttributeValue'] and '' != dict['_TotalpageFilter']:
				dict_tmp = {}
				dict_tmp[dict['Totalpage']] = (re.search(dict['_TotalpageFilter'],node.text.strip())).group()
				listname.append(dict_tmp)
		except:
			print('xpath fail to crawl page')
			pass
			#print 'totalpage',dict_tmp
	if dict['pagenumber'] == 2:
		nodes = tree.xpath(dict['_Currentpage'])
		for node in nodes:
			try:
				if 'true' == dict['_CurrentpageIsAttributeValue'] and '' != dict['_CurrentpageFilter']:
					dict_tmp = {}
					dict_tmp[dict['Currentpage']] = (re.search(dict['_CurrentpageFilter'],node)).group()
					listname.append(dict_tmp)
				elif 'true' == dict['_CurrentpageIsAttributeValue'] and '' == dict['_CurrentpageFilter']:
					dict_tmp = {}
					dict_tmp[dict['Currentpage']] = node
					listname.append(dict_tmp)
				elif 'false' == dict['_CurrentpageIsAttributeValue'] and '' == dict['_CurrentpageFilter']:
					dict_tmp = {}
					dict_tmp[dict['Currentpage']] = node.text.strip()
					listname.append(dict_tmp)
				elif 'false' == dict['_CurrentpageIsAttributeValue'] and '' != dict['_CurrentpageFilter']:
					dict_tmp = {}
					dict_tmp[dict['Currentpage']] = (re.search(dict['_CurrentpageFilter'],node.text.strip())).group()
					listname.append(dict_tmp)
			except:
				print('xpath fail to crawl page')
				pass
			#print 'currentpage',dict_tmp
	#print ('forstart1=%s') %forstart1
	# nodes = tree.xpath(formatstr(forstart1))
	# for node in nodes:
		# print (node.text.strip())
	
	jsondir = {}
	#print ('DataNodenumber=%s') %DataNodenumber
	#print ('StartChildPostion=%s') %StartChildPostion
	#print ('LastChildPostion=%s') %LastChildPostion
	#print ('IntervalPosition=%s') %IntervalPosition
	for n in range(int(dict['StartChildPostion']), leng(dict['forstart1'],tree)+1-int(dict['LastChildPostion']), int(dict['IntervalPosition'])):
		for i in range(dict['DataNodenumber']):
			if 'true' == nodelist[i]['IsAttributeValue'] and '' != nodelist[i]['Filter']:
				jsondir[nodelist[i]['standardName']] = re.search(nodelist[i]['Filter'],tree.xpath(xunhuan(nodelist[i]['region'],n))[0]).group()
				#print ("nodelist[i]['Filter']=%s") %nodelist[i]['Filter']
				#print("tree.xpath(xunhuan(nodelist[i]['region'],n)[0])=%s") %tree.xpath(xunhuan(nodelist[i]['region'],n))[0]
			elif 'true' == nodelist[i]['IsAttributeValue'] and '' == nodelist[i]['Filter']:
				jsondir[nodelist[i]['standardName']] = tree.xpath(xunhuan(nodelist[i]['region'],n))[0].text.strip()
			elif 'false' == nodelist[i]['IsAttributeValue'] and '' == nodelist[i]['Filter']:
				#print("tree.xpath(xunhuan(nodelist[i]['region'],n)[0])=%s") %tree.xpath(xunhuan(nodelist[i]['region'],n))[0].text.strip()
				jsondir[nodelist[i]['standardName']] = tree.xpath(xunhuan(nodelist[i]['region'],n))[0].text.strip()
					#print ("xunhuan(nodelist[i]['region'],n)=%s") %xunhuan(nodelist[i]['region'],n)
			elif 'false' == nodelist[i]['IsAttributeValue'] and '' != nodelist[i]['Filter']:
				jsondir[nodelist[i]['standardName']] = re.search(nodelist[i]['Filter'],tree.xpath(xunhuan(nodelist[i]['region'],n))[0].text.strip()).group()
		listname.append(jsondir)
		jsondir = {}

	#print ('data = %s') % data
	flag = '100'
	try:
		datastr = json.dumps(data,ensure_ascii=False)
	# global flag
	except:
		datastr = ''
		flag = '99'#fail
	
	return datastr,flag,listname
	
def Writetxt(dirtxt,datastr):
	with open(dirtxt,'w') as f:
		f.write(datastr)
	
def play(config,dict_config):
	#dir = r'.\000.txt'
	dict = {} #配置文件字段除了要循环的配置字段
	data = {}#爬取json内容
	data1 = {}
	listname = []#爬取list内容
	nodelist =[]#要循环行的配置字段
	data['content'] = data1
	data1['crawl'] = listname
	#configlist,tasknumber= Config(webserviceurl)
	#print 11111,config
	s, taskid, client, configversion, configid, type,taskparam = config[0], config[1], config[2], config[3], config[4], config[5],config[6]
	
	dirtxt = (r'.\%sresult.txt') % configid
	dirhtml = (r'.\%ssourceHtml.html') % configid
	print ('s = %s') % s
	if '0' == s:
		raise IOError('task is None from webservice')
	
	dict['Timeout'] = (int)(s['pageRequest']['Timeout'])/1000
	dict['Url'] = s['pageRequest']['Url']
	dict['Method'] = s['pageRequest']['method']
	dict['payload'] = s['pageRequest']['DataTemplate']
	dict['Allowautoredirect'] = s['pageRequest']['allowAutoRedirect']
	#取总页数和当前页(因为有的任务只有总页数，没有当前页)
	dict['pagenumber'] = len(s["ExtractConfig"]["PathNode"][0]["DataNode"])
	dict['_Totalpage'] = s["ExtractConfig"]["PathNode"][0]["DataNode"][0]['region']
	dict['_TotalpageIsAttributeValue'] = s["ExtractConfig"]["PathNode"][0]["DataNode"][0]['IsAttributeValue']
	dict['_TotalpageFilter'] = s["ExtractConfig"]["PathNode"][0]["DataNode"][0]['Filter']
	dict['Totalpage'] = s["ExtractConfig"]["PathNode"][0]["DataNode"][0]['Comment']
	if dict['pagenumber'] == 2:
		dict['Currentpage'] = s["ExtractConfig"]["PathNode"][0]["DataNode"][1]['Comment']
		dict['_Currentpage'] = s["ExtractConfig"]["PathNode"][0]["DataNode"][1]['region']
		dict['_CurrentpageIsAttributeValue'] = s["ExtractConfig"]["PathNode"][0]["DataNode"][1]['IsAttributeValue']
		dict['_CurrentpageFilter'] = s["ExtractConfig"]["PathNode"][0]["DataNode"][1]['Filter']
	dict['Contenttype'] = s['pageRequest']['contentType']
	dict['Useragent'] = s['pageRequest']['UserAgent']
	dict['Accept'] = s['pageRequest']['accept']
	dict['Referer'] = s['pageRequest']['Referer']
		
	dict['DataNodenumber'] = len(s["ExtractConfig"]["PathNode"][0]["PathNode"][0]['PathNode'][0]['DataNode'])#要循环的列数
	dict['number'] = len(s["ExtractConfig"]["PathNode"][0]["PathNode"][0]['PathNode'][0]['region'])
	dict['Datanumber'] = len(s["ExtractConfig"]["PathNode"][0]["PathNode"][0]['PathNode'][0]['DataNode'][0])
	dict['forstart'] = s["ExtractConfig"]["PathNode"][0]["PathNode"][0]['PathNode'][0]['region']
	dict['forstart1'] = s["ExtractConfig"]["PathNode"][0]["PathNode"][0]['PathNode'][0]['DataNode'][0]['region']#要循环的行数
	dict['StartChildPostion'] = s["ExtractConfig"]["PathNode"][0]["PathNode"][0]['PathNode'][0]['StartChildPostion']
	dict['IntervalPosition'] = s["ExtractConfig"]["PathNode"][0]["PathNode"][0]['PathNode'][0]['IntervalPosition']
	dict['LastChildPostion'] = s["ExtractConfig"]["PathNode"][0]["PathNode"][0]['PathNode'][0]['LastChildPostion']
			
	#要循环的行的每行字段配置
	for i in range(dict['DataNodenumber']):
		dict_tmp = {}
		dict_tmp['region']=s["ExtractConfig"]["PathNode"][0]["PathNode"][0]['PathNode'][0]['DataNode'][i]['region']
		dict_tmp['order']=s["ExtractConfig"]["PathNode"][0]["PathNode"][0]['PathNode'][0]['DataNode'][i]['order']
		dict_tmp['standardName']=s["ExtractConfig"]["PathNode"][0]["PathNode"][0]['PathNode'][0]['DataNode'][i]['standardName']
		dict_tmp['ColumnType']=s["ExtractConfig"]["PathNode"][0]["PathNode"][0]['PathNode'][0]['DataNode'][i]['ColumnType']
		dict_tmp['Comment']=s["ExtractConfig"]["PathNode"][0]["PathNode"][0]['PathNode'][0]['DataNode'][i]['Comment']
		dict_tmp['Filter']=s["ExtractConfig"]["PathNode"][0]["PathNode"][0]['PathNode'][0]['DataNode'][i]['Filter']
		dict_tmp['IsAttributeValue']=s["ExtractConfig"]["PathNode"][0]["PathNode"][0]['PathNode'][0]['DataNode'][i]['IsAttributeValue']
		dict_tmp['ExtractorObject']=s["ExtractConfig"]["PathNode"][0]["PathNode"][0]['PathNode'][0]['DataNode'][i]['ExtractorObject']
		nodelist.append(dict_tmp)
	#print (' denumber=%s') %DataNodenumber
	#print ('nodelist=%s') %nodelist
	dict['headers'] = { 'Accept':dict['Accept'],
			'content-type': dict['Contenttype'],
			'User-Agent': dict['Useragent']
			}
		
	content = Crawl(dirhtml,dict)
	treelist = Tree(content,nodelist,listname,dict,data)
	datastr, flag, listname = treelist[0],treelist[1],treelist[2]
	Writetxt(dirtxt,datastr)
	
	pagename = dict['Url'] + '.txt'
	
	backwebservice(client,dict_config,taskid,flag,datastr,content,pagename,type,taskparam,configid)
	#time.sleep(10000)
def person(i,q,dict_config):
	import traceback 
	while True:  #这个人一直处与可以接活干的状态
	#print(q.get())
		#print "--------Thread",i,"do_job"
	#time.sleep(random.randint(1,5))#每个人干活的时间不一样，自然就会导致每个人分配的件数不同(这里是干活的地方)
		try:
			play(q.get(timeout = 10),dict_config)
		#play(q.get())
		except: 
			traceback.print_exc()#查看异常
		# finally:
		q.task_done()   #接到的活做完了，向上汇报
		
def main(configlist,q,dict_config):

	for x in configlist:
		q.put(x)

	#叫了5个线程去干活    
	#for i in xrange(len(configlist)):
	for i in xrange(int(dict_config['threads'])):
		worker=Thread(target=person,args=(i,q,dict_config))
		worker.setDaemon(True)
		worker.start()

	q.join()  #这5个人把1000件活都做完后，结束.

def readconfig(filename):
	import uuid
	config = ConfigObj(filename)
	dict_config = {}
	section = config['client'] 
	dict_config['GUID'] = section['GUID']
	if '' == dict_config['GUID'] : 
		section['GUID'] = uuid.uuid1()
		config.write()
	dict_config['threads'] = section['threads']
	dict_config['webserviceurl'] = section['webserviceurl']
	
	if '' == dict_config['threads']:
		raise 'please check clientconfig.ini'
	return dict_config

def download(url,configid):
	#url = 'http://web2.chinagrain.gov.cn/n16/n1122/n2082/n4683307.files/n4683275.rar' 
	r = requests.get(url) 
	time.sleep(3)
	dir1 = (r'.\%s.%s') % (configid,url.split('.')[-1])
	filename = ('%s.%s') % (configid,url.split('.')[-1])
	filetype = url.split('.')[-1]
	with open(dir1, "wb") as code:
		 code.write(r.content)
	return filename,filetype
if __name__  ==  '__main__':
	
	sys.modules['BeautifulSoup'] = bs4
	reload(sys)
	sys.setdefaultencoding('utf-8')
	filename=r'.\clientconfig.ini'
	# guiddir = r'.\clientconfig.txt'
	dict_config = readconfig(filename)#读取client配置文件
	configlist= Config( dict_config['webserviceurl'])#跟webservice服务端获取任务配置文件
	q=Queue()
	main(configlist,q,dict_config)
	

	

	
		
	
	