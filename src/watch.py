import sys
import getpass
from time import sleep
from selenium import webdriver

def get_chapters():
	global browser

	while True:
		elements = browser.find_elements_by_xpath('//nav[@aria-label="课程导航"]')
		if elements:
			return elements[0].find_elements_by_xpath('./div')

def get_chapter(chapter_id):
	return get_chapters()[chapter_id]

def get_lessons(chapter_id):
	return get_chapter(chapter_id).find_elements_by_xpath('./ul/li')

def get_lesson(chapter_id, lesson_id):
	return get_lessons(chapter_id)[lesson_id]

def study(lesson):
	global browser
	
	element = lesson.find_element_by_xpath('./a')
	sys.stderr.write('进入课程：' + element.text + '\n')
	element.click()
	sleep(5)
	try:
		browser.find_element_by_class_name('xt_video_player_play_btn').click()
		sleep(5)
		while True:
			try:
				browser.find_element_by_class_name('xt_video_player_play_btn_pause')
			except:
				sys.stderr.write('学习完成\n')
				break
	except:
		sys.stderr.write('本章无视频\n')


class LoginInfo(object):
	def __init__(self, flag: bool, info: str):
		self.flag = flag
		self.info = info
		

def login():
	global browser

	usernameEdit = browser.find_element_by_xpath('/html/body/div/div[2]/div/div[1]/div/form/div[1]/input')
	passwordEdit = browser.find_element_by_xpath('/html/body/div/div[2]/div/div[1]/div/form/div[2]/input')
	usernameEdit.clear()
	passwordEdit.clear()

	# 获取用户名
	while True:
		usernameEdit.clear()
		username = input('enter username: ')
		if not username:
			sys.stderr.write('用户名不能为空\n')
			continue
		usernameEdit.send_keys(username)
		break

	# 获取密码
	while True:
		passwordEdit.clear()
		password = getpass.getpass('enter password: ')
		if not password:
			sys.stderr.write('密码不能为空\n')
			continue
		passwordEdit.send_keys(password)
		break

	# 提交登录表单，保存当前url
	url = browser.current_url
	browser.find_element_by_xpath('//button[text()="立即登录"]').click() #click login button

	# 判断是否登录成功
	while True:
		if url != browser.current_url:
			return LoginInfo(True, '登录成功')
		
		error = browser.find_elements_by_class_name('help-block')
		if error:
			return LoginInfo(False, error[0].text)

def getCourse():
	global browser

	while True:
		courses = browser.find_elements_by_class_name('container-courselist--item')
		if courses:
			course_num = len(courses)
			for i in range(course_num):
				course = courses[i]
				sys.stderr.write(str(i) + '. ' + course.find_element_by_class_name('item-title').text + '\n')
			
			while True:
				course_id = input("输入观看的课程编号：")
				try:
					course_id = int(course_id)
					if course_id not in range(course_num):
						raise Exception('输入编号不合法\n')
				except Exception as e:
					sys.stderr.write(str(e) + '\n')
					continue
				
				return courses[course_id]

def switch():
	global browser

	while True:
		if len(browser.window_handles) == 2:
			browser.close()
			browser.switch_to_window(browser.window_handles[0])
			return

if __name__ == '__main__':
	options = webdriver.FirefoxOptions()
	# options.set_headless()
	browser = webdriver.Firefox(firefox_options=options)
	sys.stderr.write('打开浏览器\n')
	home = 'http://tsinghua.xuetangx.com'
	browser.get(home)
	browser.find_element_by_xpath('//a[text()="登录"]').click() #enter login page

	# 登录
	while True:
		info = login()
		sys.stderr.write(info.info + '\n')
		if (info.flag):
			break

	# enter specified course
	course = getCourse()
	course.find_element_by_xpath('.//a[text()="继续学习"]').click()
	sys.stderr.write('进入课程：' + course.find_element_by_class_name('item-title').text + '\n')
	switch()

	# 等待章节自动展开
	while True:
		if get_chapters():
			break
	
	chapters = get_chapters()
	chapter_num = len(chapters)
	for i in range(chapter_num):
		sys.stderr.write(str(i) + '. ' + chapters[i].find_element_by_xpath('./h3').text + '\n')

	chapter_id = int(input('请输入开始章节的编号：'))

	for i in range(chapter_id, chapter_num):
		chapter = get_chapter(chapter_id=i)
		if chapter.get_attribute('class') != 'chapter is-open':
			chapter.find_element_by_xpath('./h3/a').click()
			chapter = get_chapter(chapter_id=i)
		sys.stderr.write("开始学习章节：" + chapter.find_element_by_xpath('./h3/a').text + '\n')

		lesson_num = len(get_lessons(chapter_id=i))
		for j in range(lesson_num):
			lesson = get_lesson(chapter_id=i, lesson_id=j)
			study(lesson)
	browser.close()