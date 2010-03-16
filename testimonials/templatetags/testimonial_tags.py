"""Tags and filters used with the testimony app."""
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
from django import template
from django.utils import translation
from satchmo_utils import url_join
from satchmo_utils.templatetags import get_filter_args
from testimonials import models
import logging

log = logging.getLogger("testimonial_tags")

register = template.Library()

class TestimonyGroupNode(template.Node):
    """Template Node tag which pushes the TestimonialGroup into the context"""
    def __init__(self, varname, key):
        self.varname = template.Variable(varname)
        self.raw_varname = varname
        self.key = template.Variable(key)
        self.raw_key = key

    def render(self, context):
        try:
            varname = self.varname.resolve(context)
        except template.VariableDoesNotExist:
            varname = self.raw_varname
            
        try:
            key = self.key.resolve(context)
        except template.VariableDoesNotExist:
            key = self.raw_key
            
        TestimonialGroup = models.TestimonyGroup.objects.by_key(key)
        if not TestimonialGroup:
            log.warn("No such TestimonialGroup: %s", key)
            
        context[varname] = TestimonialGroup

        return ""
            
@register.tag 
def TestimonyGroup(parser, token):
    """Push the TestimonyGroup into the context using the given variable name.

    Sample usage::

        {% TestimonialGroup key as ads %}
        {% for tg.random_testimonies as testimony %}
        {{ testimony }}
        {% endfor %}

    """
    args = token.split_contents()
    if not len(args) == 4:
        raise template.TemplateSyntaxError("%r tag expecting 'TestimonialGroup key as varname', got: %s" % (args[0], args))

    key, dummy, var = args[1:]
    return TestimonyGroupNode(var, key)

class TestimonyListNode(template.Node):
    """Template Node tag which pushes the TestimonialList into the context"""
    
    def __init__(self, varname):
        self.varname = template.Variable(varname)
        self.raw_varname = varname

    def render(self, context):
        try:
            varname = self.varname.resolve(context)
        except template.VariableDoesNotExist:
            varname = self.raw_varname

        context[varname] = models.Testimony.objects.all()

        return ""

@register.tag 
def TestimonyList(parser, token):
    """Push the testimonies into the context using the given variable name.

    Sample usage::

        {% TestimonyList as ads %}

    """
    args = token.split_contents()
    if not len(args) == 3:
        raise template.TemplateSyntaxError("%r tag expecting 'TestimonyList as varname', got: %s" % (args[0], args))

    dummy, var = args[1:]
    return TestimonyListNode(var)

@register.filter
def random_testimonials(tg, args):
    args, kwargs = get_filter_args(args, intargs=('length',))
    ct = kwargs.get('length', 4)
    if tg:
        return tg.random_testimonies(ct)
    else:
        return []
        
@register.inclusion_tag('testimonials/_testimony.html', takes_context=False)
def random_testimonial(group):
    """Show one testimony for the passed group name."""
    log.debug('random_testimonial')
    tgroup = models.TestimonyGroup.objects.by_key(group)
    if not tgroup:
        log.warn("No such TestimonialGroup: %s", group)
    
    testimony = None
    if tgroup:
        testimonies = tgroup.random_testimonies(1)
        if len(testimonies) > 0:
            testimony = testimonies[0]
    
    return {
        'testimony' : testimony
    }

@register.inclusion_tag('testimonials/_testimony.html', takes_context=False)
def show_testimonial(testimony):
    """Render one testimonial"""
    return {
        'testimony' : testimony
    }
