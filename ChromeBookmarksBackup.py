#coding:utf-8
'''
背景：2018-01-24，电脑出现故障，启动蓝屏，导致无法开机启动，只好重置电脑，重置后chrome的书签全部没有了，感觉很可惜，
	之前添加了许多很有用的网页全部都没有了
目的：在计算机后台运行，定时检查chorme书签是否有更新，并及时备份到非系统盘，以防再次发生意外
所用包：os

注意：代码文件不要删除，第二，备份文件地址之前写在与代码文件同级目录下，结果发现文件执行目录不是py文件存放目录，无法使用相对目录，当然也可以存放在相同目录下然后再查找一次也可以
'''



import os
import sys
import time
import win32api
import win32event
import win32service
import win32serviceutil
import servicemanager
import traceback
import os
import re
import shutil
import datetime

log_path = r'F:\备忘\浏览器书签备份\脚本\log.txt'
backup_file_path = r'F:\备忘\浏览器书签备份\脚本\备份数据'

def log(message):
	with open(log_path,'a',encoding='utf-8') as f:
		f.write(message+'\n')


class ChromeBookmarksBackup(win32serviceutil.ServiceFramework):

	_svc_name_ = '浏览器书签备份'
	_svc_display_name_ = '浏览器书签备份'
	_svc_description_ = 'bookmarks backup'

	# def __init__(self, args):
	# 	win32serviceutil.ServiceFramework.__init__(self, args)
	# 	self.stop_event = win32event.CreateEvent(None,0,0,None)
	# 	log('init')



	def findfile(self,backup_dir):
		log('findfile begin')
		#获取bookmark文件路径
		mark_list = []
		for root,dirs,files in os.walk('c:\\'):
			if 'Bookmarks' in files:
				for f in files:
					if 'Bookmarks' in f:
						mark_list.append(os.path.join(root,f))
		#根据路径备份文件
		for pt in mark_list:
			if not os.path.isfile(pt):							#判断是否为文件
				continue
			if not os.path.exists(backup_dir):					#判断提供的备份文件夹是否存在
				os.mkdir(backup_dir)

			size = os.path.getsize(pt)							#获取文件大小用来和已备份的文件做比较
			print(size)
			file_new_name = re.sub('[\\\.:\s]','_',pt)			#将待备份文件路径替换特殊符号后作为备份文件名
			print(file_new_name)
			backup_file_path = os.path.join(backup_dir,file_new_name)
			if not os.path.exists(backup_file_path):				#如果备份文件夹下没有备份过此文件，则直接复制备份
				shutil.copyfile(pt,backup_file_path)
				continue
			backup_size = os.path.getsize(backup_file_path)
			types = isinstance(backup_size,int)
			print('*'*10)
			print(types)
			if size < backup_size:								#如果待备份的文件小于备份文件，则将已备份的文件备份，然后重新备份
				print('#'*10)
				time_str = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
				print(''.join([backup_file_path,str(time_str)]))

				shutil.copyfile(backup_file_path,''.join([backup_file_path,str(time_str)]))
				shutil.copyfile(pt,backup_file_path)
			else:
				shutil.copyfile(pt,backup_file_path)
		log('findfile end')

	def start(self):
		
		self.findfile(backup_file_path)
		log('start end')

	def SvcDoRun(self):
		while 1:
			log('SvcDoRun begin')
			self.start()
			time.sleep(18000)

	def SvcStop(self):
		self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
		win32event.SetEvent(self.stop_event)




if __name__ == '__main__':
	log('##### begin')
	if len(sys.argv) == 1:
		try:
			log('***** begin')
			evtsrc_dll = os.path.abspath(servicemanager.__file__)
			servicemanager.PrepareToHostSingle(ChromeBookmarksBackup)
			servicemanager.Initialize('ChromeBookmarksBackup',evtsrc_dll)
			servicemanager.StartServiceCtrlDispatcher()
		except win32service.error as e:
			print(e)
			log(str(e))
			traceback.print_exc()
	else:
		win32serviceutil.HandleCommandLine(ChromeBookmarksBackup)



