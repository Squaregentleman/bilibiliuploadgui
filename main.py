import tkinter as tk
import time
import threading
from tkinter import ttk
from tkinter.messagebox import showerror, showinfo, askyesno
import configparser
from bilibiliuploader.bilibiliuploader import BilibiliUploader
from bilibiliuploader.core import VideoPart
import hashlib
import requests
import os
import datetime

# file_dir = ''

def getConfig(section, key):
    config = configparser.ConfigParser()
    config.read('./Uploader.conf', 'utf-8')
    return config.get(section, key)

file_dir = getConfig('Common', 'Path')

def calc_sign(param):
    salt = "60698ba2f68e01ce44738920a0ffe768"
    sign_hash = hashlib.md5()
    sign_hash.update(f"{param}{salt}".encode())
    return sign_hash.hexdigest()


def days(str1, str2=time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())):
    date1 = datetime.datetime.strptime(str1, "%Y-%m-%d %H-%M-%S")
    date2 = datetime.datetime.strptime(str2, "%Y-%m-%d %H-%M-%S")
    num = (date2 - date1).days
    return num


class Window:
    def __init__(self, startwindow):
        self.uploader = BilibiliUploader()
        self.cicklog = False
        self.startwindow = startwindow
        self.startwindow.title('哔哩哔哩直播录像上传')
        self.startwindow.resizable(width=False, height=False)
        screenwidth = self.startwindow.winfo_screenwidth()
        screenheight = self.startwindow.winfo_screenheight()
        size = '%dx%d+%d+%d' % (1022, 440, (screenwidth - 1022) / 2, (screenheight - 440) / 2)
        self.startwindow.geometry(size)

        self.Label1_title = tk.StringVar()
        self.Label1_title.set('bilibili账号')
        self.Label1 = ttk.Label(self.startwindow, textvariable=self.Label1_title, anchor=tk.W)
        self.Label1.place(x=669, y=22, width=72, height=20)

        self.Label2_title = tk.StringVar()
        self.Label2_title.set('bilibili密码')
        self.Label2 = ttk.Label(self.startwindow, textvariable=self.Label2_title, anchor=tk.W)
        self.Label2.place(x=669, y=57, width=72, height=20)

        self.Label3_title = tk.StringVar()
        self.Label3_title.set('使用模板')
        self.Label3 = ttk.Label(self.startwindow, textvariable=self.Label3_title, anchor=tk.W)
        self.Label3.place(x=664, y=136, width=72, height=20)

        self.Label4_title = tk.StringVar()
        self.Label4_title.set('标题')
        self.Label4 = ttk.Label(self.startwindow, textvariable=self.Label4_title, anchor=tk.W)
        self.Label4.place(x=664, y=162, width=72, height=20)

        self.Label5_title = tk.StringVar()
        self.Label5_title.set('标签')
        self.Label5 = ttk.Label(self.startwindow, textvariable=self.Label5_title, anchor=tk.W)
        self.Label5.place(x=666, y=187, width=72, height=20)

        self.Label6_title = tk.StringVar()
        self.Label6_title.set('简介')
        self.Label6 = ttk.Label(self.startwindow, textvariable=self.Label6_title, anchor=tk.W)
        self.Label6.place(x=669, y=220, width=32, height=32)

        self.Label7_title = tk.StringVar()
        self.Label7_title.set('{N} 年\n{Y} 月\n{D} 日')
        self.Label7 = ttk.Label(self.startwindow, textvariable=self.Label7_title, anchor=tk.NW)
        self.Label7.place(x=844, y=9, width=160, height=414)

        self.text1_text = tk.StringVar()
        self.text1_text.set(getConfig('Bilibili', 'username'))
        self.text1 = ttk.Entry(self.startwindow, textvariable=self.text1_text, justify=tk.LEFT)
        self.text1.place(x=732, y=21, width=101, height=21)

        self.text2_text = tk.StringVar()
        self.text2_text.set(getConfig('Bilibili', 'password'))
        self.text2 = ttk.Entry(self.startwindow, textvariable=self.text2_text, show='*', justify=tk.LEFT)
        self.text2.place(x=731, y=58, width=103, height=21)

        self.text3_text = tk.StringVar()
        self.text3_text.set('')
        self.text3 = ttk.Entry(self.startwindow, textvariable=self.text3_text, justify=tk.LEFT)
        self.text3.place(x=728, y=162, width=105, height=21)

        self.text4_text = tk.StringVar()
        self.text4_text.set('')
        self.text4 = ttk.Entry(self.startwindow, textvariable=self.text4_text, justify=tk.LEFT)
        self.text4.place(x=727, y=187, width=106, height=21)

        self.text5 = tk.Text(self.startwindow, wrap=tk.NONE, font=('微软雅黑', 9))
        self.text5.insert(tk.END, '')
        self.text5.place(x=667, y=264, width=165, height=156)

        self.button1_title = tk.StringVar()
        self.button1_title.set('登录')
        self.button1 = ttk.Button(self.startwindow, textvariable=self.button1_title, command=self.button1_cick)
        self.button1.place(x=712, y=91, width=88, height=32)

        self.combo = ttk.Combobox(self.startwindow, values=(), state='readonly')
        self.combo.bind("<<ComboboxSelected>>", self.combo_cick)
        self.combo.place(x=727, y=136, width=103, height=20)

        self.form = ttk.Treeview(self.startwindow, show='headings', columns=('距离今天', '日期', '文件列表'))
        self.form.column('距离今天', width=50, anchor='center')
        self.form.column('日期', width=50, anchor='center')
        self.form.column('文件列表', width=470, anchor='w')
        self.form.heading('距离今天', text='距离今天', anchor='center')
        self.form.heading('日期', text='日期', anchor='center')
        self.form.heading('文件列表', text='文件列表', anchor='w')
        self.form.bind('<Double-Button-1>', self.form_cick)
        self.form.place(x=9, y=7, width=647, height=415)
        list = os.listdir(file_dir)
        file_list = {}
        file_list_info = {}
        for i in range(0, len(list)):
            path = os.path.join(file_dir, list[i])
            if os.path.isfile(path):
                if '.' + list[i].split('.')[-1] in getConfig('Common', 'type').split(','):
                    if file_list.get(str(days(list[i].split('.')[0])), None) == None:
                        file_list.setdefault(str(days(list[i].split('.')[0])), [])
                    file_list[str(days(list[i].split('.')[0]))].append(list[i].split('.')[0])
                    file_list_info.setdefault(list[i].split('.')[0], path)
        file_list = dict(sorted(file_list.items(), key=lambda x: x[0]))
        self.file_list = file_list_info
        n = 0
        for line in file_list:
            tmp = ''
            i = 0
            for lin in file_list[line]:
                if i != len(file_list[line]) - 1:
                    tmp += file_list_info[lin].split('\\')[-1] + ','
                else:
                    tmp += file_list_info[lin].split('\\')[-1]
                i += 1
            self.form.insert("", n, values=(line, file_list[line][0].split(' ')[0], tmp))
            n += 1

    def button1_cick(self):
        threading.Thread(target=self.button1_cick_thread).start()

    def button1_cick_thread(self):
        time.sleep(0.25)
        if self.cicklog == False:
            self.cicklog = True
            time.sleep(0.2)
            self.cicklog = False
            try:
                self.uploader.login(self.text1.get(), self.text2.get())
            except:
                showerror(title='错误', message='登录失败')
            else:
                showinfo(title='成功', message='登录成功')
                cookies = {
                    'DedeUserID': str(self.uploader.mid)
                }
                session = requests.session()
                param = f"access_key={self.uploader.access_token}&appkey=bca7e84c2d947ac6&gourl=https%3A%2F%2Faccount.bilibili.com%2Faccount%2Fhome&ts={int(time.time())}"
                url = f"https://passport.bilibili.com/api/login/sso?{param}&sign={calc_sign(param)}"
                session.get(url=url, cookies=cookies)
                cookies = requests.utils.dict_from_cookiejar(session.cookies)
                head = {
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36 Edg/86.0.622.51'
                }
                self.temp = requests.get(url='https://member.bilibili.com/x/web/tpls', headers=head,
                                         cookies=cookies).json()
                tup = []
                for line in self.temp['data']:
                    tup.append(line['name'])
                self.combo["values"] = tuple(tup)
                self.combo.current(0)
                self.text3.delete(0, tk.END)
                self.text3.insert(0, self.temp['data'][0]['title'])
                self.text4.delete(0, tk.END)
                self.text4.insert(0, self.temp['data'][0]['tags'])
                self.text5.delete(0.0, tk.END)
                self.text5.insert(0.0, self.temp['data'][0]['description'])
        else:
            self.cicklog = False

    def combo_cick(self, event):
        self.text3.delete(0, tk.END)
        self.text3.insert(0, self.temp['data'][self.combo.current()]['title'])
        self.text4.delete(0, tk.END)
        self.text4.insert(0, self.temp['data'][self.combo.current()]['tags'])
        self.text5.delete(0.0, tk.END)
        self.text5.insert(0.0, self.temp['data'][self.combo.current()]['description'])

    def form_cick(self, event):
        if self.cicklog == True:
            self.cicklog = False
        else:
            self.cicklog = True
            time.sleep(0.18)
            self.cicklog = False
            threading.Thread(target=self.form_cick_thread).start()

    def form_cick_thread(self):
        self.cicklog = True
        curItem = self.form.focus()
        video = self.form.item(curItem)

        if video['values'] != '' and askyesno('提示', '是否要上传 ' + video['values'][1] + ' 的直播录像?'):
            parts = []
            print(self.text5.get(0.0, tk.END))
            for line in video['values'][2].replace(getConfig('Common', 'type'), '').split(','):
                parts.append(VideoPart(
                    path=self.file_list[line],
                    title=line,
                    desc=self.text5.get(0.0, tk.END).format(N=str(datetime.datetime.now().year), Y=str(datetime.datetime.now().month), D=str(datetime.datetime.now().day))
                ))
            print(parts)

            # 上传
            av, bv = self.uploader.upload(
                parts=parts,
                copyright=1,
                title=self.text3.get().format(N=str(datetime.datetime.now().year), Y=str(datetime.datetime.now().month), D=str(datetime.datetime.now().day)),
                tid=17,
                tag=self.text4.get(),
                desc=self.text5.get(0.0, tk.END).format(N=str(datetime.datetime.now().year), Y=str(datetime.datetime.now().month), D=str(datetime.datetime.now().day)),
                open_elec=1,
                max_retry=20)
        else:
            x = self.form.get_children()
            for item in x:
                self.form.delete(item)
            list = os.listdir(file_dir)
            file_list = {}
            file_list_info = {}
            for i in range(0, len(list)):
                path = os.path.join(file_dir, list[i])
                if os.path.isfile(path):
                    if '.' + list[i].split('.')[-1] in getConfig('Common', 'type').split(','):
                        if file_list.get(str(days(list[i].split('.')[0])), None) == None:
                            file_list.setdefault(str(days(list[i].split('.')[0])), [])
                        file_list[str(days(list[i].split('.')[0]))].append(list[i].split('.')[0])
                        file_list_info.setdefault(list[i].split('.')[0], path)
            file_list = dict(sorted(file_list.items(), key=lambda x: x[0]))
            self.file_list = file_list_info
            n = 0
            for line in file_list:
                tmp = ''
                i = 0
                for lin in file_list[line]:
                    if i != len(file_list[line]) - 1:
                        tmp += file_list_info[lin].split('\\')[-1] + ','
                    else:
                        tmp += file_list_info[lin].split('\\')[-1]
                    i += 1
                self.form.insert("", n, values=(line, file_list[line][0].split(' ')[0], tmp))
                n += 1
        self.cicklog = False


if __name__ == '__main__':
    root = tk.Tk()
    app = Window(root)
    root.mainloop()
