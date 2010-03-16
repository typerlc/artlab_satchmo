"""Admin configuration for testimonials."""
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

from testimonials.models import TestimonyGroup, Testimony, TestimonyTranslation
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from l10n.l10n_settings import get_l10n_setting

class TestimonyGroupOptions(admin.ModelAdmin):
    list_filter = ('site',)
    search_fieldsets = ('key',)    

class TestimonyTranslation_Inline(admin.TabularInline): 
    model = TestimonyTranslation 
    extra = 1    

class TestimonyOptions(admin.ModelAdmin):
    list_display = ('user', 'status', 'excerpt')
    inlines=[]
    if get_l10n_setting('show_translations'):
        inlines.append(TestimonyTranslation_Inline)

admin.site.register(TestimonyGroup, TestimonyGroupOptions)
admin.site.register(Testimony, TestimonyOptions)

