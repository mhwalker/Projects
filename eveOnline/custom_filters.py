import re
import datetime

from django import template
from django import utils

register = template.Library()

@register.filter(name="leadtime")
def prettify_leadtime(amt, cutoff=14):
    if amt <= 0:
        return utils.safestring.mark_safe('<font color="green">In Stock</font>')

    if amt <= 14:
        t = "%d days" % (amt,)
    else:
        t = "%d weeks" % (round(amt/7.0),)
    if amt <= cutoff:
        return t

    return utils.safestring.mark_safe('<font color="red">%s</font>' % (t,))

@register.filter(name="commas")
def commafy_number(amt, decimal=2):
    if amt is None:
        return ""
    try:
        s = ("%%.%df" % (decimal,)) % (float(amt),)
        s = re.sub(r'\.0*$', "", s)
        while True:
            s2 = re.sub(r'(\d)(\d\d\d)(?!\d)', r'\1,\2', s)
            if s2 == s: break
            s = s2
        return s
    except:
        return amt + "??"

@register.filter(name="evedate")
def covert_to_evedate(date, refdate = None):
    dstr = date.strftime("%Y.%m.%d")

    if (refdate is None) or (date.date() == refdate.date()):
        return dstr

    if date < refdate:
        return utils.safestring.mark_safe('<font color="green">%s</font>' % (dstr,))
    else:
        return utils.safestring.mark_safe('<font color="red">%s</font>' % (dstr,))

status_styles = { "Delivered": "color: green",
                  "Cancelled": "color: red",
                  }

@register.filter(name="statuscolor")
def colorize_status_string(s):
    if s in status_styles:
        return utils.safestring.mark_safe('<span style="%s">%s</span>' % (status_styles[s], s))
    else:
        return s

@register.filter(name="get_range")
def get_range(value):
    return range(value)

@register.filter(name="markup_pct")
def calc_markup_pct(price, cost = None):
    if not cost:
        return "N/A"

    pct = round((price - cost) / cost * 100)
    pct_str = "%d%%" % (pct,)

    if pct < 0:
        color = "red"
    else:
        if pct > 20:
            color = "green"
        else:
            color = "yellow"

    return utils.safestring.mark_safe('<span style="color: %s">%s</span>' %
                                      (color, pct_str))
