import os
from django.shortcuts import render
import json


def index(request):
    text = request.POST.get("text", "")
    result = ''
    if text != '':
        command = "echo {} | python3.7 stemmer.py 2>&1".format(text.replace(";", "").replace("\r", "").replace("\n", " "))
        result = json.loads(os.popen(command).read())

    return render(request, "index.html", {"result": result, "text": text})
