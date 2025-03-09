from .models import *

def save_activity(module, sub_module, heading, activity_msg, user_id, email, icon, platform, platform_icon):

   activity = ActivityLog()

   activity.module = module

   activity.sub_module = sub_module

   activity.heading = heading

   activity.activity = activity_msg

   activity.user_id = user_id

   activity.email = email

   if icon:

      activity.icon = icon

   else:

      activity.icon = 'add.png'
   
   if platform == 0:
      activity.platform = 'Web'
   else:
      activity.platform = 'App'

   if platform_icon:

      activity.platform_icon = platform_icon

   else:

      activity.platform_icon = 'web.png'

   activity.save()