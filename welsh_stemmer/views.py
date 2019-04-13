import os
from django.shortcuts import render


def index(request):
    text = request.POST.get("text", "")
    result = ''
    if text != '':
        command = "echo {} | python CyTag/CyTag.py 2>&1".format(text)
        result = os.popen(command).read()

    return render(request, "index.html", {"result": result})
