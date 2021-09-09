# coding:utf-8
# 导入类库
import re
import requests
import sys
import io
import math
import time
import pandas as pd  # 按列存放
from selenium import webdriver

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='gb18030')

# 初始化浏览器
driver = webdriver.Chrome()
# driver.maximize_window()	#窗口最大化
# driver.implicitly_wait(10)	#隐式等待10s查询元素

# 首页的请求头
headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"}
# 首页的地址
url = 'https://store.to8to.com/?groupId=&subGroupId=&groupIds=&page=1'

# 打开首页
driver.get(url)

# 一级分类的数量
filteritem_first_num = len(driver.find_elements_by_xpath('/html/body/div[2]/div[1]/div[1]/dl[1]/dd/a'))
print("一级分类的数量是", filteritem_first_num)

# 初始化列表
shopname_list = []
shoptype_list = []
sname_list = []
sprice_list = []

# 遍历一级分类
for i in range(1, filteritem_first_num):
    # 切换到细化的分类
    print("分类：", i)
    element = driver.find_element_by_xpath('/html/body/div[2]/div[1]/div[1]/dl[1]/dd[1]/a[' + str(i + 1) + ']')
    driver.execute_script("arguments[0].click();", element)
    # 获取当前页面的URL
    cur_url = driver.current_url
    # 利用requests获取页面响应隐藏的内容
    response = requests.get(cur_url, headers=headers).text
    # 定义正则：分类下商铺的总数
    total_shop = re.compile(r'<em>共有<b>(.*?)</b>条</em>')
    # 从响应数据中匹配数据（匹配结果为列表类型）
    total_shop = total_shop.findall(response)
    # 判断当前分类下店铺数量是否超过一页
    if total_shop:
        print("当前分类下店铺数量超过一页！")
        print("分类下商铺的总数:", total_shop[0])
        # 当前分类下总的页数，备注：每页最多的商铺数量是10--将总商铺数量由字符串转换为整数
        totalpage = math.ceil(int(total_shop[0]) / 10)
        print("当前分类下总的页数:", totalpage)
    else:
        totalpage = 1
        print("当前只有一页，无需翻页处理")

    for next_page in range(0, totalpage):
        # 获取当前页所有店铺的数量
        shop_num = len(driver.find_elements_by_class_name('shop-item'))
        print("店铺的数量是：", shop_num)
        for i in range(0, 1):
            # 点击店铺链接，进入商铺明细页面
            driver.find_element_by_xpath(
                '/html/body/div[2]/div[1]/div[3]/div[1]/div[' + str(i + 1) + ']/a/div[2]/div[1]/span[1]').click()
            # 获取商铺名称
            shop_name = driver.find_element_by_xpath(
                '/html/body/div[2]/div[1]/div[3]/div[1]/div[' + str(i + 1) + ']/a/div[2]/div[1]/span[1]').text
            # 打印商铺名称
            print("该商铺的名称是：", shop_name)
            shopname_list.append(shop_name)
            # 获取该商铺的分类
            try:
                shop_type = driver.find_element_by_xpath(
                    '/html/body/div[2]/div[1]/div[3]/div[1]/div[' + str(i + 1) + ']/a/div[2]/div[1]/span[2]').text
                # 打印商铺类型
                print("该商铺的分类是：", shop_type)
            except:
                shop_type = '空'
                print("该商铺的没有分类", shop_type)
            shoptype_list.append(shop_type)

            # 获取当前所有的窗口
            windows = driver.window_handles
            # # 打印页面句柄
            # print("获取当前所有窗口的句柄：", windows)
            # # 打印当前句柄
            # print("当前句柄是：", driver.current_window_handle)
            # 页面切换--切换到指定的窗口
            time.sleep(1)
            driver.switch_to.window(windows[-1])

            # 查看该店铺下是否有商品
            try:
                driver.find_elements_by_css_selector('.goods-item')
                # print("切换页面后的当前句柄是：", driver.current_window_handle)
                # 点击查看一个商铺的全部商品信息
                try:
                    driver.find_element_by_xpath('//*[@id="recommendGoods"]/div[1]/span[2]').click()
                except:
                    print("该商铺商品数量未超过4个！")

                # 获取商铺的所有商品总数量
                goods_num = len(driver.find_elements_by_class_name('goods-item'))
                print("商品的数量是：", goods_num)

                for i in range(0, 1):
                    # 获取商品名称
                    sname = driver.find_element_by_xpath(
                        '//*[@id="recommendGoods"]/div[2]/div[' + str(i + 1) + ']/a/div[2]/h3').text
                    print(sname)
                    sname_list.append(sname)
                    # 获取商品价格
                    sprice = driver.find_element_by_xpath(
                        '//*[@id="recommendGoods"]/div[2]/div[' + str(i + 1) + ']/a/div[2]/div/div[1]').text
                    sprice = sprice.encode('gbk', 'ignore').decode('gbk')
                    print(sprice)
                    sprice_list.append(sprice)
                    time.sleep(1)  # 等待2s，方便观看
            except:
                goods_num = 0
                sname_list.append('空')
                sprice_list.append('空')
                print("该商铺商品数量为0！", goods_num)
            # 关闭当前页面
            driver.close()
            # 切回原来的窗口
            driver.switch_to.window(windows[0])
            print("切回原来的窗口，当前句柄是：", driver.current_window_handle)
            time.sleep(1)
        try:
            driver.find_element_by_css_selector("#nextpageid").click()
        except:
            print("当前是最后一页，无需翻页处理")

    # 定义输入数据
    df1 = pd.DataFrame({'商铺名称': shopname_list, '分类': shoptype_list, '商品名称': sname_list, '商品价格': sprice_list})
    # 写入Excel文件
    df1.to_excel('test_data.xlsx')
    time.sleep(1)  # 等待2s，方便观看

# 退出驱动并关闭所有关联的窗口
driver.quit()
