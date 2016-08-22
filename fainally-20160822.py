# -*- coding: utf-8' -*-
"""
Created on  2016
@author:jinchener
initial version from yiyuezhuo
"""
import requests
import time
import json
import os
import numpy as np
import pickle
import csv
import datetime
import xlwt
from xlsxwriter.workbook import Workbook
import shutil

import sys
reload(sys)
sys.setdefaultencoding('utf-8')




class TreeNode(object):  #数据目录获取
    url = 'http://data.stats.gov.cn/easyquery.htm'

    def __init__(self, iid='zb', name='zb', data_me=None, dbcodename='hgjd'):
        global dbcodenames #年度、月度、季度、分省、主要城市数据类型
        self.id = iid  #目录id
        self.name = name #获取方式：指标、地区
        self.data_me = data_me  # Only leaf need this field
        self.data = None
        self.children = []
        self.leaf = None
        self.dbcode = dbcodenames

    def get(self, force=False, verbose=True):
        params = {'id': 'zb', 'dbcode': self.dbcode,
                  'name': 'zb', 'wdcode': 'zb', 'm': 'getTree'}
        if verbose:
            print 'getting', self.id, self.name
        if force or self.data == None:
            params = params.copy()  # TreeNode.
            params['id'] = self.id
            params['dbcode'] = self.dbcode
            res = requests.get(TreeNode.url, params=params)
            self.data = res.json()
            for data in self.data:
                self.children.append(TreeNode(iid=data['id'], name=data['name'],
                                              data_me=data))
            self.leaf = len(self.children) == 0

    def get_recur(self, force=False, verbose=True):
        if force or (self.data == None):
            self.get(verbose=verbose)
            for child in self.children:
                child.get_recur()

    def to_dict(self):
        children = [child.to_dict() for child in self.children]
        rd = self.data.copy()
        rd['children'] = children
        return rd

    def display(self, level=0):
        print ' ' * level + self.name + ' ' + self.id
        for child in self.children:
            child.display(level + 1)

    def get_all_pair(self):
        if self.leaf:
            return [(self.id, self.name)]
        else:
            rl = []
            for child in self.children:
                rl.extend(child.get_all_pair())
            return rl


class Downloader(object): #请求数据json文件并存储

    def __init__(self, tree, raw_root='raw', date='1978-2014', dbcodename='hgjd'):
        global dbcodenames
        self.tree = tree
        self.map_name = dict(tree.get_all_pair())
        self.map_json = {}
        self.raw_root = raw_root
        self.date = date
        self.dbcode = dbcodenames
        if (self.dbcode == 'hgyd') or (self.dbcode == 'hgjd') or (self.dbcode == 'hgnd'):
            self.wds = []
        else:
            self.wds = [{"wdcode": "reg", "valuecode": "110000"}]

    def get_params(self, valuecode): #年度、月度、季度数据请求参数格式
        params = {'m': 'QueryData', 'dbcode': self.dbcode,
                  'rowcode': 'zb', 'colcode': 'sj',
                  'wds': self.wds,
                  'dfwds': [{'wdcode': 'zb', 'valuecode': None},
                            {'wdcode': 'sj', 'valuecode': self.date}],
                  'k1': None}
        # requests can't deal tuple,list,dict correctly,I transform
        # them to string and replace ' -> " to solve it
        # Shocked!requests can't handle unicode properly
        params['dfwds'][0]['valuecode'] = str(valuecode)
        params['k1'] = int(time.time() * 1000)
        rp = {key: str(value).replace("'", '"')
              for key, value in params.items()}
        return rp

    def LongToInt(self, value):
        assert isinstance(value, (int, long))
        return int(value & sys.maxint)

    def get_paramsmul(self, valuecode):  #分省或主要城市数据请求参数格式
        params = {'m': 'QueryData', 'dbcode': self.dbcode,
                  'rowcode': 'zb', 'colcode': 'sj',
                  'wds': self.wds,
                  'dfwds': [{'wdcode': 'zb', 'valuecode': None},
                            {'wdcode': 'sj', 'valuecode': self.date}],
                  'k1': None}
        if (self.dbcode == 'fsyd') or (self.dbcode == 'fsjd') or (self.dbcode == 'fsnd'):
            dowdloadd = {"110000": "北京市", "120000": "天津市", "130000": "河北省", "140000": "山西省", "150000": "内蒙古自治区",
                         "210000": "辽宁省", "220000": "吉林省", "230000": "黑龙江省", "310000": "上海市", "320000": "江苏省",
                         "330000": "浙江省", "340000": "安徽省", "350000": "福建省", "360000": "江西省", "370000": "山东省",
                         "410000": "河南省", "420000": "湖北省", "430000": "湖南省", "440000": "广东省", "450000": "广西壮族自治区",
                         "460000": "海南省", "500000": "重庆市", "510000": "四川省", "520000": "贵州省", "530000": "云南省",
                         "540000": "西藏自治区", "610000": "陕西省", "620000": "甘肃省", "630000": "青海省", "640000": "宁夏回族自治区",
                         "650000": "新疆维吾尔自治区"}
        else:
            dowdloadd = {"110000": "北京", "120000": "天津", "130100": "石家庄", "130200": "唐山", "130300": "秦皇岛",
                         "140100": "太原", "150100": "呼和浩特", "150200": "包头", "210100": "沈阳", "210200": "大连",
                         "210600": "丹东", "210700": "锦州", "220100": "长春", "220200": "吉林", "230100": "哈尔滨",
                         "231000": "牡丹江", "310000": "上海", "320100": "南京", "320200": "无锡", "320300": "徐州",
                         "321000": "扬州", "330100": "杭州", "330200": "宁波", "330300": "温州", "330700": "金华", "340100": "合肥",
                         "340300": "蚌埠", "340800": "安庆", "350100": "福州", "350200": "厦门", "350500": "泉州", "360100": "南昌",
                         "360400": "九江", "360700": "赣州", "370100": "济南", "370200": "青岛", "370600": "烟台", "370800": "济宁",
                         "410100": "郑州", "410300": "洛阳", "410400": "平顶山", "420100": "武汉", "420500": "宜昌",
                         "420600": "襄樊", "430100": "长沙", "430600": "岳阳", "430700": "常德", "440100": "广州", "440200": "韶关",
                         "440300": "深圳", "440800": "湛江", "441300": "惠州", "450100": "南宁", "450300": "桂林", "450500": "北海",
                         "460100": "海口", "460200": "三亚", "500000": "重庆", "510100": "成都", "510500": "泸州", "511300": "南充",
                         "520100": "贵阳", "520300": "遵义", "530100": "昆明", "532900": "大理", "610100": "西安", "620100": "兰州",
                         "630100": "西宁", "640100": "银川", "650100": "乌鲁木齐"}

        # requests can't deal tuple,list,dict correctly,I transform
        # them to string and replace ' -> " to solve it
        # Shocked!requests can't handle unicode properly
        params['dfwds'][0]['valuecode'] = str(valuecode)

        rp = {key: str(value).replace("'", '"')
              for key, value in params.items()}
        rpl = []
        for i in dowdloadd.keys():
            intl = self.LongToInt(int(time.time() * 1000))
            params['k1'] = intl
            # print type( int(time.time() * 1000))
            # print type(params['k1'])
            params['wds'][0]['valuecode'] = i
            rp = {key: str(value).replace("'", '"')
                  for key, value in params.items()}

            # print rp
            rpl.append(rp)

        return rpl

    def download_once(self, valuecode, to_json=False):  #年度、月度、季度数据请求
        url = 'http://data.stats.gov.cn/easyquery.htm'
        params = self.get_params(valuecode)
        res = requests.get(url, params=params)
        if to_json:
            return res.json()
        else:
            return res.content

    def download_multi(self, valuecode, to_json=False):  #分省或主要城市数据请求
        url = 'http://data.stats.gov.cn/easyquery.htm'
        paramsl = self.get_paramsmul(valuecode)
        res = []
        for params in paramsl:
            rest = requests.get(url, params=params)
            res.append(rest)
        if to_json:
            result = []
            for i in res:
                result.append(i.json())
            return result
        else:
            result = []
            for i in res:
                result.append(i.content)
            return result

    def valuecode_path(self, valuecode):
        return os.path.join(self.raw_root, valuecode)

    def cache(self, valuecode, content): #年度、月度、季度数据写入文件
        f = open(self.valuecode_path(valuecode), 'wb')
        f.write(content)
        f.close()

    def cachell(self, valuecode, content):  #分省、主要城市数据拼接并写入文件
        f = open(self.valuecode_path(valuecode), 'wb')
        f.write('{\"data\":[')
        for i in range(len(content)):
            if i != (len(content) - 1):
                f.write(content[i])
                f.write(',')
            else:
                f.write(content[i])
        f.write(']}')
        f.close()

    def is_exists(self, valuecode, to_json=False):
        if to_json:
            return self.map_json.has_key(valuecode)
        else:
            path = os.path.join(self.raw_root, valuecode)
            return os.path.isfile(path)

    def download(self, verbose=True, to_json=False):
        length = len(self.map_name)
        for index, valuecode in enumerate(self.map_name.keys()):
            if verbose:
                print 'get data', valuecode, self.map_name[valuecode].replace('/', '~'), 'clear', float(index) / length
            if not self.is_exists(valuecode, to_json=to_json):
                if (self.dbcode == 'hgyd') or (self.dbcode == 'hgjd') or (self.dbcode == 'hgnd'):  #年度、月度、季度数据请求
                    res_obj = self.download_once(valuecode, to_json=to_json)
                    if to_json:
                        self.map_json[valuecode] = res_obj
                    else:
                        self.cache(valuecode, res_obj)
                else:  #分省、主要城市数据请求
                    res_obj = self.download_multi(valuecode, to_json=to_json)
                    if to_json:
                        self.map_json[valuecode] = res_obj
                    else:
                        self.cachell(valuecode, res_obj)


class Document(object): #解析json数据文件并解析

    def __init__(self, raw_root='raw', dbcodename='hgjd'):
        global dbcodenames
        self.raw_root = raw_root
        self.cellnum = int(0)
        self.dbcode = dbcodenames

    def get(self, name):
        path = os.path.join(self.raw_root, name)
        with open(path, 'rb') as f:
            content = f.read()
        return content

    def get_json(self, name):
        return json.loads(self.get(name))

    def json_to_dataframe(self, dic, origin_code=True):  #年度、月度、季度数据json格式转换
        dic = json.loads(dic)
        try:
            assert dic['returncode'] == 200
        except AssertionError, args:
            print '%s:%s' % (args.__class__.__name__, args)
        returndata = dic['returndata']
        datanodes, wdnodes = returndata['datanodes'], returndata['wdnodes']
        if not origin_code:  # parse wdnodes for transform that
            wd = {}
            tmpd = {}
            for ww in wdnodes[0]['nodes']:
                if ww['unit']:
                    tmpd[ww['code']] = (
                        ww['cname'] + '(' + ww['unit'] + ')'), (ww['unit'])
                else:
                    tmpd[ww['code']] = ww['cname'], ''
            wd[wdnodes[0]['wdcode']] = tmpd
            wd[wdnodes[1]['wdcode']] = {ww['code']: (
                ww['cname']) for ww in wdnodes[1]['nodes']}
            zb_wd, sj_wd = wd['zb'], wd['sj']
        rd = {}
        for node in datanodes:
            sd = {w['wdcode']: w['valuecode'] for w in node['wds']}
            zb, sj = sd['zb'], sd['sj']
            if not origin_code:
                zb, sj = zb_wd[zb], sj_wd[sj]
            rd[(zb, sj)] = node['data']['strdata'] if node[
                'data']['hasdata'] else np.NaN
        return rd

    def json_to_dataframell(self, dic, origin_code=True):   #分省、主要城市数据解析json格式转换
        datalist = json.loads(dic.replace("\'", '"'))['data']
        rdl = []
        for dic in datalist:
            try:
                assert dic['returncode'] == 200
            except AssertionError, args:
                print '%s:%s' % (args.__class__.__name__, args)

            returndata = dic['returndata']
            datanodes, wdnodes = returndata['datanodes'], returndata['wdnodes']
            if wdnodes[1]['nodes'][0]:
                if not origin_code:  # parse wdnodes for transform that
                    wd = {}
                    tmpd = {}
                    for ww in wdnodes[0]['nodes']:
                        if ww['unit']:
                            tmpd[ww['code']] = (
                                                   ww['cname'] + '(' + ww['unit'] + ')'), (ww['unit'])
                        else:
                            tmpd[ww['code']] = ww['cname'], ''
                    wd[wdnodes[0]['wdcode']] = tmpd
                    wd[wdnodes[1]['wdcode']] = {ww['code']: (
                        ww['cname']) for ww in wdnodes[1]['nodes']}
                    wd[wdnodes[2]['wdcode']] = {ww['code']: (
                        ww['cname']) for ww in wdnodes[2]['nodes']}
                    zb_wd, sj_wd, reg_wd = wd['zb'], wd['sj'], wd['reg']
                rd = {}

                for node in datanodes:
                    sd = {w['wdcode']: w['valuecode'] for w in node['wds']}
                    zb, sj, reg = sd['zb'], sd['sj'], sd['reg']
                    if not origin_code:
                        zb, sj, reg = zb_wd[zb], sj_wd[sj], reg_wd[reg]
                    rd[(zb, sj, reg)] = node['data']['strdata'] if node[
                        'data']['hasdata'] else np.NaN
                    if rd not in rdl:
                        rdl.append(rd)
        return rdl

    def get_dataframe(self, name, origin_code=False):
        return self.json_to_dataframe(self.get(name), origin_code=False)

    def get_dataframell(self, name, origin_code=False):
        return self.json_to_dataframell(self.get(name), origin_code=False)

    def iter_tree(self, tree, path=('zb',), origin_dir=False):
        yield path, tree
        for node in tree.children:
            # print node
            newpath = path + ((node.id,) if origin_dir else (node.name,))
            for r in self.iter_tree(node, path=newpath):
                yield r

    def nametol(self, pathtmp):  #数据目录分级拆分
        namel = pathtmp.split('--')
        while len(namel) < 3:
            namel.append('')
        return namel

    def cvsstran2xls(self, filename):
        workbook = Workbook(os.path.splitext(filename)[0] + '.xlsx')
        worksheet = workbook.add_worksheet()
        with open(filename, 'rb') as f:
            reader = csv.reader(f)
            for r, row in enumerate(reader):
                for c, col in enumerate(row):
                    worksheet.write(r, c, col)
        workbook.close()
        print os.path.splitext(filename)[0] + '.xls', 'OK'

    def cvstran2xlxs(self, filename):
        with open(filename, 'rb') as f:
            reader = csv.reader(f)
            cvscontent = []
            rownum=0
            for row in reader:
                rownum=rownum+1
                print rownum
                try:
                    cvscontent.append([x.decode('utf-8') for x in row])
                except:
                    cvscontent.append([x.decode('gbk') for x in row])
        file = xlwt.Workbook()
        table = file.add_sheet('sheet1', cell_overwrite_ok=True)
        for row in range(len(cvscontent)):
            for col in range(len(cvscontent[row])):
                table.write(row, col, cvscontent[row][col])
        file.save(os.path.splitext(filename)[0] + '.xls')
        print os.path.splitext(filename)[0] + '.xls', 'OK'



    def cvstran2xls(self, filename):  #将csv文件转换为xlsx
        with open(filename, 'rb') as f:
            reader = csv.reader(f)
            cvscontent = []
            #rownum=0
            for row in reader:
                #rownum = rownum + 1
                #print rownum
                # print len(cvscontent)
                try:
                    cvscontent.append([x.decode('utf-8') for x in row])
                    #print '1',len(cvscontent)
                except:
                    cvscontent.append([x.decode('gbk') for x in row])
                    #print '0',len(cvscontent)
                '''
                else:
                    cvscontent.append(row)
                    print '3', len(cvscontent)
                '''


        workbook = Workbook(os.path.splitext(filename)[0] + '.xlsx')
        worksheet = workbook.add_worksheet()
        for row in range(len(cvscontent)):
            for col in range(len(cvscontent[row])):
                worksheet.write(row, col, cvscontent[row][col])
        workbook.close()
        print os.path.splitext(filename)[0] + '.xlsx', 'OK'





    def dictran2ll(self, dic, path):  #提取数据dict整理成list
        df = dic
        pathd = path
        datatotal = []
        for j in df.keys():
            dataname = j[0][0]
            unit = j[0][1]
            time = j[1]
            if df[j] != df[j]:#json中的null替换为'-'
                data = '-'
            else:
                data = df[j]
            namell = self.nametol(pathd)
            title = time + '_' + '_'.join(namell) + '_' + dataname
            if self.dbcode == 'hgyd':
                datatype = u'月度数据'
                timetype = u'月度'
                area = u'国家'
                locate = u'中国'
            elif self.dbcode == 'hgjd':
                datatype = u'季度数据'
                timetype = u'季度'
                area = u'国家'
                locate = u'中国'
            elif self.dbcode == 'hgnd':
                datatype = u'年度数据'
                timetype = u'年度'
                area = u'国家'
                locate = u'中国'
            elif self.dbcode == 'fsyd':
                datatype = u'分省月度数据'
                timetype = u'月度'
                area = u'省'
                locate = j[2]
            elif self.dbcode == 'fsjd':
                datatype = u'分省季度数据'
                timetype = u'季度'
                area = u'省'
                locate = j[2]
            elif self.dbcode == 'fsnd':
                datatype = u'分省年度数据'
                timetype = u'年度'
                area = u'省'
                locate = j[2]
            elif self.dbcode == 'csnd':
                datatype = u'主要城市年度价格'
                timetype = u'年度'
                area = u'市'
                locate = j[2]
            elif self.dbcode == 'csyd':
                datatype = u'主要城市月度价格'
                timetype = u'月度'
                area = u'市'
                locate = j[2]

            if (not unit) or (len(unit)<1):
                unit='-'


            datalist = ['', title, title, u'31', '', '', u'统计局', datatype, area, locate, namell[0],
                        namell[1], namell[2], dataname, unit, timetype, time, data]
            #datalistt = [unicode(s).encode("gb2312")  for s in datalist]
            datalistt=datalist
            datatotal.append(datalistt)
        return datatotal

    def to_file_all(self, tree, filename='result.csv', encoding='utf8'):  #数据文件解析写入到csv文件
        csvfile = file(filename, 'wb')
        writer = csv.writer(csvfile, dialect='excel')
        titlel = [u'url', u'title', u'format_content', u'source_typet', u'release_date', u'download_date', u'media_name', u'data_type', u'prefecture', u'area',
                  u'index_type_total', u'index_type_classify', u'index_type_subclass', u'index_name', u'unit', u'calculation_freq', u'calculation_date', u'index_data']
        writer.writerow(titlel)
        csvfile.close()
        self.cellnum = self.cellnum + 1
        for path, node in self.iter_tree(tree):
            if node.leaf:
                pathd = '--'.join(path[1:])
                if (self.dbcode == 'hgyd') or (self.dbcode == 'hgjd')  or (self.dbcode == 'hgnd'):  #年度、月度、季度数据解析
                    try:
                        df = self.get_dataframe(node.id)
                    except ValueError:
                        print node.id
                        raw_input()
                    csvfile = file(filename, 'ab+')
                    writer = csv.writer(csvfile, dialect='excel')
                    data = self.dictran2ll(df, pathd)
                    writer.writerows(data)
                    self.cellnum = self.cellnum + len(data)
                    print 'lines done number:',self.cellnum
                    csvfile.close()

                else:  #分省、主要城市数据解析
                    dfl = self.get_dataframell(node.id)
                    csvfile = file(filename, 'ab+')
                    writer = csv.writer(csvfile)
                    for df in dfl:
                        data = self.dictran2ll(df, pathd)
                        writer.writerows(data)
                        self.cellnum = self.cellnum + len(data)
                        print'lines done number:', self.cellnum
                    csvfile.close()

        self.cvstran2xls(filename)


if __name__ == "__main__":

    temp = u'国家数据(国家统计局)抓取器加强版/This toolkit could automatically download data from National data base. '
    print temp.encode('gb18030')
    querytype = ''
    while not(querytype == '1' or querytype == '2' or querytype == '3' or querytype == '4' or querytype == '5' or querytype == '6' or querytype == '7' or querytype == '8'):
        temp = u'请输入查询数据种类/Please input the type of query:\n1--月度数据/monthly  2--季度数据/seasonly  3--分省月度/promonthly  4--分省季度/proseasonly  5--主要城市月度价格/maincity  6--年度数据/yearly   7--分省年度/proyearly   8--主要城市年度价格/maincityyear'
        print temp.encode('gb18030')
        querytype = raw_input()
    querystarttime = ''
    if (querytype == '1' or querytype == '3' or querytype == '5'):
        while not len(querystarttime) == 6:
            temp = u'请输入查询的起始年月（六位数，形如201601）/Please input the start year of query (6 digits):'
            print temp.encode('gb18030')
            querystarttime = raw_input()
        queryendtime = 'x'
        while not (len(queryendtime) == 6 or len(queryendtime) == 0):
            temp = u'请输入查询的结束年月（六位数，空输入表示最新的月份）/Please input the end year of query (4 digits,Empty Input for the latest year):'
            print temp.encode('gb18030')
            queryendtime = raw_input()
            today = datetime.date.today()
            if not len(queryendtime) == 6:
                queryendtime = today.strftime('%Y%m%d')[:-2]
            else:
                pass

    else:
        while not len(querystarttime) == 4:
            temp = u'请输入查询的起始年份（四位数，形如2016）/Please input the start year of query (4 digits):'
            print temp.encode('gb18030')
            querystarttime = raw_input()
        queryendtime = 'x'
        while not (len(queryendtime) == 4 or len(queryendtime) == 0):
            temp = u'请输入查询的结束年份（四位数，空输入表示最新的年份）/Please input the end year of query (4 digits,Empty Input for the latest year):'
            print temp.encode('gb18030')
            queryendtime = raw_input()
            today = datetime.date.today()
            if not len(queryendtime) == 4:
                queryendtime = today.strftime('%Y%m%d')[:-4]
            else:
                pass
    today = datetime.date.today()
    todaydate = today.strftime('%Y%m%d')


    querytime = querystarttime + '-' + queryendtime
    savefoldname = 'data'
    # datatypedic = {"1": u"月度数据", "2": u"季度数据",
    #               "3": u"分省月度数据", "4": u"分省季度数据", "5": u"主要城市月度价格"}
    datatypedic = {"1": u"monthly", "2": u"seasonly",
                   "3": u"promonthly", "4": u"proseasonly", "5": u"maincity", "6": u"yearly", "7": u"proyearly", "8": u"maincityyear"}
    filename = datatypedic[querytype] + '--' + \
        querytime + '--' + todaydate + '.csv'
    dbcodenames = 'hgjd'
    if(querytype == '1'):  # 'hgyd'-->月度
        dbcodenames = 'hgyd'
        savefoldname = 'Monthly'
    elif(querytype == '2'):  # 'hgjd'-->季度
        dbcodenames = 'hgjd'
        savefoldname = 'Seasonly'
    elif(querytype == '3'):  # 'fsyd'-->分省月度
        dbcodenames = 'fsyd'
        savefoldname = 'Promonthly'
    elif (querytype == '4'):  # 'fsjd'-->分省季度
        dbcodenames = 'fsjd'
        savefoldname = 'Proseasonly'
    elif (querytype == '6'):  # 'fsjd'-->分省季度
        dbcodenames = 'hgnd'
        savefoldname = 'yearly'
    elif (querytype == '7'):  # 'fsjd'-->分省季度
        dbcodenames = 'fsnd'
        savefoldname = 'proyearly'
    elif (querytype == '8'):  # 'fsjd'-->分省季度
        dbcodenames = 'csnd'
        savefoldname = 'maincityyear'
    else:  # 'hgnd'--》年度
        dbcodenames = 'csyd'
        savefoldname = 'Maincity'


    '''
    querytime = '2016-2016'
    filename = querytime + '.csv'
    #savefoldname = 'Monthly'
    dbcodenames = 'hgjd'


    tree = TreeNode(iid='zb', name='zb', data_me=None, dbcodename=dbcodenames)
    tree.get_recur()
    with open('tree', 'wb') as f:
        pickle.dump(tree, f)
     '''





    with open('tree', 'rb') as f:
        tree = pickle.load(f)

    if not os.path.isdir('temp'):
        os.mkdir('temp')
    downloader = Downloader(tree, raw_root='temp',
                            date=querytime, dbcodename=dbcodenames)
    downloader.download()
    with open('tree', 'rb') as f:
        tree = pickle.load(f)

    doc = Document(raw_root='temp', dbcodename=dbcodenames)
    doc.to_file_all(tree, filename=filename, encoding='utf-8')

    print '''Finished!'''
    deletefolder=''
    while not (len(deletefolder) == 1):
        temp = u'\n\n是否删除临时数据文件夹temp？(y/n)'
        print temp.encode('gb18030')
        deletefolder = raw_input()
    path=os.getcwd()
    pathdlit=path+'\\'+'temp'
    if deletefolder=='y':
        shutil.rmtree(pathdlit)
    else:
        pass
    deletefile = ''
    while not (len(deletefile) == 1):
        temp = u'\n\n是否删除临时数据文件%s？(y/n)'%(filename)
        print temp.encode('gb18030')
        deletefile = raw_input()
    if deletefile == 'y':
        os.remove(filename)
    else:
        raw_input()