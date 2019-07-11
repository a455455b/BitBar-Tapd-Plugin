#!/usr/local/bin/python3
# coding=utf-8

# <bitbar.title>Tapd All Undo Tasks Status</bitbar.title>
# <bitbar.version>v1.0</bitbar.version>
# <bitbar.author>Artillery</bitbar.author>
# <bitbar.author.github>a455455b</bitbar.author.github>
# <bitbar.desc>Show current status of Undo jobs on a Tapd instance. Clicks navigate to task Detail.</bitbar.desc>
# <bitbar.dependencies>python3,selenium,chromedriver</bitbar.dependencies>

from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.keys import Keys
import os, sys, stat, random, time, json, datetime
import re
import pickle

# Must config
user_email = u"XXXXXXXXXXXXX@banggood.com"
user_password = u"XXXXXXXXXXXXXXX"
# Optional Config
# 默认只查找了XXXXXXXX的任务列表
task_id = u"XXXXXXXXXX"
user_config_url = u"https://www.tapd.cn/" + task_id + "/prong/tasks?Model_name=Task&perpage=20&sort_name=status&order=ASC"


# simulate a UA
def get_ua():
    first_num = random.randint(55, 62)
    third_num = random.randint(0, 3200)
    fourth_num = random.randint(0, 140)
    os_type = ['(X11; Linux x86_64)', '(Macintosh; Intel Mac OS X 10_14_5)']
    chrome_version = 'Chrome/{}.0.{}.{}'.format(first_num, third_num,
                                                fourth_num)
    ua = ' '.join([
        'Mozilla/5.0',
        random.choice(os_type), 'AppleWebKit/537.36', '(KHTML, like Gecko)',
        chrome_version, 'Safari/537.36'
    ])
    return ua


# element is exist
def isElementExist(driver, element):
    flag = True
    try:
        driver.find_element_by_id(element)
        return flag
    except:
        flag = False
        return flag


color_map = {"未开始": "lightgray", "进行中": "#1B7837", "已完成": "yellow"}

# 创建chrome启动选项
chrome_options = ChromeOptions()

# 指定chrome启动类型为headless 并且禁用gpu
ua = get_ua()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_experimental_option('excludeSwitches',
                                       ['enable-automation'])
chrome_options.add_argument('user-agent=' + ua)

# 调用环境变量指定的chrome浏览器创建浏览器对象
# 步骤:
# 下载chromedriver安装包：https://sites.google.com/a/chromium.org/chromedriver/downloads
# unzip chromedriver_map.zip
# mv chromedriver /usr/local/bin
# cd /usr/local/bin && chmod a+x chromedirver
# /usr/local/bin/chromedriver

driver = Chrome(options=chrome_options,
                executable_path="/usr/local/bin/chromedriver")
driver.get(user_config_url)

cookie_path = os.path.dirname(os.path.realpath(__file__)) + '/cookie/'

if not os.path.exists(cookie_path):
    os.mkdir(cookie_path, mode=0o777)

tapdcookies_path = cookie_path + 'tapdcookies.pkl'
if os.path.exists(tapdcookies_path):
    cookies = pickle.load(open(tapdcookies_path, "rb"))
    for cookie in cookies:
        driver.add_cookie({
            'name': cookie["name"],
            'value': cookie["value"],
            'path': cookie["path"],
            'secure': True
        })
else:
    pickle.dump(driver.get_cookies(), open(tapdcookies_path, "wb"))

if isElementExist(driver, "username"):
    driver.find_element_by_id("username").send_keys(user_email)
    driver.find_element_by_id("password_input").send_keys(user_password)
    driver.find_element_by_id("tcloud_login_button").click()
    time.sleep(1)

arr = driver.find_elements_by_class_name("rowNOTdone")
undo_output = ''
doing_output = ''

for item in arr:
    id_Str = item.get_attribute('id')
    task_id = item.get_attribute("data-editable-params")
    text = json.loads(task_id)

    task_status_item = driver.find_element_by_xpath('//*[@id=\'task_' +
                                                    text['data[id]'] +
                                                    '_status\']')
    task_status_title = task_status_item.get_attribute("title")

    subItem = driver.find_element_by_xpath('//tr[@id=\'' + id_Str +
                                           '\']/td[4]')
    estimate_time = driver.find_element_by_xpath('//tr[@id=\'' + id_Str +
                                                 '\']/td[11]')

    estimate_title = estimate_time.get_attribute("data-editable-value")

    title = subItem.get_attribute("data-editable-value")
    title = re.sub('[’!"#$%\'()*+,-/:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~\s]+',
                   "", title)

    href = "https://www.tapd.cn/" + task_id + "/prong/tasks/view/" + text[
        'data[id]']

    if task_status_title == '进行中':
        if estimate_title and len(estimate_title) > 1:
            estimate_date = datetime.datetime.strptime(estimate_title,
                                                       '%Y-%m-%d').date()
            current_date = datetime.datetime.strptime(
                datetime.date.today().strftime("%Y-%m-%d"), '%Y-%m-%d').date()
            doing_output += '%s | color=%s href=%s\n' % (
                title, "red" if current_date > estimate_date else
                color_map[task_status_title], href)
        else:
            doing_output += '%s | color=%s href=%s\n' % (
                title, color_map[task_status_title], href)
    else:
        if estimate_title and len(estimate_title) > 1:
            estimate_date = datetime.datetime.strptime(estimate_title,
                                                       '%Y-%m-%d').date()
            current_date = datetime.datetime.strptime(
                datetime.date.today().strftime("%Y-%m-%d"), '%Y-%m-%d').date()
            undo_output += '%s | color=%s href=%s\n' % (
                title, "red" if current_date > estimate_date else
                color_map[task_status_title], href)
        else:
            undo_output += '%s | color=%s href=%s\n' % (
                title, color_map[task_status_title], href)

print('Tapd')
print('---')
print("进行中 | size=14 font=UbuntuMono color=orange")
print('---')
print(doing_output)
print('---')
print("未开始 | size=14 font=UbuntuMono color=orange")
print('---')
print(undo_output)

driver.close()