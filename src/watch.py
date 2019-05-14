import sys
import getpass
from time import sleep
from selenium import webdriver
from bs4 import BeautifulSoup

options = webdriver.FirefoxOptions()
# options.set_headless()
browser = webdriver.Firefox(firefox_options=options)

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

head = '\r' + ' ' * 20 + '\r'

def study(lesson):
	global browser
	global head

	element = lesson.find_element_by_xpath('./a')
	sys.stderr.write('进入课程：' + element.text + '\n')
	element.click()
	sleep(5)
	try:
		browser.find_element_by_class_name('xt_video_player_play_btn').click()
		sleep(5)
		while True:
			soup = BeautifulSoup(browser.page_source, 'html.parser')
			element = soup.find(class_='xt_video_player_current_time_display')
			span = element.find_all('span')
			cur, tot = span[0].text.strip(), span[1].text.strip()
			sys.stderr.write(head + cur + '/' + tot)
			if cur == tot:

				sys.stderr.write(head + '学习完成\n')
				break
			sys.stderr.flush()
	except:
		sys.stderr.write('本章无视频\n')


class LoginInfo(object):
	def __init__(self, flag: bool, info: str):
		self.flag = flag
		self.info = info


def login():
	global browser

	username_edit = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[1]/div/div[2]/form/div[1]/div[1]/input')
	pwd_edit = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[1]/div/div[2]/form/div[1]/div[2]/input')
	username_edit.clear()
	pwd_edit.clear()

	# 获取用户名
	while True:
		username_edit.clear()
		username = input('enter username: ')
		if not username:
			sys.stderr.write('用户名不能为空\n')
			continue
		username_edit.send_keys(username)
		break

	# 获取密码
	while True:
		pwd_edit.clear()
		password = getpass.getpass('enter password: ')
		if not password:
			sys.stderr.write('密码不能为空\n')
			continue
		pwd_edit.send_keys(password)
		break

	# 提交登录表单，保存当前url
	url = browser.current_url
	browser.find_element_by_xpath('//*[@id="loginSubmit"]').click() #click login button
	# sys.stderr.write(url)
	# 判断是否登录成功
	while True:
		if url != browser.current_url:
			print(233)
			return LoginInfo(True, '登录成功')

		# error = browser.find_element_by_class_name('error_message')
		error = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[1]/div/div[2]/form/div[3]/div/p')
		# print(244)
		if (error.text):
			return LoginInfo(False, error.text)

		sleep(1)

def get_course():
	global browser

	while True:
		courses = browser.find_elements_by_class_name('name_link')
		# courses = browser.find_element_by_xpath('//*[@id="courses_list"]')
		if courses:
			course_num = len(courses)
			for i in range(course_num):
				course = courses[i]
				sys.stderr.write('%d.%s\n' % (i, course.text))

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
	sys.stderr.write('打开浏览器\n')
	home = 'http://www.xuetangx.com/dashboard/course/'
	browser.get(home)

	# 登录
	while True:
		info = login()
		sys.stderr.write(info.info + '\n')
		if (info.flag):
			break

	# enter specified course
	course = get_course()
	sys.stderr.write('进入课程：' + course.text + '\n')
	course.click()
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
