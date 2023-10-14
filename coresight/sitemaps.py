from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from posts.models import Post, ReadPost
from databanks.models import DataBank
from events.models import Event

 
class PostSitemap(Sitemap):    
    changefreq = "always"
    priority = 0.9
 
    def items(self):
        return Post.objects.filter(status=Post.PUBLISHED)
 
class DataBankSitemap(Sitemap):    
    changefreq = "always"
    priority = 0.9
 
    def items(self):
        return DataBank.objects.filter(status=DataBank.PUBLISHED)
 
class EventSitemap(Sitemap):    
    changefreq = "always"
    priority = 0.9
 
    def items(self):
        return Event.objects.filter(status=Event.PUBLISHED)
 

class StaticSitemap(Sitemap):
   priority = 0.6

   def items(self):
        return ['post-list','category-list','theme-list','content_editor','all_researches','sector_list']

   def location(self, item):
        return reverse(item)


coresight_sitemap = {
	'posts': PostSitemap, 
	'databanks': DataBankSitemap, 
	'events': EventSitemap, 
	'static': StaticSitemap,
	}
