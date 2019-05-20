import sys
import getpass
from time import sleep
from selenium import webdriver
from bs4 import BeautifulSoup
import re

options = webdriver.FirefoxOptions()
# options.set_headless()
browser = webdriver.Firefox(firefox_options=options)

def get_chapters():
    global browser

    while True:
        try:
            father = browser.find_element_by_xpath('/html/body/div[5]/div[2]/div[4]/div/div/div/nav')
            return father.find_elements_by_tag_name('div')
        except:
            # print(e)
            pass
            # return elements[0].find_elements_by_xpath('./div')

def get_chapter(chapter_id):
    return get_chapters()[chapter_id]

def get_lessons(chapter):
    return chapter.find_elements_by_tag_name('li')

def study(lesson):
    global browser
    # global head
    head = '\r' + ' ' * 20 + '\r'

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
        sys.stderr.write('本节无视频\n')


class LoginInfo(object):
    def __init__(self, flag: bool, info: str):
        self.flag = flag
        self.info = info


def login():
    global browser

    while True:
        try:
            username_edit = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[1]/div/div[2]/form/div[1]/div[1]/input')
            pwd_edit = browser.find_element_by_xpath('/html/body/div[3]/div/div/div[1]/div/div[2]/form/div[1]/div[2]/input')
            username_edit.clear()
            pwd_edit.clear()
            break
        except:
            pass

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

        try:
            error = browser.find_element_by_class_name('error_message')
            if error.text:
                return LoginInfo(False, error.text)
            # hint(error.text)
            # break
        except:
            pass

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

def get_currnet_chapter():
    global browser

    while True:
        try:
            return browser.find_element_by_class_name('is-open')
            # return browser.find_element_by_css_selector("[class="]")
            
        except:
            pass
    

def hint(info):
    sys.stderr.write('%s\n' % str(info))

def switch_to_next_chapter():
    # currnet_chapter = get_currnet_chapter()
    chapters = get_chapters()
    for i, chapter in enumerate(chapters):
        if re.match('.*is-open.*', chapter.get_attribute('class')):
        # if chapter.get_attribute('class') == 'chapter is-open':
            if chapter is chapters[-1]:
                return False
            
            chapters[i + 1].find_element_by_tag_name('a').click()
            study(get_lessons(get_chapter(i + 1))[0])
            
            return True

def switch_to_next_lesson():
    # currnet_chapter = 
    # lessons = currnet_chapter.find_elements_by_tag_name('li')
    lessons = get_lessons(chapter=get_currnet_chapter())
    hint('len :%d' % len(lessons))
    # for i , lesson in zip(len(lessons), lessons):
    for i, lesson in enumerate(lessons):
        hint(lesson.get_attribute('class') + '233')
        if re.match('.*active.*', lesson.get_attribute('class')):
            if lesson is lessons[-1]:
                return switch_to_next_chapter()
            study(lesson=lessons[i + 1])
            return True

    raise Exception('switch lesson error')

def start_watch(start_lesson):
    # if start_lesson:
    study(lesson=start_lesson)
    while switch_to_next_lesson():
        pass

def from_last():
    global browser
    try:
        last = browser.find_element_by_xpath('/html/body/div[5]/div[2]/div[4]/div/section/p/a')
        flag = input('上次观看到 %s，是否要继续观看（是则输入y）？' % last.text)
        hint('flag: %s' % flag)
        if flag in ['y', 'Y', 'yes', 'YES', 'Yes']:
            print(233333)
            last.click()
            lesson = None
            while True:
                try:
                    lesson = browser.find_element_by_class_name('active ')
                    break
                except:
                    pass
            start_watch(lesson)

            return True
        else:
            # hint('失败')
            return False

    except:
        hint('失败')
        return False
        # pass

# def get_integer_input(l = 0, r):


def get_start_chapter_id(chapter_num):
    while True:
        chapter_id = int(input('请输入开始章节的编号：'))
        try:
            assert 0 <= chapter_id < chapter_num
            return chapter_id
        except:
            hint('章节编号不合法')

def get_start_lesson_id(lessons_num):
    while True:
        lesson_id = int(input('请输入开始课节的编号：'))
        try:
            assert 0 <= lesson_id < chapter_num
            return lesson_id
        except:
            hint('课节编号不合法')

        
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

        browser.find_element_by_xpath('/html/body/div[3]/div/div/div[2]').click()   # 关闭
        while True:
            try:
                browser.find_element_by_xpath('//*[@id="header_login"]').click()    # 打开登录
                break
            except:
                pass

    # enter specified course
    course = get_course()
    sys.stderr.write('进入课程：' + course.text + '\n')
    course.click()

    sleep(1)

    target_handle = browser.window_handles[1]
    browser.close()
    browser.switch_to.window(target_handle)
    # switch()

    # 等待章节自动展开
    get_chapters()

    if not from_last():
        browser.refresh()
        chapters = get_chapters()
        chapter_num = len(chapters)
        sleep(1)
        for i in range(chapter_num):
            sys.stderr.write('%d. %s\n' % (i, chapters[i].find_element_by_xpath('./h3').text))

        chapter_id = get_start_chapter_id(chapter_num=chapter_num)
        chapter = chapters[chapter_id]
        if chapter.get_attribute('class') != 'chapter is-open':
            chapter.find_element_by_tag_name('a').click()
            chapter = get_chapter(chapter_id=chapter_id)
        
        lessons = get_lessons(chapter)
        cnt = 0
        for i, lesson in enumerate(lessons):
            hint('%d. %s\n' % (i, lesson.text))
            cnt += 1

        lesson_id = get_start_lesson_id(cnt)
        start_watch(lessons[lesson_id])

    browser.close()
