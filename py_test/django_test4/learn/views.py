#-*- coding:utf-8 -*-
from django.shortcuts import render

# Create your views here.
def home(request):
    info_dict = {"site":u"自强学堂", "content":u"各种IT技术教程"}
    test_list = map(str, range(10))
    return render(request, "learn/home.html", {"info_dict":info_dict, "tst_list":test_list})