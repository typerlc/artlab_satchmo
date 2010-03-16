# -*- coding: utf-8 -*-
"""Testimonial app model"""
"""
:Authors:
    - Bruce Kroeze

New BSD License
===============
Copyright (c) 2008, Bruce Kroeze http://solidsitesolutions.com

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.
    * Neither the name of SolidSiteSolutions LLC, Zefamily LLC nor the names of its 
      contributors may be used to endorse or promote products derived from this 
      software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import get_language, gettext_lazy as _
import keyedcache
from keyedcache.models import CachedObjectMixin, find_by_key, find_by_id
from product.models import Product
import types
import random
import logging

log = logging.getLogger("testimonials.models")

STATUS_CHOICES=(('OFF',_('Disabled')),
                ('ON',_('Enabled')),
                ('NEW',_('New for approval')),
                )

class TestimonyGroupManager(models.Manager):
    def by_key(self, key):
        return find_by_key(TestimonyGroup, 'TestimonyGroup', key)

class TestimonyGroup(models.Model, CachedObjectMixin):
    """A group of Testimony objects."""

    key = models.SlugField(_('key'), max_length=50, blank=False, primary_key=True,
        help_text=_("The Keyword for this testimony group.  This can only be letters numbers and underscores.  Example: maingroup."))
    title = models.CharField(_('title'), max_length=100, blank=False)
    enabled = models.BooleanField(_('Enabled'), default=True)
    site = models.ForeignKey(Site)
    
    objects = TestimonyGroupManager()
    
    def get_testimony(self, id):
        try:
            ids = self.cache_get('testimonies')
            if id in ids:
                return Testimony.objects.by_id(id)
        except keyedcache.NotCachedError, e:
            testimonies = self.testimonies.all()
            ids = []
            for testimony in testimonies:
                keys.append(testimony.id)
                if testimony.id == id:
                    hit = spot
            keyedcache.cache_set(e.key, value=keys)
            if hit:
                return hit
            else:
                raise KeyError(id)
    
    def __len__(self):
        try:
            ids = self.cache_get('testimonies')
            return len(ids)
        except keyedcache.NotCachedError, e:
            return self.testimonies.count()
            
            
    def random_ids(self, count):
        """Build a random set."""
        
        try:
            weighted = self.cache_get('weighted')
        except keyedcache.NotCachedError, e:
            # build the weighted set
            weighted = []
            for testimony in self.testimonies.filter(status__exact="ON"):
                id = testimony.id
                weight = testimony.weight
                
                for i in range(0, weight):
                    weighted.append(id)
                
            keyedcache.cache_set(e.key, value=weighted)
            
        work = []
        random.shuffle(weighted)
        i = 0
        while len(work) < count and i<len(weighted):
            k = weighted[i]
            if k not in work:
                work.append(k)
            i+=1
                
        if len(work) < count:
            log.warn('Could not get the requested number of ads in adgroup %s.  Asked for %i, only had %i', self.key, count, len(work))
    
        return work
    
    def random_testimonies(self, count=1):
        return [Testimony.objects.by_id(k) for k in self.random_ids(count)]
        
    def __unicode__(self):
        return self.title
            
    def save(self, force_insert=False, force_update=False):
        self.cache_delete()
        super(TestimonyGroup, self).save(force_insert=force_insert, force_update=force_update)
        self.cache_set()
        return self
                
    class Meta:
        verbose_name = _('Testimony Group')
        verbose_name_plural = _('Testimony Groups')
        ordering = ('key',)
                    
class TestimonyManager(models.Manager):
    def by_id(self, id):
        """Retrieve by ID"""
        return find_by_id(Testimony, 'Testimony', id)

class Testimony(models.Model, CachedObjectMixin):
    """A Testimony."""

    group = models.ForeignKey(TestimonyGroup, null=False, blank=False, related_name='testimonies')
    
    name = models.CharField(_('name'), max_length=100, blank=False,
        help_text=_("The name of the person doing the testifying"))

    user = models.ForeignKey(User, null=True, blank=True, help_text=_("(Optional) User who gave this testimony"))

    from_url = models.URLField(_('From URL'), blank=True, null=True,
        help_text=_("(Optional) URL of person doing the testifying"))

    from_product = models.ForeignKey(Product, null=False, blank=False, related_name='testimonies',
        help_text=_("The product being testified about."))
        
    #target_url = models.URLField(_('Target URL'), blank=True, null=True,
    #    help_text=_("(Optional) URL of what is being testified about"))
        
    statement = models.TextField(_('Statement'), blank=False, null=False,
        help_text=_("The testimony given."))
        
    weight = models.IntegerField(_('Weight'), default=10,
        help_text=_("How much weight to give this testimony in random display.  Ex: 20 = 2 times as often as the default weight of 10"))
        
    status = models.CharField(_('Status'), choices=STATUS_CHOICES, max_length=3, null=False, default="NEW")
        
    date_added = models.DateField(_("Date added"), null=True, blank=True)
            
    objects = TestimonyManager()
            
    def save(self, force_insert=False, force_update=False):
        log.debug("Saving: %s", self)
        if not self.pk:
            self.date_added = datetime.today()
        
        try:
            self.group.cache_delete()
        except:
            pass
        self.cache_delete()
        super(Testimony, self).save(force_insert=force_insert, force_update=force_update)
        self.cache_set()
        log.debug("Saved: %s", self)
        return self
        
    @property
    def excerpt(self):
        return self.statement[:20]
        
    def __unicode__(self):
        return self.name + " " + self.excerpt
        
    class Meta:
        verbose_name = _('Testimony')
        verbose_name_plural = _('Testimonies')

        
class TestimonyTranslation(models.Model):
    """A specific language translation for a `Testimony`.  This is intended for all descriptions which are not the
    default settings.LANGUAGE.
    """
    testimony = models.ForeignKey('Testimony', related_name="translations")
    languagecode = models.CharField(_('language'), max_length=10, choices=settings.LANGUAGES)
    name = models.CharField(_('name'), max_length=100, blank=False,
        help_text=_("The name of the person doing the testifying"))
    statement = models.TextField(_('Statement'), blank=True,
        help_text=_("The testimony given."))

    class Meta:
        verbose_name = _('Testimonial Translation')
        verbose_name_plural = _('Testimonial Translations')
        ordering = ('testimony', 'name', 'languagecode')
        unique_together = ('testimony', 'languagecode')

    def __unicode__(self):
        return u"TestimonyTranslation: [%s] %s: %s" % (self.languagecode, self.name, self.statement)


