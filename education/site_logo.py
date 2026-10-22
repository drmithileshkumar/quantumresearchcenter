"""The site logo, shared by scripts/build.py and every course build in education/."""


def site_logo(cls, href):
    # Wordmark lockup: the favicon's interference bars beside "Quantum" set in the logo face.
    bars=''.join(f'<rect x="{x}" y="{50-h/2:g}" width="{w}" height="{h}" rx="{w/2:g}"{a}/>' for x,w,h,a in
        ((10,2.4,18,' opacity=".35"'),(19.5,4,30,' opacity=".6"'),(31,6.5,44,''),(45,10,60,' class="logo-peak"'),(62.5,6.5,44,''),(76.5,4,30,' opacity=".6"'),(87.6,2.4,18,' opacity=".35"')))
    return (f'<a class="site-logo {cls}" href="{href}"><svg class="logo-mark" viewBox="0 0 100 100" aria-hidden="true" focusable="false">{bars}</svg>'
        '<span class="logo-word"><span class="logo-name">Quantum</span> <span class="logo-sub">Research Center</span></span></a>')


# Course pages live in education/<course>/, two levels below the site root.
COURSE_LOGO = site_logo('course-logo', '../../index.html')
