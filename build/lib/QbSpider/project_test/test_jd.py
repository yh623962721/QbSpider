# coding=utf-8
# from selenium import webdriver
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
#
# dcap = dict(DesiredCapabilities.PHANTOMJS)
# dcap["phantomjs.page.settings.userAgent"] = (
#     "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36"
# )
#
# driver = webdriver.PhantomJS(executable_path='phantomjs.exe', desired_capabilities=dcap)
# driver.get('https://passport.jd.com/new/login.aspx')
# #cap_dict = driver.desired_capabilities
# # for key in cap_dict:
# #     print '%s: %s' % (key, cap_dict[key])
# # print driver.page_source
# driver.find_element_by_id("loginname").clear()
# driver.find_element_by_id("nloginpwd").clear()
# driver.find_element_by_id("loginname").send_keys("18519114597")
# driver.find_element_by_id("nloginpwd").send_keys("4148287549abc")
# driver.find_element_by_id("loginsubmit").click()
# #print driver.page_source
# print driver.get_cookies()
# print driver.current_url
#
# driver.quit()
if __name__ == "__main__":

    company = "hahahah投资顾问有限公司"

    company = company[0:company.index("投资顾问有限公司")] if "投资顾问有限公司" in company else company

    print company



