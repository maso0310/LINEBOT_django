from django.shortcuts import render

# Create your views here.
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage

from .models import *

import random, string, os

# 啟動 LINE BOT API 的驗證
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
# 收到 webhook 的時候進行來源驗證
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)


@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            if isinstance(event, MessageEvent):
                if event.message.type=='text':
                    mtext=event.message.text
                    uid=event.source.user_id
                    profile=line_bot_api.get_profile(uid)
                    name=profile.display_name
                    pic_url=profile.picture_url

                    message=[]
                    if User_Info.objects.filter(uid=uid).exists()==False:
                        User_Info.objects.create(uid=uid,name=name,pic_url=pic_url,mtext=mtext)
                        message.append(TextSendMessage(text='會員資料新增完畢'))
                    elif User_Info.objects.filter(uid=uid).exists()==True:
                        message.append(TextSendMessage(text='已經有建立會員資料囉'))
                        user_info = User_Info.objects.filter(uid=uid)
                        for user in user_info:
                            info = 'UID=%s\nNAME=%s\n大頭貼=%s'%(user.uid,user.name,user.pic_url)
                            message.append(TextSendMessage(text=info))
                    line_bot_api.reply_message(event.reply_token,message)

                elif event.message.type=='image':
                    image_name = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(4))
                    image_content = line_bot_api.get_message_content(event.message.id)
                    image_name = image_name.upper()+'.jpg'
                    print(os.getcwd())
                    print(__file__)
                    print(os.path.abspath(__file__))
                    path='/GISlab/static/'+image_name
                    with open(path, 'wb') as fd:
                        for chunk in image_content.iter_content():
                            fd.write(chunk)
                    domain_name = 'https://linebot-dj.onrender.com'
                    message=[]
                    message.append(ImageSendMessage(original_content_url=domain_name + path[2:],preview_image_url=domain_name + path[1:]))
                    line_bot_api.reply_message(event.reply_token,message)

        return HttpResponse()
    else:
        return HttpResponseBadRequest()